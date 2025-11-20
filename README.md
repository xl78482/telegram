# ⏰ Telegram 时间昵称自动更新脚本

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python">
  <img src="https://img.shields.io/badge/Telethon-Library-green?logo=telegram">
  <img src="https://img.shields.io/badge/Timezone-Beijing-red?logo=clockify">
  <img src="https://img.shields.io/badge/Auto%20Update-59s%20Trigger-success?logo=github">
</p>

自动在 Telegram 昵称显示当前北京时间（分钟级），**每分钟第 59 秒自动更新**。

示例：
```
Lina 2025-11-20 22:00 🕛
```

---

## ✨ 功能
- ⏱ 秒数 = **59** → 立即更新昵称  
- 🕰 自动选择整点/半点表盘 emoji  
- ✂ 保留原名，仅替换时间部分  
- 🤖 Bot 控制（支持）：`/status` `/start` `/stop` `/nickname`  
- 🛡 自动处理 FloodWait（限频安全等待）

---

## 🚀 使用方法

### 1️⃣ 安装依赖
```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install telethon
```

### 2️⃣ 配置环境变量
```bash
export TG_API_ID=你的API_ID
export TG_API_HASH=你的API_HASH
export TG_BOT_TOKEN=你的BotToken
export TG_OWNER_ID=你的数字ID
```

### 3️⃣ 启动脚本
```bash
python3 telegram.py
```

---

## ❓ 常见问题

**昵称会被覆盖吗？**  
不会，只更新 “时间 + emoji”。

**需要登录 Telegram 吗？**  
首次运行输入验证码即可。

**能后台运行吗？**  
可以：
```bash
nohup python3 telegram.py &
```

---