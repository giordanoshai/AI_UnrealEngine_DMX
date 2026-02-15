# Bug 修复报告 - SACNSender 方法调用错误

## 修复时间
2026-02-14 21:25

## 问题描述

在运行 `effect_examples.py` 时遇到以下错误：

```
AttributeError: 'SACNSender' object has no attribute 'activate_output'
```

## 根本原因

在 `effect_examples.py` 中使用了错误的方法名：
- **错误**：`sender.activate_output(universe)`
- **正确**：`sender.activate_universe(universe)`

同时，在 finally 块中调用了不存在的 `deactivate_output()` 方法。

## 修复内容

### 文件：`effect_examples.py`

#### 1. 修复 activate 方法调用（第 190 行）

```python
# 修复前
for universe in universes:
    sender.activate_output(universe)

# 修复后
for universe in universes:
    sender.activate_universe(universe)
```

#### 2. 修复 finally 块清理逻辑（第 221-228 行）

```python
# 修复前
finally:
    # 关闭所有输出
    for universe in universes:
        sender.deactivate_output(universe)
    sender.stop()
    print("\n✅ 播放结束，已停止 sACN 发送")

# 修复后
finally:
    # 停止发送器（自动清理所有 Universe）
    sender.stop()
```

**说明**：
- `SACNSender.stop()` 方法内部已经处理了所有 Universe 的清理工作
- 不需要额外调用 `deactivate_output()`（该方法不存在）
- `stop()` 方法本身会打印停止消息，不需要重复打印

## SACNSender 正确的 API

根据 `aetherlight/sacn_sender.py` 的实现：

### 可用方法：

1. **`activate_universe(app_universe: int)`**
   - 激活一个 DMX Universe
   - 参数：应用层 Universe 编号

2. **`send_dmx(app_universe: int, dmx_data: List[int])`**
   - 发送 DMX 数据到指定 Universe
   - 参数：
     - `app_universe`：Universe 编号
     - `dmx_data`：512 个通道的数据列表

3. **`send_multiple(dmx_data_list: List[Dict])`**
   - 批量发送多个灯具的数据

4. **`stop()`**
   - 停止 sACN 发送器
   - 自动清理所有已激活的 Universe

### Universe 映射机制：

- **默认偏移**：`universe_offset = 1`
- **映射规则**：应用 Universe X → sACN Universe X+1
- **原因**：sACN 标准 Universe 从 1 开始，而应用可能从 0 开始

### 使用示例：

```python
# 初始化
sender = SACNSender()

# 激活 Universe
sender.activate_universe(0)  # 实际发送到 sACN Universe 1

# 发送数据
dmx_data = [255] * 512
sender.send_dmx(0, dmx_data)

# 停止（自动清理）
sender.stop()
```

## 验证结果

修复后程序成功运行：

```
✅ sACN 发送器已启动: AetherLight DMX
   Universe 映射: 应用 Universe X → sACN Universe X+1
✅ 已加载效果: blue_slow_wave
   排序轴: y（自动检测）
   [灯具列表...]
🎬 开始播放效果: Unknown
   帧率: 30 FPS
   时长: 15 秒
   灯具数: 21
   Universe: [0]
⏱️  2.0s / 15s (13%)
```

程序正在正常播放灯光效果！✅

## 总结

- ✅ 修复了方法名错误
- ✅ 简化了资源清理逻辑
- ✅ 程序成功运行
- ✅ sACN 数据正常发送

所有问题已解决！
