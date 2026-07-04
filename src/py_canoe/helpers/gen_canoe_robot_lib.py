"""Generate a generic Robot Framework Python library wrapper.

This script introspects a source class and writes a thin wrapper
library class to the configured target file.
"""

import argparse
import ast
import datetime
import logging
import py_compile
from importlib.metadata import version as _dist_version, PackageNotFoundError
from datetime import timezone
from pathlib import Path



class RobotLibraryGenerator:
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [py_canoe.helpers.gen_canoe_robot_lib] %(levelname)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    def __init__(
        self,
        source_path: Path,
        source_import: str,
        source_class_name: str,
        target_path: Path,
        wrapper_class_name: str | None = None,
        method_prefix: str = "",
    ) -> None:
        self.source_path = Path(source_path)
        self.source_import = source_import
        self.source_class_name = source_class_name
        self.target_path = Path(target_path)
        self.wrapper_class_name = wrapper_class_name or f"{source_class_name}RobotLib"
        self.method_prefix = method_prefix

    def _python_name_to_robot_method(self, name: str) -> str:
        return self.method_prefix + name

    @classmethod
    def _format_node(cls, node: ast.AST) -> str:
        if hasattr(ast, "unparse"):
            return ast.unparse(node)
        if isinstance(node, ast.Constant):
            return repr(node.value)
        return ast.dump(node)

    @classmethod
    def _collect_annotation_names(cls, node: ast.AST) -> set[str]:
        names: set[str] = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                names.add(child.id)
            elif isinstance(child, ast.Attribute):
                parts = []
                current = child
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                dotted = ".".join(reversed(parts))
                names.add(dotted)
                for i in range(1, len(parts)):
                    names.add(".".join(reversed(parts[:i])))
            elif isinstance(child, ast.Constant) and isinstance(child.value, str):
                try:
                    expr = ast.parse(child.value, mode="eval")
                except SyntaxError:
                    continue
                names.update(cls._collect_annotation_names(expr))

        return names

    @staticmethod
    def _is_type_checking_if(node: ast.If) -> bool:
        return isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"

    @staticmethod
    def _get_imported_names(stmt: ast.stmt) -> set[str]:
        imported_names: set[str] = set()
        if isinstance(stmt, ast.Import):
            for alias in stmt.names:
                imported_names.add(alias.asname or alias.name)
                imported_names.add(alias.name)
                imported_names.add(alias.name.split(".")[0])
        elif isinstance(stmt, ast.ImportFrom):
            module_name = stmt.module or ""
            for alias in stmt.names:
                imported_names.add(alias.asname or alias.name)
                imported_names.add(alias.name)
                if module_name:
                    imported_names.add(f"{module_name}.{alias.name}")
        return imported_names

    @classmethod
    def _import_statement_relevant(cls, stmt: ast.stmt, annotation_names: set[str]) -> bool:
        return bool(cls._get_imported_names(stmt) & annotation_names)

    @classmethod
    def _annotation_names_for_nodes(cls, nodes: list[ast.FunctionDef]) -> set[str]:
        annotation_names: set[str] = set()
        for node in nodes:
            for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
                if arg.annotation is not None:
                    annotation_names.update(cls._collect_annotation_names(arg.annotation))
            if node.args.vararg is not None and node.args.vararg.annotation is not None:
                annotation_names.update(cls._collect_annotation_names(node.args.vararg.annotation))
            if node.args.kwarg is not None and node.args.kwarg.annotation is not None:
                annotation_names.update(cls._collect_annotation_names(node.args.kwarg.annotation))
            if node.returns is not None:
                annotation_names.update(cls._collect_annotation_names(node.returns))
        return annotation_names

    @classmethod
    def _get_preserved_import_lines(cls, module: ast.Module, nodes: list[ast.FunctionDef]) -> tuple[list[str], bool, set[str]]:
        annotation_names = cls._annotation_names_for_nodes(nodes)
        preserved_lines: list[str] = []
        has_future_annotations = False
        type_checking_block_relevant = False
        type_checking_import_line: str | None = None

        for stmt in module.body:
            if isinstance(stmt, ast.ImportFrom) and stmt.module == "__future__":
                if any(alias.name == "annotations" for alias in stmt.names):
                    preserved_lines.append(ast.unparse(stmt))
                    has_future_annotations = True
                continue

            if isinstance(stmt, ast.If) and cls._is_type_checking_if(stmt):
                relevant_children = [
                    sub
                    for sub in stmt.body
                    if isinstance(sub, (ast.Import, ast.ImportFrom)) and cls._import_statement_relevant(sub, annotation_names)
                ]
                if relevant_children:
                    preserved_lines.append(ast.unparse(stmt))
                    type_checking_block_relevant = True
                continue

            if isinstance(stmt, (ast.Import, ast.ImportFrom)) and cls._import_statement_relevant(stmt, annotation_names):
                preserved_lines.append(ast.unparse(stmt))
                continue

            if isinstance(stmt, ast.ImportFrom) and stmt.module == "typing":
                if any(alias.name == "TYPE_CHECKING" for alias in stmt.names):
                    type_checking_import_line = ast.unparse(stmt)

        if type_checking_block_relevant and type_checking_import_line is not None:
            if type_checking_import_line not in preserved_lines:
                preserved_lines.insert(0, type_checking_import_line)

        return preserved_lines, has_future_annotations, annotation_names

    def _get_source_class_from_source(self) -> tuple[ast.Module, list[tuple[str, ast.FunctionDef]], ast.FunctionDef]:
        source = self.source_path.read_text(encoding="utf-8")
        module = ast.parse(source)

        source_class = next(
            (node for node in module.body if isinstance(node, ast.ClassDef) and node.name == self.source_class_name),
            None,
        )
        if source_class is None:
            raise RuntimeError(f"Could not find {self.source_class_name} class definition in {self.source_path}")

        methods: list[tuple[str, ast.FunctionDef]] = []
        init_method = None
        for item in source_class.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "__init__":
                    init_method = item
                elif not item.name.startswith("_"):
                    methods.append((item.name, item))

        if init_method is None:
            raise RuntimeError(f"{self.source_class_name}.__init__ not found in {self.source_path}")

        return module, methods, init_method

    @classmethod
    def _build_method_signature_from_ast(cls, node: ast.FunctionDef) -> tuple[str, str, str | None]:
        parameters: list[str] = []
        call_args: list[str] = []

        def add_param(arg: ast.arg, default: ast.expr | None = None, prefix: str = "") -> None:
            annotation = f": {cls._format_node(arg.annotation)}" if arg.annotation is not None else ""
            if default is None:
                parameters.append(f"{prefix}{arg.arg}{annotation}")
            else:
                parameters.append(f"{prefix}{arg.arg}{annotation}={cls._format_node(default)}")
            call_args.append(arg.arg)

        pos_defaults = [None] * (len(node.args.posonlyargs) - len(node.args.defaults)) + node.args.defaults[: len(node.args.posonlyargs)]
        for arg, default in zip(node.args.posonlyargs, pos_defaults):
            if arg.arg != "self":
                add_param(arg, default)

        arg_defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + node.args.defaults[len(node.args.posonlyargs) :]
        for arg, default in zip(node.args.args, arg_defaults):
            if arg.arg != "self":
                add_param(arg, default)

        if node.args.vararg is not None:
            annotation = f": {cls._format_node(node.args.vararg.annotation)}" if node.args.vararg.annotation is not None else ""
            parameters.append(f"*{node.args.vararg.arg}{annotation}")
            call_args.append(f"*{node.args.vararg.arg}")

        if node.args.kwonlyargs:
            if not node.args.vararg:
                parameters.append("*")
            for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                add_param(arg, default)

        if node.args.kwarg is not None:
            annotation = f": {cls._format_node(node.args.kwarg.annotation)}" if node.args.kwarg.annotation is not None else ""
            parameters.append(f"**{node.args.kwarg.arg}{annotation}")
            call_args.append(f"**{node.args.kwarg.arg}")

        return_annotation = cls._format_node(node.returns) if node.returns is not None else None
        return ", ".join(parameters), ", ".join(call_args), return_annotation

    @staticmethod
    def _consolidate_typing_imports(lines: list[str]) -> list[str]:
        typing_names: set[str] = set()
        other_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("from typing import") and not stripped.startswith("if TYPE_CHECKING"):
                try:
                    stmt = ast.parse(stripped).body[0]
                except SyntaxError:
                    other_lines.append(line)
                    continue
                if isinstance(stmt, ast.ImportFrom) and stmt.module == "typing":
                    for alias in stmt.names:
                        typing_names.add(alias.asname or alias.name)
                    continue
            other_lines.append(line)

        if typing_names:
            other_lines.insert(0, f"from typing import {', '.join(sorted(typing_names))}")
        return other_lines

    def _write_wrapper_method(self, f, name: str, method: ast.FunctionDef) -> None:
        method_name = self._python_name_to_robot_method(name)
        signature, call_args, return_annotation = self._build_method_signature_from_ast(method)
        doc = ast.get_docstring(method) or f"Wrapper for {self.source_class_name}.{name}."
        doc_lines = doc.splitlines() if doc else [f"Wrapper for {self.source_class_name}.{name}." ]

        sig_prefix = f", {signature}" if signature else ""
        return_suffix = f" -> {return_annotation}" if return_annotation else ""

        f.write(f"    def {method_name}(self{sig_prefix}){return_suffix}:\n")
        if len(doc_lines) == 1:
            f.write(f"        \"\"\"{doc_lines[0]}\"\"\"\n")
        else:
            f.write("        \"\"\"\n")
            for line in doc_lines:
                f.write(f"        {line}\n")
            f.write("        \"\"\"\n")

        if call_args:
            f.write(f"        return self._source.{name}({call_args})\n\n")
        else:
            f.write(f"        return self._source.{name}()\n\n")

    def _write_header_and_imports(
        self,
        f,
        has_future_annotations: bool,
        preserved_imports: list[str],
        annotation_names: set[str],
    ) -> None:
        if has_future_annotations:
            f.write("from __future__ import annotations\n")

        imports = self._consolidate_typing_imports(preserved_imports)
        for line in imports:
            f.write(f"{line}\n")

        if has_future_annotations or imports:
            f.write("\n")

        if not has_future_annotations and not any(line.strip().startswith("from typing import") for line in imports):
            needed_typing = {name for name in annotation_names if name in {"Iterable", "Optional", "Any"}}
            if needed_typing:
                f.write(f"from typing import {', '.join(sorted(needed_typing))}\n")

        f.write(f"from {self.source_import} import {self.source_class_name}\n\n\n")

    def create_robot_library(self) -> None:
        library_path = self.target_path

        try:
            module, methods, init_method = self._get_source_class_from_source()
        except Exception as exc_import:
            self.logger.error(f"Failed to load {self.source_class_name} class from source for generation: {exc_import}")
            return

        preserved_imports, has_future_annotations, annotation_names = self._get_preserved_import_lines(
            module, [init_method] + [method for _, method in methods]
        )
        init_signature, init_call_args, _ = self._build_method_signature_from_ast(init_method)

        self.logger.info(
            f"Generating Robot Framework Python library '{library_path}' with {len(methods)} wrapper methods."
        )

        try:
            gen_ts = datetime.datetime.now(timezone.utc).isoformat()
            try:
                pkg_version = _dist_version("py-canoe")
            except PackageNotFoundError:
                pkg_version = "unknown"

            header = (
                "# ---------------------------------------------------------------------------\n"
                "# THIS FILE IS AUTO-GENERATED - DO NOT EDIT MANUALLY\n"
                f"# Generated: {gen_ts}\n"
                f"# py-canoe package version: {pkg_version}\n"
                "# To update this file, run the generator: python -m py_canoe.helpers.gen_canoe_robot_lib\n"
                "# ---------------------------------------------------------------------------\n\n"
            )

            with open(library_path, "w", encoding="utf-8") as f:
                f.write(header)
                self._write_header_and_imports(f, has_future_annotations, preserved_imports, annotation_names)
                f.write(f"class {self.wrapper_class_name}:\n")
                f.write(f"    \"\"\"Robot Framework library wrapper around {self.source_class_name}.\"\"\"\n\n")

                init_sig_prefix = f", {init_signature}" if init_signature else ""
                f.write(f"    def __init__(self{init_sig_prefix}):\n")
                f.write(
                    f"        self._source = {self.source_class_name}({init_call_args})\n\n"
                    if init_call_args
                    else f"        self._source = {self.source_class_name}()\n\n"
                )

                for name, method in methods:
                    self._write_wrapper_method(f, name, method)

            py_compile.compile(str(library_path), doraise=True)
            self.logger.info(f"Success! Generated '{library_path}' with {len(methods)} wrapper methods.")
            self.logger.info(f"Validated generated library '{library_path}' (syntax OK).")
        except Exception as exc:
            self.logger.error(f"Failed to generate '{library_path}': {exc}")



def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Robot Framework library wrapper around py_canoe.CANoe.")
    parser.add_argument("--source-path", default=str(Path(__file__).resolve().parent.parent / "canoe.py"), help="Source Python file containing the CANoe class.")
    parser.add_argument("--source-import", default="py_canoe.canoe", help="Python import path for the source module.")
    parser.add_argument("--source-class-name", default="CANoe", help="Source class name to wrap.")
    parser.add_argument("--target-path", default=str(Path(__file__).resolve().parent.parent / "canoe_robot_lib.py"), help="Target file path for the generated Robot library.")
    parser.add_argument("--wrapper-class-name", default="CanoeRobotLib", help="Wrapper class name to generate.")
    parser.add_argument("--method-prefix", default="canoe_", help="Prefix added to each generated wrapper method name.")
    args = parser.parse_args()

    generator = RobotLibraryGenerator(
        source_path=Path(args.source_path),
        source_import=args.source_import,
        source_class_name=args.source_class_name,
        target_path=Path(args.target_path),
        wrapper_class_name=args.wrapper_class_name,
        method_prefix=args.method_prefix,
    )
    generator.create_robot_library()


if __name__ == "__main__":
    main()
