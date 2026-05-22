# 脚本说明

| 脚本 | 用途 |
|------|------|
| `create_shortcut.ps1` | 在桌面生成带图标的 `.lnk` 快捷方式（由根目录 `创建桌面快捷方式.bat` 调用） |
| `build_app_icon.py` | 从 `APP_ICON_SOURCE` 生成 `assets/app_icon.ico` |
| `import_puppypal_pack.py` | 导入 PuppyPal 素材到 `形象/`（一次性工具） |
| `split_transparent_sheet.py` | 切分透明立绘大图集 |
| `render_spz_wallpaper.py` | 壁纸相关渲染工具 |
| `launcher.py` | PyInstaller 打包入口（生成 `DesktopPet.exe`） |

打包 exe（可选）：

```bat
build_launcher.bat
```

生成根目录 `DesktopPet.exe`（已在 `.gitignore`，勿提交仓库）。
