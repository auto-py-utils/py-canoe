# [py-canoe](https://github.com/chaitu-ycr/py-canoe)

## about package

Python 🐍 Package for accessing Vector CANoe 🛶 Tool via COM Interface

> **Note:** Looking for volunteers to maintain and contribute to this project. If interested, please reach out to me on [LinkedIn](https://www.linkedin.com/in/chaitu-ycr/).

## 🔗 useful links

- [github documentation](https://chaitu-ycr.github.io/py-canoe/)
- [pypi package](https://pypi.org/project/py-canoe/)
- [github releases](https://github.com/chaitu-ycr/py-canoe/releases)
- [for ideas💡/sugessions comment under discussions **here**](https://github.com/chaitu-ycr/py-canoe/discussions)
- [create issue/request feature **here**](https://github.com/chaitu-ycr/py-canoe/issues/new/choose)
- [fork repo](https://github.com/chaitu-ycr/py-canoe/fork) and create pull request to contribute back to this project.
- [vector canoe documentation](https://help.vector.com/CANoeDEFamily/index.html)

## prerequisites

- [python(>=3.10)](https://www.python.org/downloads/)
- [vector canoe software(>=v11)](https://www.vector.com/int/en/support-downloads/download-center/)
- [visual studio code](https://code.visualstudio.com/Download)
- Windows PC(recommended windows 11 OS along with 16GB RAM)

## setup and installation

create a python virtual environment and activate it. you can use any method to create a virtual environment; here are some examples.

### standard way

```bash
# create a new directory for your project (optional)
mkdir my-project
cd my-project

# create virtual environment
python -m venv .venv

# activate virtual environment
.venv\Scripts\activate

# upgrade pip (optional but recommended)
python -m pip install --upgrade pip

# install/upgrade py-canoe package
pip install py-canoe --upgrade
```

### using astral uv

```bash
# install uv if not already installed (optional)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# create a new uv python package (optional)
uv init my-project --package
cd my-project

# create virtual environment with uv
uv venv .venv

# activate virtual environment
.venv\Scripts\activate

# install/upgrade py-canoe package
uv pip install py-canoe --upgrade

# add py-canoe as dependency to your pyproject.toml (optional)
uv add py-canoe
```

---

## example use cases

### import CANoe module and create CANoe class object

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
```

### open CANoe, start measurement, get version info, stop measurement and close canoe configuration

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo.cfg')

canoe_inst.start_measurement()
canoe_version_info = canoe_inst.get_canoe_version_info()
canoe_inst.stop_measurement()
canoe_inst.quit()
```

### restart/reset running measurement

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo.cfg')

canoe_inst.start_measurement()
canoe_inst.reset_measurement()
canoe_inst.stop_ex_measurement()
```

### open CANoe offline config and start/break/step/reset/stop measurement in offline mode

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(r'tests\demo_cfg\demo_offline.cfg')

canoe_inst.add_offline_source_log_file(r'tests\demo_cfg\Logs\demo_log.blf')
canoe_inst.start_measurement_in_animation_mode(animation_delay=200)
canoe_inst.break_measurement_in_offline_mode()
canoe_inst.step_measurement_event_in_single_step()
canoe_inst.reset_measurement_in_offline_mode()
canoe_inst.stop_measurement()
```

### get/set CANoe measurement index

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

meas_index_value = canoe_inst.get_measurement_index()
canoe_inst.start_measurement()
canoe_inst.stop_measurement()
meas_index_value = canoe_inst.get_measurement_index()
canoe_inst.set_measurement_index(meas_index_value + 1)
meas_index_new = canoe_inst.get_measurement_index()
canoe_inst.reset_measurement()
canoe_inst.stop_measurement()
```

### save CANoe config to a different version with different name

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.save_configuration_as(path=r'tests\demo_cfg\demo_v10.cfg', major=10, minor=0, create_dir=True)
```

### get CAN bus statistics of CAN channel 1

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
canoe_inst.get_can_bus_statistics(channel=1)
canoe_inst.stop_measurement()
```

### get/set bus signal value, check signal state and get signal full name

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
sig_full_name = canoe_inst.get_signal_full_name(bus='CAN', channel=1, message='LightState', signal='FlashLight')
sig_value = canoe_inst.get_signal_value(bus='CAN', channel=1, message='LightState', signal='FlashLight', raw_value=False)
canoe_inst.set_signal_value(bus='CAN', channel=1, message='LightState', signal='FlashLight', value=1, raw_value=False)
sig_online_state = canoe_inst.check_signal_online(bus='CAN', channel=1, message='LightState', signal='FlashLight')
sig_state = canoe_inst.check_signal_state(bus='CAN', channel=1, message='LightState', signal='FlashLight')
sig_val = canoe_inst.get_signal_value(bus='CAN', channel=1, message='LightState', signal='FlashLight', raw_value=True)
canoe_inst.stop_measurement()
```

### clear write window / read text from write window / control write window output file

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.enable_write_window_output_file(r'tests\demo_cfg\Logs\write_win.txt')
canoe_inst.start_measurement()
canoe_inst.clear_write_window_content()
canoe_inst.write_text_in_write_window("hello from py_canoe!")
text = canoe_inst.read_text_from_write_window()
canoe_inst.stop_measurement()
canoe_inst.disable_write_window_output_file()
```

### switch between CANoe desktops

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')
canoe_inst.ui_activate_desktop('Configuration')
```

### get/set system variable or define system variable

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
canoe_inst.set_system_variable_value('demo::level_two_1::sys_var2', 20)
canoe_inst.set_system_variable_value('demo::string_var', 'hey hello this is string variable')
canoe_inst.set_system_variable_value('demo::data_var', 'hey hello this is data variable')
canoe_inst.set_system_variable_array_values('demo::int_array_var', (00, 11, 22, 33, 44, 55, 66, 77, 88, 99))
sys_var_val = canoe_inst.get_system_variable_value('demo::level_two_1::sys_var2')
sys_var_val = canoe_inst.get_system_variable_value('demo::data_var')
canoe_inst.stop_measurement()
canoe_inst.define_system_variable('sys_demo::demo', 1)
canoe_inst.save_configuration()
canoe_inst.start_measurement()
sys_var_val = canoe_inst.get_system_variable_value('sys_demo::demo')
canoe_inst.stop_measurement()
```

### send diagnostic request, control tester present

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(r'tests\demo_cfg\demo_diag.cfg')

canoe_inst.start_measurement()
resp = canoe_inst.send_diag_request('Door', 'DefaultSession_Start', False)
canoe_inst.control_tester_present('Door', False)
wait(2)
canoe_inst.control_tester_present('Door', True)
wait(5)
resp = canoe_inst.send_diag_request('Door', '10 02')
canoe_inst.control_tester_present('Door', False)
wait(2)
resp = canoe_inst.send_diag_request('Door', '10 03', return_sender_name=True)
canoe_inst.stop_measurement()
```

### set replay block source file / control replay block start stop

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
canoe_inst.set_replay_block_file(block_name='DemoReplayBlock', recording_file_path=r'tests\demo_cfg\Logs\demo_log.blf')
canoe_inst.control_replay_block(block_name='DemoReplayBlock', start_stop=True)
wait(2)
canoe_inst.control_replay_block(block_name='DemoReplayBlock', start_stop=False)
canoe_inst.stop_measurement()
```

### compile CAPL nodes and call capl function

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.compile_all_capl_nodes()
canoe_inst.start_measurement()
canoe_inst.call_capl_function('addition_function', 100, 200)
canoe_inst.call_capl_function('hello_world')
canoe_inst.stop_measurement()
```

### execute test configuration test units

```python
from py_canoe import CANoe, wait
canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'CAN\Diagnostics\UDSSystem\UDSSystem.cfg')
canoe_inst.start_measurement()
canoe_inst.execute_all_test_configurations(wait_for_completion=True)
canoe_inst.execute_test_configuration('DiagTestConfiguration', wait_for_completion=False)
wait(5)
canoe_inst.stop_test_configuration()
canoe_inst.stop_measurement()
```

### execute test setup test module / test environment

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
canoe_inst.execute_all_test_modules_in_test_env(demo_test_environment)
canoe_inst.execute_test_module('demo_test_node_002')
canoe_inst.stop_measurement()
```

### get/set environment variable value

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
canoe_inst.set_environment_variable_value('int_var', 123.12)
canoe_inst.set_environment_variable_value('float_var', 111.123)
canoe_inst.set_environment_variable_value('string_var', 'this is string variable')
canoe_inst.set_environment_variable_value('data_var', (1, 2, 3, 4, 5, 6, 7))
var_value = canoe_inst.get_environment_variable_value('int_var')
var_value = canoe_inst.get_environment_variable_value('float_var')
var_value = canoe_inst.get_environment_variable_value('string_var')
var_value = canoe_inst.get_environment_variable_value('data_var')
canoe_inst.stop_measurement()
```

### add/remove database

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r"tests\demo_cfg\demo_conf_gen_db_setup.cfg")

canoe_inst.start_measurement()
# add database
canoe_inst.add_database(fr"{file_path}\demo_cfg\DBs\sample_databases\XCP.dbc", 'CAN1', 1)
# remove database
canoe_inst.remove_database(fr"{file_path}\demo_cfg\DBs\sample_databases\XCP.dbc", 1)
```

### start/stop online logging block

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r"tests\demo_cfg\demo_online_setup.cfg")

canoe_inst.start_measurement()
# stop logging block
canoe_inst.start_stop_online_logging_block(fr'{demo_cfg_dir}\Logs\demo_online_setup_log.blf', start_stop=False)
wait(2)
# start logging block
canoe_inst.start_stop_online_logging_block(fr'{demo_cfg_dir}\Logs\demo_online_setup_log.blf', start_stop=True)
```

### working with logging blocks

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
# remove current logging blocks
for i in range(canoe_inst.logging_collection.count):
    canoe_inst.remove_logging_block(1)  # iteration start from 1 and shifts after each delete
# add a new block
# define dest path with file format as asc, blf or other
# may include field functions like {IncMeasurement}
full_path = "C:/sample_log_{IncMeasurement}.blf"
canoe_inst.add_logging_block(full_path)
canoe_inst.start_measurement()
# ...
canoe_inst.stop_measurement()
# log should be fully generated at this point for you to analyze
canoe_inst.set_configuration_modified(False)  # to avoid popup asking to save changes
canoe_inst.quit()
```
