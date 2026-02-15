# Effect 和 Cue List 编辑器使用说明

## 功能概述

新增了两个编辑页面，用于管理灯光效果(Effect)和 Cue List。这两个页面均采用左侧列表、右侧编辑区域的布局，与现有UI框架保持一致。

## Effect 编辑器

### 功能特点

1. **左侧列表**：显示所有已创建的 Effects
2. **右侧编辑区域**：
   - 基本信息编辑（名称、描述、时长）
   - Channel 配置表格，显示所有 channel
   - 未编辑的 channel 自动使用 `fixture_config.py` 中的默认值

### 操作说明

#### 创建新 Effect
1. 点击工具栏中的 "✨ Effect 编辑" 切换到 Effect 编辑页面
2. 点击 "➕ 新建 Effect" 按钮
3. 系统会创建一个默认的 Effect，所有 channel 使用默认值
4. 在右侧编辑区域修改 Effect 信息：
   - **名称**：输入 Effect 名称
   - **描述**：输入 Effect 描述（可选）
   - **时长**：设置 Effect 持续时间（秒）
   - **Channel 配置**：在表格中修改每个 channel 的值
5. 点击 "💾 保存" 保存修改

#### 编辑 Effect
1. 在左侧列表中选择要编辑的 Effect
2. 右侧会自动加载该 Effect 的详细信息
3. 修改需要更改的内容
4. 点击 "💾 保存" 保存修改

#### 删除 Effect
1. 在左侧列表中选择要删除的 Effect
2. 点击 "🗑️ 删除" 按钮
3. 确认删除操作

### Channel 配置说明

Channel 配置表格显示了 `fixture_config.py` 中定义的所有 channel：

| Channel | 类型 | 默认值 | 说明 |
|---------|------|--------|------|
| pan | continuous | 0.5 | 水平旋转 (0~1) |
| tilt | continuous | 0.5 | 垂直旋转 (0~1) |
| color_wheel | discrete | white | 色片选择 |
| gobo_wheel | discrete | solid | 图案选择 |
| dimmer | continuous | 1 | 调光 (0~1) |
| shutter | continuous | 1 | 快门 (0~1) |
| zoom | continuous | 1 | 缩放 (0~1) |
| frost | continuous | 1 | 柔光 (0~1) |

- **continuous** 类型：使用数值编辑（0~1）
- **discrete** 类型：使用预定义的字符串值（如 "white", "red" 等）

## Cue List 编辑器

### 功能特点

1. **左侧列表**：显示所有已创建的 Cue Lists
2. **右侧编辑区域**：
   - 基本信息编辑（名称、关联项目、循环播放）
   - Cue 配置表格，支持添加、删除、排序 Cues

### 操作说明

#### 创建新 Cue List
1. 点击工具栏中的 "🎬 Cue List 编辑" 切换到 Cue List 编辑页面
2. 点击 "➕ 新建 Cue List" 按钮
3. 系统会创建一个默认的 Cue List
4. 在右侧编辑区域修改 Cue List 信息：
   - **名称**：输入 Cue List 名称
   - **项目**：从下拉菜单选择关联的项目
   - **循环播放**：勾选是否循环播放
5. 添加 Cues（见下文）
6. 点击 "💾 保存" 保存修改

#### 管理 Cues

**添加 Cue**：
1. 点击 "➕ 添加 Cue" 按钮
2. 在新增的行中配置：
   - **Effect**：从下拉菜单选择要播放的 Effect
   - **Transition**：选择转场类型（CUT 或 FADE）
   - **Fade Time (s)**：设置淡入淡出时间（仅 FADE 有效）
   - **Group**：指定播放的分组名称

**删除 Cue**：
1. 在表格中选中要删除的 Cue
2. 点击 "➖ 删除 Cue" 按钮

**调整 Cue 顺序**：
1. 在表格中选中要移动的 Cue
2. 点击 "⬆️ 上移" 或 "⬇️ 下移" 按钮
3. Cues 会按表格中的顺序播放

#### 编辑 Cue List
1. 在左侧列表中选择要编辑的 Cue List
2. 右侧会自动加载该 Cue List 的详细信息
3. 修改需要更改的内容
4. 点击 "💾 保存" 保存修改

#### 删除 Cue List
1. 在左侧列表中选择要删除的 Cue List
2. 点击 "🗑️ 删除" 按钮
3. 确认删除操作

## 页面切换

在主窗口工具栏中可以切换不同的页面：

- 📁 **导入管理**：GDTF 和 MVR 导入页面
- 📋 **分组管理**：灯具分组管理页面
- ✨ **Effect 编辑**：灯光效果编辑页面（新增）
- 🎬 **Cue List 编辑**：Cue List 编辑页面（新增）

## 数据存储

所有的 Effects 和 Cue Lists 数据都存储在 Supabase 数据库中，支持：
- 自动保存
- 跨设备同步
- 多用户协作

## 技术实现

### 文件结构

```
aetherlight/
├── gui/
│   ├── effect_editor_page.py     # Effect 编辑页面
│   ├── cue_list_editor_page.py   # Cue List 编辑页面
│   └── main_window.py             # 主窗口（已更新）
├── database/
│   └── database.py                # 数据库操作
└── fixture_config.py              # Channel 配置和默认值
```

### 数据模型

**Effect**:
```python
{
    "id": "uuid",
    "effect_name": "Effect 名称",
    "description": "描述",
    "primitives": [
        {
            "type": "static",
            "channels": {
                "pan": 0.5,
                "tilt": 0.5,
                # ...
            },
            "duration": 10.0
        }
    ],
    "duration": 10.0
}
```

**Cue List**:
```python
{
    "id": "uuid",
    "cue_list_name": "Cue List 名称",
    "project_id": "项目 UUID",
    "cues": [
        {
            "effect_id": "Effect UUID",
            "transition": "CUT" or "FADE",
            "fade_time": 1.0,
            "group": "default"
        }
    ],
    "loop": false
}
```

## 注意事项

1. **Effect 名称**：必须唯一且不能为空
2. **Cue List 项目**：创建 Cue List 前需要先创建项目
3. **Effect 引用**：删除 Effect 前请确保没有 Cue List 引用该 Effect
4. **默认值**：Channel 的默认值定义在 `fixture_config.py` 中，可以根据实际灯具修改
5. **数据同步**：所有数据实时保存到云端数据库

## 后续扩展

可能的功能扩展：
- Effect 预览功能
- Cue List 播放控制
- 复制/粘贴 Effect 或 Cue
- 批量编辑 Channel
- 导入/导出 Effect 库
