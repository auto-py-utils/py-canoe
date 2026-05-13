# UnicodeEncodeError due to Emojis in Log Messages on Windows

## Problem
py_canoe crashes on Windows when log messages contain emojis (📖 🧹 ❌ ✔️).
The default Windows encoding cp1252 cannot encode Unicode emoji characters,
causing a UnicodeEncodeError when the logger attempts to write to stdout.

## Error
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4d6'
Message: '📖 Text read successfully from write window'
```

## Affected Files
Files in `src/py_canoe/core/` using emojis in log messages:
- `write.py`, `bus.py`, `buses.py`, `database.py`, `databases.py`
- `simulation_setup.py`, `networks.py`, `measurement.py`
- `configuration.py`, `canoe.py`

## How to Reproduce
```python
from py_canoe import CANoe

canoe = CANoe()
canoe.open(r"path\to\config.cfg")  # triggers log message with emoji
```
Any method that logs with emoji will trigger the error on Windows
with default cp1252 encoding.

## Environment
- Windows 11, Python 3.11, default encoding cp1252
- Branch: main (commit 9fa4e4c and later)

## Workaround
Set UTF-8 mode before starting Python:
```bash
set PYTHONUTF8=1
python your_script.py
```

## Fix Options
1. **Configure logger for UTF-8:** `handler.stream.reconfigure(encoding='utf-8')`
2. **Replace emojis with ASCII:** `📖` → `[OK]`, `❌` → `[ERROR]`
3. **Use error handling in logger:** `errors='replace'` to substitute unencodable chars
