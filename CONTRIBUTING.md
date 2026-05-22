# 参与贡献

感谢关注本项目。

## 本地开发

1. Fork 仓库并 clone
2. `setup_env.bat` 或按 README 手动建 `.venv`
3. `copy .env.example .env` 并填入自己的 API Key（勿提交 `.env`）
4. `python main.py` 或 `run_debug.bat`

## 提交前检查

- 不要提交 `.env`、`data/`、`*.db`、`.venv/`、`DesktopPet.exe`
- 新形象素材放在 `形象/<包名>/`，体积过大的 GIF 请说明或考虑 Git LFS
- Python 变更保持与现有风格一致，优先小范围修改

## Pull Request

简要说明改动内容与测试方式（Windows + Python 3.12）。
