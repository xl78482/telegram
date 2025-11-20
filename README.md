📜 Telegram 自动更新时间昵称脚本 功能介绍与使用方法

1. 📋 功能介绍

该脚本通过 Telegram API 和 Telethon 库，实现了实时监控当前北京时间并且 在秒数达到59时自动更新 Telegram 昵称。它支持 Telegram Bot 控制，可以远程查看脚本状态、启动和停止脚本，甚至查看当前的 Telegram 昵称。

主要功能：

自动更新时间昵称：每分钟更新一次 Telegram 昵称，显示当前时间和表盘符号。

秒数到达59时立即更新：当秒数到达 59 时，立刻更新昵称，确保精准的时间显示。

昵称格式：Lina 2025-11-20 22:00 🕛（不显示秒数）。

Telegram Bot 控制：

/status 查看脚本状态

/start 启动脚本

/stop 停止脚本

/nickname 查看当前昵称


自动处理 FloodWait：在 Telegram 限频时自动等待，不会崩溃或退出。


2. 🛠 依赖安装与配置

2.1 安装依赖

该脚本依赖于 Python 3 和 Telethon 库。你需要先安装 Python 和相关依赖：

# 安装 Python 3 和 pip
sudo apt update
sudo apt install python3 python3-pip

# 安装 Telethon 库
pip3 install telethon

2.2 获取 Telegram API 密钥

1. 访问 Telegram API 申请 API ID 和 API Hash。


2. 创建一个 Bot：

通过 BotFather 创建一个 Bot，获取 Bot Token。




2.3 配置环境变量

为了使脚本正常运行，你需要设置以下环境变量：

export TG_API_ID=你的API_ID
export TG_API_HASH=你的API_HASH
export TG_BOT_TOKEN=你的Bot Token
export TG_OWNER_ID=你的Telegram数字ID

> 注意：

TG_API_ID 和 TG_API_HASH 从 Telegram API 获取。

TG_BOT_TOKEN 由 BotFather 获取。

TG_OWNER_ID 是你的 Telegram 数字 ID，可以通过向 userinfobot 发送消息来获取。




2.4 运行脚本

设置完环境变量后，运行以下命令启动脚本：

python3 tg_name_clock.py

脚本会开始运行并自动更新 Telegram 昵称。

3. 💡 使用方法

3.1 脚本功能

自动更新时间：每秒钟检查当前时间，当秒数达到59时，会立即更新 Telegram 昵称。

昵称格式：昵称格式为 Lina 2025-11-20 22:00 🕛，不包含秒数，且每次更新时间都会更新日期和表盘符号。

Bot 控制：通过 Telegram Bot 控制脚本。

/status：查看当前脚本状态，包括当前时间、最后更新时间、FloodWait 状态等。

/start：启动脚本，开始自动更新。

/stop：停止脚本，停止自动更新。

/nickname：查看当前的 Telegram 昵称。



3.2 Telegram Bot 控制

启动脚本后，你可以通过与 Bot 进行交互来控制脚本的运行。以下是可以使用的命令：

/status
查看当前脚本状态，包括当前时间、最后更新时间和 FloodWait 状态。

示例：

🟢 *脚本运行状态*

⏱ 当前北京时间：`2025-11-20 22:05:03`
🕒 最近检测时间：`2025-11-20 22:05`
🔄 最近更新时间：`2025-11-20 22:05:00`
⛔ FloodWait：`False`
📡 是否运行：`True`

/start
启动脚本。如果脚本已经在运行，则提示已经启动。

示例：

🚀 脚本已重新启动

/stop
停止脚本的运行，停止自动更新时间。

示例：

🛑 已停止更新时间脚本

/nickname
查看当前 Telegram 昵称。

示例：

👤 当前昵称： `Lina 2025-11-20 22:05 🕛`


3.3 停止脚本

如果你需要停止脚本，可以通过 /stop 命令在 Telegram 中停止脚本，或者在 VPS 终端中使用 Ctrl + C 终止脚本。

3.4 FloodWait 处理

如果脚本频繁更新 Telegram 昵称，Telegram API 可能会返回 FloodWait 错误（即限频）。脚本会自动处理这种情况，等待一定的时间后继续更新，不会退出或崩溃。


---

4. 🧑‍💻 脚本优化与扩展

如果你希望对脚本进行扩展或修改，可以参考以下常见的优化方向：

邮件推送功能：实现当脚本运行状态变化时，通过邮件发送通知。

Web UI：使用 Flask 或 Django 创建一个 Web 面板来显示脚本状态和控制。

Docker 化部署：将脚本放入 Docker 容器中，方便跨平台部署。


如果你有这些需求，可以随时联系我，我可以帮你进行调整和优化。


---

5. 📝 总结

通过这个脚本，你可以自动化地更新 Telegram 昵称，以精确的时间和表盘符号显示当前时间，并且通过 Telegram Bot 控制脚本的运行。这个脚本非常适合用于 展示动态时间，或者在 特定场合下使用。

如果在使用过程中遇到任何问题，欢迎随时提问！

---
📩 联系方式
如有任何疑问，欢迎通过以下方式联系我：
  Telegram: @n456n
