# Cue Player 使用说明

## 概述

Cue Player 是一个强大的灯光 Cue 播放控制系统,支持:
- 多效果连续播放 (Cue List)
- CUT/FADE 切换效果
- 多种 ease 函数
- 循环播放
- 手动控制(play/pause/stop/resume/next/prev/goto)

## 快速开始

### 1. 准备工作

**创建 Supabase 表:**
```bash
# 登录 Supabase Dashboard,在 SQL Editor 中执行:
# aetherlight/database/create_tables.sql
```

**上传 Effects 到 Supabase:**
```bash
cd d:\Dev_project\Python_Project\AI_DMX
.venv\Scripts\python upload_effects_to_supabase.py
```

### 2. 基础使用

```python
from aetherlight.cue_player import CuePlayer
from aetherlight.sacn_sender import SACNSender

# 初始化 sACN 发送器
sender = SACNSender()
sender.activate_universe(0)

# 创建 CuePlayer
player = CuePlayer(sender, fixtures, channel_config, fps=30)

# 加载 Cue List
cue_list = {
    "cue_list_name": "演示",
    "cues": [
        {
            "cue_number": 1,
            "effect_id": "blue_slow_wave",  # 从数据库加载
            "transition_type": "CUT",
        },
        {
            "cue_number": 2,
            "effect_id": "red_pulse",
            "transition_type": "FADE",
            "fade_time": 2.0,
            "ease_type": "ease_in_out_quad",
        },
    ],
    "loop": False
}

player.load_cue_list(cue_list)
player.play()
```

### 3. 运行演示

```bash
cd d:\Dev_project\Python_Project\AI_DMX
.venv\Scripts\python demo_cue_player.py
```

## Cue List JSON 格式

```json
{
  "cue_list_name": "演出名称",
  "project_id": "project-uuid",
  "cues": [
    {
      "cue_number": 1,
      "effect_id": "effect_name_or_uuid",
      "transition_type": "CUT" | "FADE",
      "fade_time": 2.0,
      "ease_type": "ease_in_out_quad",
      "comment": "备注"
    }
  ],
  "loop": false
}
```

## 可用的 Ease 函数

- `linear` - 线性
- `ease_in_quad` - 二次方 ease-in
- `ease_out_quad` - 二次方 ease-out
- `ease_in_out_quad` - 二次方 ease-in-out
- `ease_in_cubic` - 三次方 ease-in
- `ease_out_cubic` - 三次方 ease-out
- `ease_in_out_cubic` - 三次方 ease-in-out
- `ease_in_sine` - 正弦 ease-in
- `ease_out_sine` - 正弦 ease-out
- `ease_in_out_sine` - 正弦 ease-in-out

## API 参考

### CuePlayer 类

**方法:**

- `load_cue_list(cue_list_data)` - 加载 cue list
- `play()` - 开始播放
- `pause()` - 暂停播放
- `resume()` - 继续播放
- `stop()` - 停止播放
- `next_cue()` - 下一个 cue
- `prev_cue()` - 上一个 cue
- `goto_cue(cue_number)` - 跳到指定 cue

## 数据库迁移

将 SQLite 数据迁移到 Supabase:

```bash
cd d:\Dev_project\Python_Project\AI_DMX
.venv\Scripts\python -m etherlight.database.migrate_sqlite_to_supabasea
```

## 注意事项

1. **Effect Duration**: 所有 effect 必须包含 `duration` 字段
2. **切换类型**: 
   - `CUT` - 直接切换,无过渡
   - `FADE` - 淡入淡出,需要指定 `fade_time` 和 `ease_type`
3. **Discrete 通道**: color_wheel 和 gobo_wheel 等离散通道不会做 crossfade
4. **播放控制**: 不支持播放中修改 cue_list (热更新)
