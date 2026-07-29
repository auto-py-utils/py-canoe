# [py-canoe](https://github.com/auto-py-utils/py-canoe)

## 关于本包

Python 🐍 封装库，通过 COM 接口访问 Vector CANoe 🛶 工具

> **注意：** 正在寻找志愿者来维护和贡献本项目。如有兴趣，请通过 [LinkedIn](https://www.linkedin.com/in/chaitu-ycr/) 联系我。

## 🔗 实用链接

- [文档](https://auto-py-utils.github.io/py-canoe/)
- [PyPI 包](https://pypi.org/project/py-canoe/)
- [GitHub 发布页](https://github.com/auto-py-utils/py-canoe/releases)
- [提交问题 / 请求功能](https://github.com/auto-py-utils/py-canoe/issues/new/choose)
- [Fork 仓库](https://github.com/auto-py-utils/py-canoe/fork) 并创建 Pull Request 来贡献本项目，或在 LinkedIn 上发送你的 GitHub 用户名，我会将你添加为协作者。
- [Vector CANoe 文档](https://help.vector.com/CANoeDEFamily/index.html)

## 前提条件

- [Python (>=3.10)](https://www.python.org/downloads/)
- [Vector CANoe 软件 (>=v11)](https://www.vector.com/int/en/support-downloads/download-center/)
- [Visual Studio Code](https://code.visualstudio.com/Download)
- Windows PC（推荐 Windows 11 操作系统及 16GB 内存）

## 安装

### 标准方式

```bash
# 安装 py-canoe 包
pip install py-canoe

# 升级 py-canoe 包
pip install py-canoe --upgrade

# 安装 py-canoe 包及所有可选依赖
pip install py-canoe[all]
```

### 使用 Astral UV

```bash
# 安装 py-canoe 包
uv pip install py-canoe

# 升级 py-canoe 包
uv pip install py-canoe --upgrade

# 安装 py-canoe 包及所有可选依赖
uv pip install py-canoe[all]

# 将 py-canoe 添加为 pyproject.toml 的依赖
uv add py-canoe

# 将 py-canoe 包及所有可选依赖添加到 pyproject.toml
uv add py-canoe[all]

# 升级 pyproject.toml 中的 py-canoe 包
uv update py-canoe
```

---

## 使用示例

### 导入 CANoe 模块并创建 CANoe 类对象

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
```

### 打开 CANoe、启动测量、获取版本信息、停止测量并关闭配置

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo.cfg')

canoe_inst.start_measurement()
canoe_version_info = canoe_inst.get_canoe_version_info()
canoe_inst.stop_measurement()
canoe_inst.quit()
```

### 重启/重置正在运行的测量

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo.cfg')

canoe_inst.start_measurement()
canoe_inst.reset_measurement()
canoe_inst.stop_ex_measurement()
```

### 打开 CANoe 离线配置，在离线模式下启动/暂停/单步/重置/停止测量

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

### 获取/设置 CANoe 测量索引

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

### 将 CANoe 配置另存为不同版本和名称

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.save_configuration_as(path=r'tests\demo_cfg\demo_v10.cfg', major=10, minor=0, create_dir=True)
```

### 获取 CAN 通道 1 的总线统计数据

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
canoe_inst.get_can_bus_statistics(channel=1)
canoe_inst.stop_measurement()
```

### 获取/设置总线信号值、检查信号状态、获取信号全名

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

### 清空写入窗口 / 读取写入窗口文本 / 控制写入窗口输出文件

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

### 切换 CANoe 桌面

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')
canoe_inst.ui_activate_desktop('Configuration')
```

### 获取/设置系统变量或定义系统变量

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

### 列出系统变量命名空间和变量

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

namespace_names = canoe_inst.application.system.get_all_namespace_names()
variables = canoe_inst.application.system.get_all_variables_in_namespace('demo')
```

### 发送诊断请求、控制 Tester Present

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
wait(2)
resp = canoe_inst.send_diag_request('Door', 'Variant_Coding_Write', False, CountryType="Europe")
canoe_inst.stop_measurement()
```

### 设置回放块源文件 / 控制回放块启停

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

### 编译 CAPL 节点并检查编译结果

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

# 简单布尔检查
if canoe_inst.application.configuration.run_compilation():
    print("编译成功")

# 获取详细错误信息
result = canoe_inst.application.configuration.get_compilation_result()
if not result["success"]:
    print(f"编译失败: {result['error']}")
```

### 编译 CAPL 节点并调用 CAPL 函数

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

### 执行测试配置中的测试单元

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

### 执行测试设置中的测试模块 / 测试环境

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
canoe_inst.execute_all_test_modules_in_test_env(demo_test_environment)
canoe_inst.execute_test_module('demo_test_node_002')
canoe_inst.stop_measurement()
```

### 执行测试模块时选择性启用/禁用测试用例

`execute_test_module` 方法支持在执行前通过通配符或正则表达式模式选择性地启用或禁用测试用例。

**模式匹配规则：**
- **通配符**（默认）：使用 fnmatch 风格的模式（`*` 匹配任意字符，`?` 匹配单个字符，`[seq]` 匹配序列中的任意字符）
- **正则表达式**：以 `(?` 开头或包含正则元字符（`^`、`$`、`[`、`]`、`+`、`{`、`}`）的模式将被视为正则表达式
- **优先级**：`disable_test_cases` 优先于 `enable_test_cases`

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()

# 仅启用冒烟测试用例（通配符）
canoe_inst.execute_test_module('demo_test_node_002', enable_test_cases=["SmokeTest_*"])

# 禁用慢速/压力测试，启用其余全部（通配符）
canoe_inst.execute_test_module('demo_test_node_002', enable_test_cases=["*"], disable_test_cases=["*slow*", "*stress*"])

# 使用正则表达式按编号启用特定测试用例
canoe_inst.execute_test_module('demo_test_node_002', enable_test_cases=["(?i)^tc_(001|002|003)$"])

canoe_inst.stop_measurement()
```

### 获取测试模块结果（报告地址 + 测试用例判定）

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

canoe_inst.start_measurement()
canoe_inst.execute_test_module('demo_test_node_002')

# 获取结果：报告地址 + 所有测试用例判定
result = canoe_inst.get_test_module_result('demo_test_node_002')
print(f"判定结果: {result['verdict_name']}")
print(f"通过率: {result['pass_rate']:.1f}% ({result['passed']}/{result['total']})")
print(f"测试报告: {result['report']['generated_full_name']}")
for tc in result['test_cases']:
    print(f"  {tc['name']}: {tc['verdict_name']} (已启用={tc['enabled']})")

canoe_inst.stop_measurement()
```

### 获取/设置环境变量值

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

### 添加/移除数据库

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r"tests\demo_cfg\demo_conf_gen_db_setup.cfg")

canoe_inst.start_measurement()
# 按网络名添加数据库
canoe_inst.add_database(r"path\to\DBs\XCP.dbc", 'CAN1')
# 按通道号添加数据库
canoe_inst.add_database(r"path\to\DBs\XCP.dbc", 1)
# 移除数据库
canoe_inst.remove_database(r"path\to\DBs\XCP.dbc", 1)
```

### 获取已配置的网络名称

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

network_names = canoe_inst.application.networks.get_all_network_names()
```

### 获取已配置的仿真总线和数据库路径

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

bus_names = canoe_inst.get_simulation_bus_names()
db_paths = canoe_inst.get_simulation_database_paths()
```

### 启动/停止在线日志记录块

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r"tests\demo_cfg\demo_online_setup.cfg")

canoe_inst.start_measurement()
# 停止日志记录块
canoe_inst.start_stop_online_logging_block(fr'{demo_cfg_dir}\Logs\demo_online_setup_log.blf', start_stop=False)
wait(2)
# 启动日志记录块
canoe_inst.start_stop_online_logging_block(fr'{demo_cfg_dir}\Logs\demo_online_setup_log.blf', start_stop=True)
```

### 操作日志记录块

```python
from py_canoe import CANoe, wait

canoe_inst = CANoe()
# 移除当前日志记录块
for i in range(canoe_inst.logging_collection.count):
    canoe_inst.remove_logging_block(1)  # 索引从 1 开始，每次删除后索引会偏移
# 添加新的日志记录块
# 指定目标路径，文件格式支持 asc、blf 等
# 可包含字段函数如 {IncMeasurement}
full_path = "C:/sample_log_{IncMeasurement}.blf"
canoe_inst.add_logging_block(full_path)
canoe_inst.start_measurement()
# ...
canoe_inst.stop_measurement()
# 此时日志已完全生成，可供分析
canoe_inst.set_configuration_modified(False)  # 避免弹出"保存更改"对话框
canoe_inst.quit()
```

### 服务器/无头模式（无 GUI 交互）

默认情况下，py-canoe 使用 COM 事件接收器（`WithEvents`）来接收 CANoe 的通知（如测量已启动、测量已停止）。这对交互式桌面应用程序工作良好，但在服务器环境中可能会出现问题。

**问题描述：**
- 当 CANoe 繁忙时（如正在生成报告），可能以 `RPC_E_CALL_REJECTED` 拒绝 COM 调用
- 长时间运行的服务器进程需要对这些瞬态状态进行健壮的错误处理
- 在某些场景下，Windows 可能会显示"程序忙"对话框（在较新版本中已减少）

**解决方案：**
使用底层 `Application` 类并设置 `enable_events=False` 来禁用 COM 事件接收器。py-canoe 将改用轮询方式，这在服务器/无头操作中更加可靠：

```python
from py_canoe.core.application import Application

# 创建不使用 COM 事件接收器的实例（改用轮询）
app = Application(enable_events=False)
app.open(r'tests\demo_cfg\demo.cfg', visible=True, auto_save=True, prompt_user=False)

app.measurement.start()
# ... 运行测试 ...
app.measurement.stop()
app.quit()
```

### 添加网络 / 获取网络信息

```python
from py_canoe import CANoe
from py_canoe.helpers.bus_type import BusType

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

# 添加 CAN 网络（可指定软件通道号）
canoe_inst.add_netWork('NewCAN', BusType.CAN, sw_channel=2)
# 添加 LIN 网络
canoe_inst.add_netWork('NewLIN', BusType.LIN)
# 获取网络对象
bus = canoe_inst.get_network('CAN1')
# 按名称删除网络（最后一个网络无法删除）
canoe_inst.remove_netWork('NewCAN')
```

### 获取/设置通道使用情况

```python
from py_canoe import CANoe
from py_canoe.helpers.bus_type import BusType

canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

# 获取 CAN 通道使用情况
usage = canoe_inst.get_channelUsage(BusType.CAN)
# 设置 CAN 通道数量
canoe_inst.set_channelUsage(BusType.CAN, 3)
```

### 查询和设置硬件通道映射

```python
from py_canoe import CANoe, BusType

# 查询可用的 CAN 硬件通道（打开 CANoe 之前）
can_channels = CANoe().get_hardware_channels(BusType.CAN)
for ch in can_channels:
    print(ch.label)  # "Ch00 idx=0 [VN1630 CAN/Piggy]"

    # 将 CANoe 应用通道 0 映射到此物理通道
    ch.apply_to("CANoe", 0, BusType.CAN)

# 打开 CANoe 并添加网络（同时指定硬件通道）
canoe_inst = CANoe()
canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo_dev.cfg')

# 一站式：添加网络 + 软件通道 + 硬件通道
canoe_inst.add_netWork_with_hardware(
    'MyCAN2', BusType.CAN, sw_channel=1, hw_channel=can_channels[0])

# 查询当前映射
hw = canoe_inst.get_hardware_config(0, BusType.CAN)
print(hw.label if hw else "未配置硬件通道")

# 清空所有 CANoe 硬件通道映射
canoe_inst.clear_hardware_channels()
```

**参数说明：**
- `enable_events=False`：禁用 COM 事件接收器，使用轮询检测状态变化
- `timeout`：`start()` 和 `stop()` 方法可用（默认 30 秒）— 最大等待时间

**优势：**
- 减少"程序忙"对话框（内部 COM 代理共享）
- CANoe 暂时繁忙时自动重试（如正在生成报告）
- 对长时间运行的服务器进程安全（REST API、MCP 服务器、定时任务）
- 所有操作均可配置超时时间

**无需重启 CANoe 即可切换配置：**

服务器应用程序通常需要使用不同的 CANoe 配置运行测试。使用 `open_config()` 在保持 CANoe 运行的同时切换配置：

```python
# CANoe 已打开某个配置
canoe_inst.open_config(r'tests\demo_cfg\another_config.cfg', timeout=60)
# 现在已切换到新配置
```

**自定义 COM 消息泵送：**

在需要在自定义等待循环中泵送 COM 消息的高级场景中：

```python
import time

# 带 COM 消息泵送的自定义等待循环
while not my_condition():
    canoe_inst.pump_messages()  # 处理待处理的 COM 消息
    time.sleep(0.1)
```

## 重新生成 Robot Framework 包装库

本项目包含一个代码生成器，用于创建 `src/py_canoe/canoe_robot_lib.py` 中的 Robot Framework Python 库包装器。请勿手动编辑该文件——它是自动生成的。要重新生成，请运行：

```bash
python -m py_canoe.helpers.gen_canoe_robot_lib
```

生成的文件头部包含时间戳和生成器元数据。
