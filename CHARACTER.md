# 角色与形象说明

人设由 `brain/prompts.py` 与 `.env` 中的 `CHARACTER_PERSONA`（`dog` / `girl` / `auto`）控制。

## 形象资源

所有立绘放在 **`形象/<包名>/`**，在 `.env` 配置 `CHARACTER_PACK` 即可。

详见 [README.md](README.md) 中的「内置形象包」表格与 `.env.example`。

## 添加新形象

1. 在 `形象/` 下新建文件夹，放入 PNG（可选同名 GIF 动画）
2. 在 `.env` 设置 `CHARACTER_PACK=你的文件夹名`
3. 动作触发：含「鼠标/拖动」→ 悬停/拖拽；其余（走动、运动、开心等）→ 定时随机播 GIF/PNG（原地，不自动满屏走动）
4. 重启程序，或在托盘「切换形象」中选择（若已加入 `config/character_presets.py` 可显示中文标题）

`assets/character/` 仅保留说明文件；实际素材使用项目根目录的 `形象/`。
