from py_canoe.core.com_session import dispatch_com_object


class SnippetSetup:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def snippet_files(self) -> 'SnippetFiles':
        return SnippetFiles(self.com_object.SnippetFiles)


class SnippetFiles:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'SnippetFile':
        return SnippetFile(self.com_object.Item(index))

    def add(self, file_name: str, full_name: str) -> 'SnippetFile':
        return SnippetFile(self.com_object.Add(file_name, full_name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class SnippetFile:
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def snippets(self) -> 'Snippets':
        return self.com_object.Snippets


class Snippets:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'Snippet':
        return Snippet(self.com_object.Item(index))


class Snippet:
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def name(self) -> str:
        return self.com_object.Name

    def is_running(self) -> bool:
        return self.com_object.IsRunning()

    def run(self):
        self.com_object.Run()
