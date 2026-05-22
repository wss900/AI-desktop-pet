# 打包成 exe 分发给他人

## 重要说明

旧的 `build_launcher.bat` 生成的 **单个 DesktopPet.exe** 仍依赖本机 `.venv`，**不能**发给没装 Python 的人。

请使用 **`build_release.bat`**，生成完整文件夹 `dist/DesktopPet/`。

## 在你电脑上打包（只需做一次）

### 1. 准备环境

```bat
setup_env.bat
```

### 2. 打包

```bat
build_release.bat
```

完成后得到：

```
dist/DesktopPet/
  DesktopPet.exe
  _internal/          ← PySide6 等依赖（勿删）
  形象/
  assets/
  .env.example
  首次使用.txt
  使用说明.txt        ← 来自 README 摘要
```

### 3. 发给用户

1. 把 **整个 `DesktopPet` 文件夹** 打成 zip（例如 `DesktopPet-win64.zip`）
2. 上传到网盘 / GitHub Releases
3. 附带说明：**Windows 10/11 64 位**，解压后双击 exe，按首次向导配置

**zip 内不要包含你的 `.env`（含 API Key）。** 只保留 `.env.example`。

## 用户电脑上的步骤

1. **解压** zip 到任意路径（如 `D:\DesktopPet`）
2. 双击 **`DesktopPet.exe`**
3. 在 **首次「选择形象」向导** 中：
   - 选形象、生存/普通模式
   - 可选填 OpenAI 兼容 API（Key + 地址 + 模型）；可先留空
4. 之后改配置：任务栏托盘 → 右键 → **「设置…」**
5. 若提示 DLL 错误，安装 [VC++ 运行库 x64](https://aka.ms/vs/17/release/vc_redist.x64.exe)

用户 **不需要** 安装 Python。程序首次运行会自动从 `.env.example` 生成 `.env`（若不存在）。

也可阅读包内 **`首次使用.txt`**（与 `docs/首次使用.txt` 同步）。

## 只打包一套形象（当前默认）

编辑 **`build/release_pack.txt`**（首行写文件夹名）：

```text
透明底小女孩示例
```

然后运行 `build_release.bat`。发布包内 **只有** `形象/<上述名称>/`，不含其它形象包。

默认配置见 **`build/.env.release.example`**（`CHARACTER_PACK` 已对准该包，`SHOW_CHARACTER_PICKER=0`）。

## 体积

| 内容 | 约大小 |
|------|--------|
| PySide6 + 依赖 | ~120–180 MB |
| 单套形象素材 | 视 PNG/GIF 数量 |

若要打包全部形象，将 `build/DesktopPet.spec` 的 `datas` 改回整目录 `形象/`。

## 单文件 exe（不推荐）

onedir 更稳定；onefile 启动慢且易出现 Qt 插件路径问题。

## 上架 GitHub Releases 示例

```text
DesktopPet-v1.0-win64.zip
  └── DesktopPet/
        DesktopPet.exe
        _internal/
        形象/
        首次使用.txt
        ...
```

Release 说明建议写明：

- Windows 10/11 64 位
- 聊天需自备 OpenAI 兼容 API（可选）
- 可能需要 VC++ 运行库
- 密钥仅存本机，见 [SECURITY.md](../SECURITY.md)

## 常见问题

**Q：exe 能开但形象不对？**  
重新 `build_release.bat`，或把 `_internal\形象` 复制到 exe 同级 `形象\`。

**Q：用户不会配 API？**  
说明可在首次向导或托盘「设置」填写；不填也能用桌宠与提醒。

**Q：打包报错 PySide6 / PyQt5 冲突？**  
只用项目 `.venv` 内的 `pyinstaller.exe`，见上文 `setup_env.bat`。

**Q：杀毒软件报毒？**  
PyInstaller 常被误报；可代码签名或让用户添加信任。

**Q：切换形象 / 改模式后？**  
切换形象、修改运行模式后会自动重启；仅改 API 时保存即可立即生效。
