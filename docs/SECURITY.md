# 安全与隐私说明

## 本地数据

- **`.env`**：存放 API Key、形象与模式配置，仅在本机读写。
- **`data/`**：SQLite 数据库，保存对话片段、用户名字与简短记忆、提醒记录。

本程序**不会**把 API Key 或聊天内容发送到除你配置的 API 地址以外的第三方服务器（聊天请求走你填写的 OpenAI 兼容接口）。

## 分发时注意

- **切勿**将含有真实 `CHAT_API_KEY` 的 `.env` 打进 zip、提交 Git 或发到公开群。
- 若 Key 曾误提交仓库，请在对应平台**立即轮换**密钥。
- 发给他人请使用 **`build_release.bat`** 生成的包，并确认 zip 内只有 `.env.example` 模板。

## 聊天 API

推荐使用 `CHAT_API_KEY` / `CHAT_API_BASE_URL` / `CHAT_API_MODEL`；旧 `DEEPSEEK_*` 仍可读。可填任意 OpenAI 兼容服务。

三项（Key、地址、模型）均非空时才会发起网络请求。
