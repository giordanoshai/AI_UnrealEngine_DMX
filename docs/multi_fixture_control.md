# 多灯具控制功能说明

## 概述
已成功实现将 DMX 效果数据发送给项目文件（TEST1.json）中所有灯具的功能。

## 主要修改

### 1. dmx_translator.py 的改进

#### 新增功能函数：`run_effect_for_project()`
```python
def run_effect_for_project(effect_json: dict, project_file: str, fps: float = 30.0, duration: float = None)
```

**功能说明**：
- 从项目 JSON 文件（如 `projects/TEST1.json`）加载所有灯具配置
- 为每个灯具创建独立的 `EffectTranslator` 实例
- 为每个灯具计算正确的 DMX 起始地址
- 同时控制所有灯具，发送相同的效果数据

**参数**：
- `effect_json`: 效果定义（JSON 格式）
- `project_file`: 项目文件路径
- `fps`: 帧率（默认 30）
- `duration`: 运行时长（秒），None 表示无限循环

#### 保留原有功能：`run_effect()`
原有的单灯具控制函数 `run_effect()` 仍然保留，可以单独控制一个灯具。

### 2. 导入语句优化
改进了模块导入逻辑，支持：
- 包内调用（相对导入）
- 直接脚本执行（绝对导入）

## 测试结果

### 测试配置
- **项目文件**: `projects/TEST1.json`
- **灯具数量**: 21 个 RotaHead 摇头灯
- **测试效果**: 绿色波动 + Pan/Tilt 扫动
- **运行时长**: 15 秒
- **帧率**: 30 FPS

### 测试输出
```
✅ 运行结束，共 442 帧，15.0 秒
   已控制 21 个灯具
```

## 使用示例

### 方法 1: 直接运行 dmx_translator.py
```python
# 在 dmx_translator.py 的 __main__ 部分已配置好
python aetherlight/dmx_translator.py
```

### 方法 2: 使用独立测试脚本
```python
# 运行 test_multi_fixture.py
python test_multi_fixture.py
```

### 方法 3: 在自己的代码中调用
```python
from aetherlight.dmx_translator import run_effect_for_project

# 定义效果
effect = {
    "effect_name": "my_effect",
    "description": "我的自定义效果",
    "primitives": [
        {"channel": "pan",    "animation": "wave",   "params": {"speed": 0.25, "min": 0.2, "max": 0.8}},
        {"channel": "dimmer", "animation": "static", "params": {"value": 0.8}},
        # ... 更多通道
    ],
}

# 运行效果
run_effect_for_project(
    effect_json=effect,
    project_file="projects/TEST1.json",
    fps=30,
    duration=10  # 运行 10 秒，或 None 表示无限循环
)
```

## 数据流程

1. **加载项目文件** → 读取 `TEST1.json`
2. **解析灯具列表** → 获取所有灯具的配置（UUID、名称、DMX 地址等）
3. **创建 Translator** → 为每个灯具创建独立的 `EffectTranslator` 实例
4. **加载效果** → 每个 Translator 加载相同的效果定义
5. **实时循环**：
   - 每帧为所有灯具计算 DMX 值
   - 显示前 5 个灯具的状态（控制台输出）
   - 准备好发送到 DMX 硬件（当前注释掉）

## DMX 输出格式

每帧生成的数据结构：
```python
{
    "fixture_name": "RotaHead",      # 灯具名称
    "universe": 0,                    # DMX Universe
    "address": 1,                     # DMX 起始地址
    "dmx_values": [255, 128, ...],   # 相对通道值列表
    "dmx_absolute": {1: 255, 2: 128, ...}  # 绝对地址映射
}
```

## 下一步集成建议

要将数据实际发送到 DMX 硬件，可以：

1. **使用 ArtNet**（网络 DMX）：
```python
import artnet
artnet_node = artnet.Node(ip='192.168.1.100')
for dmx_data in all_dmx_data:
    artnet_node.send(dmx_data["dmx_values"], universe=dmx_data["universe"])
```

2. **使用 Enttec USB Pro**（USB DMX）：
```python
import serial
enttec = serial.Serial('COM3', baudrate=57600)
for dmx_data in all_dmx_data:
    enttec.write(build_enttec_packet(dmx_data["dmx_values"]))
```

3. **其他 DMX 接口**：根据具体硬件调整即可

## 文件清单

- ✅ `aetherlight/dmx_translator.py` - 主程序（已修改）
- ✅ `test_multi_fixture.py` - 测试脚本（新增）
- ✅ `projects/TEST1.json` - 项目文件（21 个灯具）
- ✅ `aetherlight/fixture_config.py` - 灯具通道配置
- ✅ `aetherlight/primitives.py` - 动画原语

## 验证清单

- ✅ 成功从 TEST1.json 加载 21 个灯具
- ✅ 为每个灯具正确设置 DMX 起始地址
- ✅ 实时计算所有灯具的 DMX 值
- ✅ 30 FPS 稳定运行
- ✅ 支持自定义效果和时长
- ✅ 控制台显示运行状态
