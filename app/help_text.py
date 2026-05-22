"""Tray help / usage copy."""

from __future__ import annotations

from config.pet_mode import is_survival_mode
from config.version import APP_NAME, APP_VERSION


def general_help_text() -> str:
    lines = [
        "【在哪里找宠物】",
        "任务栏右下角点击 ^，找到「桌面宠物」托盘图标。",
        "",
        "【常用操作】",
        "· 双击宠物或托盘图标：打开聊天",
        "· 左键拖动：移动宠物（不超出当前屏幕）",
        "· 托盘「设置…」：运行模式、宠物大小滑块、聊天 API、启动向导",
        "· 托盘「切换形象」：更换立绘（会重启）",
        "",
        "【导入形象包】",
        "方式：托盘菜单「导入形象文件夹…」。",
        "",
        "导入什么：一个文件夹 = 一套形象，建议包含——",
        "· 透明背景的立绘图片（PNG 推荐，也可 GIF）",
        "· 多张不同动作/表情（如 站立.png、开心.png、悬停.png）",
        "· 可选：同目录放 人设.txt（或 persona.txt）",
        "  用于绑定这套形象的 AI 说话风格与性格",
        "",
        "文件夹结构示例：",
        "  我的角色/",
        "    动作1.png",
        "    动作2.png",
        "    悬停.png      ← 文件名含「悬停/鼠标」时，鼠标移入播放",
        "    拖动.png      ← 文件名含「拖动/拖拽」时，拖动窗口播放",
        "    人设.txt      ← 可选，不写则用默认小狗/少女人设",
        "",
        "也可拖入单张横向透明 PNG 图集，程序会自动切成多帧动作。",
        "导入成功后会复制到 形象/ 目录并切换为该包（同名会询问是否覆盖）。",
        "",
        "【聊天 API】",
        "不配置也能用桌宠；要 AI 聊天需在「设置」填 Key、地址、模型三项。",
        "支持 DeepSeek、OpenAI、Ollama 等 OpenAI 兼容接口。",
        "",
        "【提醒】",
        "· 配置 API 后可在聊天里说「明天下午 3 点提醒我…」",
        "· 或托盘「管理提醒」→「添加提醒」手动创建",
    ]
    if is_survival_mode():
        lines.extend(["", survival_help_text()])
    return "\n".join(lines)


def survival_help_text() -> str:
    return "\n".join(
        [
            "【生存模式】",
            "· 顶部 12 格 HP，约每小时减 1 格",
            "· 右键宠物 →「生成食物」，把食物拖到宠物身上喂食",
            "· HP 归零会变成骷髅；再右键生成食物，喂满 3 次可复活",
            "· 设置里「生存记忆」：开启后退出程序也计时，久不打开会离线饿死",
            "· 关闭生存记忆：仅程序开着时扣 HP",
            "· 右键「加速一小时」：快进时间（方便测试）",
        ]
    )


def about_text() -> str:
    return (
        f"{APP_NAME}\n"
        f"版本 {APP_VERSION}\n\n"
        "Windows 透明桌宠 · 2D 形象 · OpenAI 兼容聊天\n"
        "生存模式 · 本地提醒与记忆\n\n"
        "开源协议：MIT"
    )
