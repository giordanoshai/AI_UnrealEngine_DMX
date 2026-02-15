# AetherLight - sACN DMX 控制器

通过 sACN 协议向 Unreal Engine 发送 DMX 灯光控制数据。

## 🚀 快速开始

### 1. 验证连接（推荐第一步）
```bash
python quick_sacn_test.py
```
选择 "1" 进行基础连接测试，确保 UE 能收到数据。

### 2. 发送完整效果到 UE
```bash
python test_sacn_ue.py
```
将运行一个 20 秒的绿色扫动效果，控制 21 个摇头灯。

### 3. 尝试不同的效果
```bash
python effect_examples.py
```
可以选择 5 种预设效果（蓝色波动、红色脉冲、绿色扫动等）。

## 📋 前置要求

### Python 环境
- Python 3.8+
- 已安装依赖：`sacn` 库

### Unreal Engine 配置
1. **启用 DMX 插件**
   - Edit → Plugins → 搜索 "DMX" → 启用

2. **配置 DMX Library**
   - 创建 DMX Library
   - 添加 Controller（协议: sACN, Universe: 1）
   - ✅ 启用 "Receive DMX"

3. **查看接收状态**
   - Window → DMX → DMX Monitor
   - 选择 Universe 1

详细配置请参考：`docs/sacn_ue_guide.md`

## 📁 可用脚本

| 脚本 | 功能 | 适用场景 |
|------|------|----------|
| `quick_sacn_test.py` | 快速连接测试 | 首次使用，验证连接 |
| `test_sacn_ue.py` | 完整效果演示 | 测试实际效果 |
| `effect_examples.py` | 交互式效果选择 | 尝试不同效果 |
| `test_multi_fixture.py` | 本地计算测试 | 调试效果（无网络）|

## 🎯 自定义效果

创建你自己的效果：

```python
from aetherlight.dmx_translator import run_effect_with_sacn

# 定义效果
my_effect = {
    "effect_name": "custom_effect",
    "primitives": [
        {"channel": "pan",    "animation": "wave",   "params": {"speed": 0.5}},
        {"channel": "tilt",   "animation": "static", "params": {"value": 0.5}},
        {"channel": "dimmer", "animation": "static", "params": {"value": 1.0}},
    ]
}

# 发送到 UE
run_effect_with_sacn(
    effect_json=my_effect,
    project_file="projects/TEST1.json",
    fps=30,
    duration=None  # None = 无限循环，或设置秒数
)
```

## 📖 支持的动画类型

### static - 静态值
```python
{"channel": "dimmer", "animation": "static", "params": {"value": 0.8}}
```

### wave - 正弦波动
```python
{"channel": "pan", "animation": "wave", "params": {
    "speed": 0.3,    # 速度
    "min": 0.0,      # 最小值
    "max": 1.0       # 最大值
}}
```

## 🔧 故障排查

### UE 收不到数据？

1. **检查 Universe ID**
   - 应用层使用 Universe 0
   - UE 中配置为 Universe 1（自动映射）

2. **检查防火墙**
   - 允许 UDP 端口 5568

3. **运行快速测试**
   ```bash
   python quick_sacn_test.py
   ```
   选择 "1"，在 UE DMX Monitor 中应该看到所有通道都是 128

## 📚 文档

- **sACN 完整指南**: `docs/sacn_ue_guide.md`
- **实现总结**: `docs/sacn_implementation_summary.md`
- **多灯具控制**: `docs/multi_fixture_control.md`

## 🎓 技术说明

- **协议**: sACN (Streaming ACN / E1.31)
- **传输**: UDP 组播 (239.255.0.x)
- **端口**: 5568
- **帧率**: 30 FPS
- **灯具**: 21 个 RotaHead 摇头灯
- **通道**: 每个灯具 8 通道（Pan, Tilt, Color, Gobo, Dimmer, Shutter, Zoom, Frost）

## ⚡ 性能

- 延迟: < 33ms
- 带宽: ~40 KB/s per Universe
- 可靠性: 稳定 30 FPS

## 🎉 开始使用吧！

```bash
# 第一步：验证连接
python quick_sacn_test.py

# 第二步：发送效果
python test_sacn_ue.py

# 第三步：自定义你的效果！
```
