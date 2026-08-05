from py_canoe.canoe import CANoe as CANoe
from py_canoe.helpers.bus_type import BusType as BusType
from py_canoe.helpers.common import wait as wait
from py_canoe.helpers.exceptions import PyCanoeError as PyCanoeError
from py_canoe.helpers.exceptions import ConfigurationNotLoadedError as ConfigurationNotLoadedError
from py_canoe.helpers.vxlapi import ChannelInfo as ChannelInfo
from py_canoe.helpers.vxlapi import XlBusType as XlBusType


sample_py_canoe_script = '''
from py_canoe import CANoe

canoe_obj = CANoe()
canoe_obj.open(r"path\\to\\your.cfg")
canoe_obj.start_measurement()

# write your logic here

canoe_obj.stop_measurement()
canoe_obj.quit()
'''


def main():
    import argparse
    import platform
    from importlib.metadata import version, PackageNotFoundError

    try:
        v = version("py-canoe")
    except PackageNotFoundError:
        v = "unknown"

    parser = argparse.ArgumentParser(prog="py-canoe")
    parser.add_argument("--version", action="version", version=f"py-canoe {v}")
    parser.add_argument("--info", action="store_true", help="show environment and diagnostic info")
    parser.add_argument("--check", action="store_true", help="check CANoe installation and COM availability")
    parser.add_argument("--init", metavar="PATH", help="create a starter py-canoe script at PATH")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress non-essential output")
    args = parser.parse_args()

    if args.info:
        print(f"py-canoe {v}")
        print(f"Python {platform.python_version()} ({platform.architecture()[0]})")
        print(f"Platform: {platform.platform()}")
        return

    if args.check:
        try:
            import win32com.client
            win32com.client.Dispatch("CANoe.Application")
            print("CANoe COM interface: OK")
        except Exception as e:
            print(f"CANoe COM interface: FAILED ({e})")
        return

    if args.init:
        file_path = fr"{args.init}\starter_py_canoe_script.py"
        with open(file_path, "w") as f:
            f.write(sample_py_canoe_script)
        print(f"Created starter script: {file_path}")
        return

    if not args.quiet:
        print(f"py-canoe {v} — paddling through CANoe, one test at a time.")
        print("Run `py-canoe --help` to see available options.\n")
