
MOVE_HEAD = {
    "fixture_id": "FD9E205E-4729-3C5B-5AC5-7A97BF09E833",
    "name": "DMXL_huzhou RotaHead",
    "dmx_start_address": 1,    # DMX 起始地址，根据实际修改
    "channels": {
        "pan": {
            "offset": 0,
            "default_value": 0.5,
            "type": "continuous",  # 连续值 0~1 → DMX 0~255
        },
        "tilt": {
            "offset": 1,
            "default_value": 0.5,
            "type": "continuous",
        },
        "color_wheel": {
            "offset": 2,
            "default_value": "white",  # 使用字符串名称,会自动查找 mapping
            "type": "discrete",
            "mapping": {
                # 色片名 → DMX 值,根据 color_table.json
                "white": 2,           # 0-4
                "red": 10,            # 9-12
                "orange": 19,         # 18-21
                "aquamarine": 27,     # 26-29
                "green": 36,          # 35-38
                "light_green": 44,    # 43-46
                "lavender": 53,       # 52-55
                "pink": 61,           # 60-63
                "yellow": 70,         # 69-72
                "magenta": 79,        # 77-81
                "cyan": 87,           # 86-89
                "light_blue": 96,        # 94-98
                "light_yellow": 104,       # 103-106
                "blood_yellow": 113,      # 111-115
                "blue": 121,          # 120-123
            },
        },
        "gobo_wheel": {
            "offset": 3,
            "default_value": "solid",  # 使用字符串名称,会自动查找 mapping
            "type": "discrete",
            "mapping": {
                # 图案名 → DMX 值,根据 gobo_table.json 和 gobo_pic_name.md
                "solid": 1,           # 0-3 (T_Gobo_White - 纯白)
                "dots": 5,            # 4-7 (T_Gobo_01 - 点阵)
                "grid": 9,            # 8-11 (T_Gobo_02 - 网格)
                "starburst": 13,      # 12-15 (T_Gobo_03 - 放射星芒)
                "rays": 17,           # 16-19 (T_Gobo_04 - 光线条)
                "spiral": 21,         # 20-23 (T_Gobo_05 - 螺旋)
                "waves": 25,          # 24-27 (T_Gobo_06 - 波纹)
                "cross": 29,          # 28-31 (T_Gobo_07 - 十字形)
                "blades": 33,         # 32-35 (T_Gobo_08 - 扇叶/刀片状)
                "scatter": 37,        # 36-39 (T_Gobo_09 - 随机散点)
                "ring": 41,           # 40-43 (T_Gobo_10 - 圆环)
                "triangle": 45,       # 44-47 (T_Gobo_11 - 三角形)
                "hexagon": 49,        # 48-51 (T_Gobo_12 - 六边形)
                "burst": 53,          # 52-55 (T_Gobo_13 - 爆裂/爆点)
                "stripe": 57,         # 56-59 (T_Gobo_14 - 条纹)
                "noise": 61,          # 60-63 (T_Gobo_15 - 噪点)
                "flower": 65,         # 64-67 (T_Gobo_16 - 花形)
                "swirl": 69,          # 68-71 (T_Gobo_17 - 旋涡)
            },
        },
        "dimmer": {
            "offset": 4,
            "default_value": 1,
            "type": "continuous",
        },
        "shutter": {
            "offset": 5,
            "default_value": 1,
            "type": "continuous",
        },
        "zoom": {
            "offset": 6,
            "default_value": 1,
            "type": "continuous",
        },
        "frost": {
            "offset": 7,
            "default_value": 1,
            "type": "continuous",
        },
    },
}
