# AI Desktop Pet · 桌面宠物

Windows 透明置顶桌宠：2D 立绘 / GIF、OpenAI 兼容聊天、生存模式、本地提醒与记忆。

![Python](https://img.shields.io/badge/python-3.12-blue)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6)
![License](https://img.shields.io/badge/license-MIT-green)

## 功能

- 多套 **2D 形象包**（PNG / GIF，悬停与随机切换）
- **OpenAI 兼容** 流式聊天（DeepSeek / OpenAI / Ollama 等，可停止生成）
- **生存模式**（12 段 HP、喂食、饿死骷髅复活）或 **普通模式**（无 HP）
- **本地提醒**（对话设置，托盘管理 / 取消）
- 记住用户名字与简短记忆（SQLite）
- 多显示器边界、托盘菜单、开机可选快捷方式

## 环境要求

- **Windows 10 / 11**（64 位）
- **Python 3.12**（源码运行；不要用 Anaconda 3.13 建 venv，易触发 Qt DLL 问题）
- 聊天可选：任意 OpenAI 兼容 API 的 Key、地址、模型名

## 快速开始（源码）

```bash
git clone https://github.com/<你的用户名>/<仓库名>.git
cd <仓库名>

# 方式一：自动安装
setup_env.bat

# 方式二：手动
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

也可双击 `run.bat` / `run.vbs`（无控制台用 `pythonw`）。

**首次启动**会弹出「选择形象」向导（`SHOW_CHARACTER_PICKER=1`）：选形象、生存/普通模式、聊天 API。勾选「下次不再询问」后，仍可在托盘 **「设置…」** 修改。

**桌面快捷方式**：运行 `创建桌面快捷方式.bat`。

## 配置聊天 API

支持 **任意 OpenAI 兼容接口**（三项都填才能聊天）：

| 配置项 | `.env` 变量 | 示例 |
|--------|-------------|------|
| API Key | `CHAT_API_KEY` | 平台提供的 sk-… |
| API 地址 | `CHAT_API_BASE_URL` | `https://api.deepseek.com` |
| 模型 | `CHAT_API_MODEL` | `deepseek-chat` |

旧版 `DEEPSEEK_*` 仍可读；在「设置」保存后会迁移为 `CHAT_API_*`。支持 OpenAI、Ollama 等。

填写方式（任选其一）：

1. 启动向导里填写  
2. 托盘 → **设置…**  
3. 编辑 `.env`（复制自 `.env.example`）

> **切勿将 `.env` 提交到 Git。** 详见 [docs/SECURITY.md](docs/SECURITY.md)。

## 运行模式

| `PET_MODE` | 说明 |
|------------|------|
| `survival`（默认） | 顶部 HP 条、桌面食物、喂食、饿死变骷髅、喂满复活 |
| `normal` | 仅陪伴与聊天，无 HP |

切换模式后需 **重新启动**（设置保存时会提示重启）。

## 内置形象包

资源目录：`形象/<包名>/`

| 包名 | 说明 | 人设 |
|------|------|------|
| `PuppyPal线条小狗` | GIF 动图，多表情 | 小狗 |
| `透明底银杰形象文件夹` | 透明 PNG，推荐 | 少女 |
| `银杰动漫蓝色衣服` | 蓝衣立绘 | 少女 |
| `银杰动漫形象` | 多动作，可自动扫描 | 少女 |

启动时可 **选择形象**，或托盘 **切换形象**（会重启）。托盘 **设置…** 可改模式与 API 而不必换形象。

常用 `.env`：

```env
CHARACTER_PACK=透明底银杰形象文件夹
CHARACTER_MAX_HEIGHT=220
MOOD_SWITCH_MS=4500
PET_MODE=survival
SHOW_CHARACTER_PICKER=1
```

| 变量 | 说明 |
|------|------|
| `CHARACTER_PACK` | 当前形象包文件夹名 |
| `PET_MODE` | `survival` / `normal` |
| `SHOW_CHARACTER_PICKER` | `1` 每次启动问形象；`0` 跳过（用托盘设置改回） |
| `CHAT_API_*` | 聊天 API 三项（OpenAI 兼容） |

扫描规则：默认随机轮播 GIF/PNG；文件名含「悬停/鼠标」→ 移入播放；「拖动/拖拽」→ 拖动时播放。宠物窗口可左键拖动。

## 使用

| 操作 | 方式 |
|------|------|
| 聊天 | 双击宠物 / 托盘「聊天」 |
| 设置 | 托盘 → **设置…**（模式、API、启动向导） |
| 生存喂食 | 生存模式下右键宠物 → 生成食物，拖到宠物上 |
| 提醒 | 对话设置，或托盘「管理提醒」→「添加提醒」（无需 API） |
| 管理提醒 | 托盘 → 管理提醒 |
| 使用说明 | 托盘 → 使用说明 / 关于 |
| 导入形象 | 拖文件夹到宠物上 |
| 切换形象 | 托盘 → 切换形象（重启） |

## 项目结构

```
├── main.py
├── app/          # Qt 窗口、托盘、设置、聊天
├── pet/          # 形象、GIF、生存
├── brain/        # 聊天与动作解析
├── memory/       # SQLite
├── reminder/
├── config/
├── docs/         # 打包、首次使用、安全说明
└── 形象/
```

## 给别人用（exe  zip）

```bat
build_release.bat
```

将 **`dist\DesktopPet\` 整个文件夹** 打成 zip 分发。用户解压后双击 `DesktopPet.exe`，按 **首次向导** 或 **docs/首次使用.txt** 操作即可，**无需安装 Python**。

详细步骤：[docs/PACKAGING.md](docs/PACKAGING.md) · 首次说明：[docs/首次使用.txt](docs/首次使用.txt)

## 常见问题

1. **看不到宠物**：任务栏托盘 ^ → 「桌面宠物」  
2. **聊天报错**：托盘「设置」检查 Key / 地址 / 模型；401 多为 Key 错误，404 多为模型名错误  
3. **未配置聊天**：三项 API 可留空，桌宠与提醒仍可用  
4. **QtCore DLL 错误**：删除 `.venv` 后 `setup_env.bat`；或安装 [VC++ 运行库](https://aka.ms/vs/17/release/vc_redist.x64.exe)  
5. **抠图伤衣服**：`CHARACTER_MATTE=off`  
6. **杀软报毒**：PyInstaller 常见误报，见 PACKAGING.md

## 开发与打包

```bash
.venv\Scripts\activate
python main.py
run_debug.bat
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

手测清单：[docs/MANUAL_TEST.md](docs/MANUAL_TEST.md)

不要用旧的 `build_launcher.bat`（依赖本机 `.venv`）。

## 开源协议

[MIT](LICENSE) — 代码可自由使用；`.env` 与 `data/` 请勿提交。

## 致谢

- [PySide6](https://doc.qt.io/qtforpython/)
- 各 OpenAI 兼容 API 服务商（由用户自行配置）
