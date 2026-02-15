# sACN 集成指南 - 发送 DMX 数据到 Unreal Engine

## 概述
已成功集成 sACN（Streaming ACN / E1.31）协议，可以通过网络实时发送 DMX 数据到 Unreal Engine 中的灯具。

## 🎉 测试结果

✅ **成功运行测试**：
- 项目: TEST1
- 灯具数量: 21 个 RotaHead 摇头灯
- Universe: 0 (映射到 sACN Universe 1)
- 运行时长: 20 秒
- 帧率: 30 FPS
- 协议: sACN (E1.31) 组播模式

## 核心功能

### 1. SACNSender 类
位置：`aetherlight/sacn_sender.py`

**特性**：
- 自动 Universe 映射（0-based → 1-based）
- 组播模式（239.255.0.x）
- 批量发送多个灯具
- 自动填充 512 通道数据
- 上下文管理器支持

**Universe 映射**：
```
应用层 Universe 0 → sACN Universe 1
应用层 Universe 1 → sACN Universe 2
...
```

### 2. run_effect_with_sacn() 函数
位置：`aetherlight/dmx_translator.py`

实际发送 DMX 数据到网络的函数。

## 使用方法

### 方法 1: 使用测试脚本（推荐）

```bash
python test_sacn_ue.py
```

这个脚本会：
- 加载 TEST1.json 中的所有灯具
- 通过 sACN 发送绿色扫动效果
- 运行 20 秒并自动停止

### 方法 2: 在代码中调用

```python
from aetherlight.dmx_translator import run_effect_with_sacn

# 定义你的效果
effect = {
    "effect_name": "my_effect",
    "primitives": [
        {"channel": "pan",    "animation": "wave", "params": {"speed": 0.3}},
        {"channel": "dimmer", "animation": "static", "params": {"value": 1.0}},
        # ...
    ]
}

# 发送到 UE
run_effect_with_sacn(
    effect_json=effect,
    project_file="projects/TEST1.json",
    fps=30,
    duration=None,  # None = 无限循环
    source_name="My DMX Controller"
)
```

### 方法 3: 直接使用 SACNSender

```python
from aetherlight.sacn_sender import SACNSender

with SACNSender(source_name="Test") as sender:
    # 激活 Universe
    sender.activate_universe(0)  # 应用层 Universe 0
    
    # 发送 DMX 数据
    dmx_data = [255, 128, 64, ...]  # 最多 512 个通道
    sender.send_dmx(0, dmx_data)
    
    # 或批量发送多个灯具
    sender.send_multiple([
        {"universe": 0, "address": 1, "dmx_values": [255, 128, ...]},
        {"universe": 0, "address": 9, "dmx_values": [128, 64, ...]},
    ])
```

## Unreal Engine 配置

### 1. 启用 DMX 插件
1. 打开 UE 项目
2. Edit → Plugins
3. 搜索 "DMX"
4. 启用 "DMX Protocol" 插件
5. 重启 UE

### 2. 配置 DMX Library

#### 创建 DMX Library：
1. Content Browser → 右键 → DMX → DMX Library
2. 命名为 "DMXLibrary_TEST1"

#### 配置 Input/Output：
1. 打开 DMX Library
2. 在 "Controllers" 标签：
   - 添加 Protocol: sACN
   - Universe ID: 1（对应应用层的 Universe 0）
   - 启用 "Receive DMX"

#### 添加 Fixture Type：
1. 在 "Fixture Types" 标签：
   - 添加灯具类型（如 RotaHead）
   - 配置通道：
     - Channel 1: Pan (0-255)
     - Channel 2: Tilt (0-255)
     - Channel 3: Color Wheel (0-255)
     - Channel 4: Gobo Wheel (0-255)
     - Channel 5: Dimmer (0-255)
     - Channel 6: Shutter (0-255)
     - Channel 7: Zoom (0-255)
     - Channel 8: Frost (0-255)

#### 导入灯具：
1. 在 "Fixture Patch" 标签：
   - 从 MVR 导入，或
   - 手动添加 21 个灯具
   - 设置每个灯具的起始地址（1, 9, 17, 25, ...）

### 3. 在关卡中使用

#### 方法 A: DMX Fixture Actor
```cpp
// 在蓝图或 C++ 中
UDMXEntityFixturePatch* FixturePatch = ...;  // 从 DMX Library 获取
float PanValue = FixturePatch->GetNormalizedAttributeValue("Pan");
```

#### 方法 B: DMX Monitor
1. Window → DMX → DMX Monitor
2. 选择 Universe 1
3. 实时查看接收到的 DMX 值

### 4. 网络配置检查

确保防火墙允许：
- **协议**: UDP
- **端口**: 5568
- **组播地址**: 239.255.0.1（Universe 1）

Windows 防火墙规则：
```powershell
# 允许入站 sACN 数据
New-NetFirewallRule -DisplayName "sACN DMX Input" -Direction Inbound -Protocol UDP -LocalPort 5568 -Action Allow
```

## 效果示例

### 1. 静态白光
```python
effect = {
    "effect_name": "white_static",
    "primitives": [
        {"channel": "pan",         "animation": "static", "params": {"value": 0.5}},
        {"channel": "tilt",        "animation": "static", "params": {"value": 0.5}},
        {"channel": "color_wheel", "animation": "static", "params": {"value": "white"}},
        {"channel": "dimmer",      "animation": "static", "params": {"value": 1.0}},
        {"channel": "shutter",     "animation": "static", "params": {"value": 0.0}},
    ]
}
```

### 2. 动态扫光
```python
effect = {
    "effect_name": "scan_effect",
    "primitives": [
        {"channel": "pan",  "animation": "wave", "params": {"speed": 0.3, "min": 0.0, "max": 1.0}},
        {"channel": "tilt", "animation": "wave", "params": {"speed": 0.2, "min": 0.3, "max": 0.7}},
        {"channel": "color_wheel", "animation": "static", "params": {"value": "blue"}},
        {"channel": "dimmer",      "animation": "static", "params": {"value": 1.0}},
    ]
}
```

### 3. 呼吸灯效果
```python
effect = {
    "effect_name": "breathing",
    "primitives": [
        {"channel": "pan",    "animation": "static", "params": {"value": 0.5}},
        {"channel": "tilt",   "animation": "static", "params": {"value": 0.5}},
        {"channel": "dimmer", "animation": "wave",   "params": {"speed": 0.5, "min": 0.2, "max": 1.0}},
    ]
}
```

## 故障排查

### 问题 1: UE 收不到数据

**检查项**：
1. ✅ UE DMX 插件已启用
2. ✅ DMX Library 中的 Universe ID 正确（应为 1）
3. ✅ Controller 启用了 "Receive DMX"
4. ✅ 防火墙允许 UDP 5568 端口
5. ✅ 网络连接正常（可以 ping 通本机）

**测试方法**：
```python
# 发送简单的测试数据
from aetherlight.sacn_sender import SACNSender
import time

with SACNSender() as sender:
    sender.activate_universe(0)
    # 所有通道设为 128
    while True:
        sender.send_dmx(0, [128] * 512)
        time.sleep(0.1)
```

在 UE DMX Monitor 中应该能看到所有通道都是 128。

### 问题 2: 只有部分灯具有反应

**可能原因**：
- DMX 地址配置不匹配
- 灯具跨越多个 Universe

**解决方法**：
1. 检查 `TEST1.json` 中的 `address` 字段
2. 确保每个灯具的地址 + 通道数 ≤ 512
3. 如果有多个 Universe，确保 UE 中都已配置

### 问题 3: 数据延迟

**优化方法**：
```python
# 增加帧率
run_effect_with_sacn(..., fps=40)  # 或更高

# 减少数据处理
# 只更新变化的通道
```

## 技术细节

### sACN 协议特点
- **标准**: ANSI E1.31 (sACN)
- **传输**: UDP 组播
- **端口**: 5568
- **组播地址**: 239.255.0.x（x = Universe ID）
- **帧率**: 推荐 30-44 FPS
- **优先级**: 默认 100（0-200）

### 数据包结构
每个 sACN 数据包包含：
- Root Layer（ACN 协议头）
- Framing Layer（sACN 源信息）
- DMP Layer（512 通道 DMX 数据）

### 性能指标
- **延迟**: < 33ms @ 30 FPS
- **带宽**: ~1.3 KB/packet × 30 FPS = ~40 KB/s per Universe
- **可靠性**: UDP 无确认，但有帧序列号检测

## 完整工作流程

1. **编写效果** → 定义 JSON 效果描述
2. **加载项目** → 从 TEST1.json 加载灯具配置
3. **启动 sACN** → 初始化网络发送器
4. **实时计算** → 每帧计算所有灯具的 DMX 值
5. **网络发送** → 通过组播发送到 UE
6. **UE 接收** → DMX 插件解析数据
7. **驱动灯具** → 更新虚拟灯具参数

## 文件清单

- ✅ `aetherlight/sacn_sender.py` - sACN 发送器类
- ✅ `aetherlight/dmx_translator.py` - 效果翻译器（含 sACN 函数）
- ✅ `test_sacn_ue.py` - UE 测试脚本
- ✅ `projects/TEST1.json` - 项目配置（21 个灯具）

## 下一步建议

1. **实时音频同步**：集成 pyaudio，根据音乐节奏控制灯光
2. **时间轴编辑器**：创建 GUI 工具来设计复杂的灯光效果序列
3. **灯光分组**：支持从 TEST1.json 中的 `groups` 字段控制灯具组
4. **效果预设库**：创建常用效果的预设文件
5. **双向通信**：从 UE 读取灯具状态（sACN 支持双向）

## 参考资源

- [ANSI E1.31 标准](https://tsp.esta.org/tsp/documents/docs/ANSI_E1-31-2018.pdf)
- [UE DMX 插件文档](https://docs.unrealengine.com/en-US/WorkingWithMedia/IntegratingMedia/DMX/)
- [sacn Python 库](https://github.com/Hundemeier/sacn)
