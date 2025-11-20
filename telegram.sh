#!/bin/bash
# ============================================
#  Telegram 昵称自动更新时间脚本 安装环境检测工具
#  适用系统：Debian 10/11/12 及 Ubuntu 20/22+
# ============================================

echo -e "\n🔍 开始检测运行环境...\n"

# 检测 root 权限
if [ "$EUID" -ne 0 ]; then
  echo "❌ 请使用 root 权限运行：sudo bash install.sh"
  exit 1
fi

# ----------------------------
#  检测并安装 Python3
# ----------------------------
echo -n "🧪 检测 Python3 ... "
if command -v python3 >/dev/null 2>&1; then
    echo "✔ 已安装：$(python3 --version)"
else
    echo "未安装，正在安装..."
    apt update -y && apt install -y python3
fi

# ----------------------------
#  检测 pip3
# ----------------------------
echo -n "🧪 检测 pip3 ... "
if command -v pip3 >/dev/null 2>&1; then
    echo "✔ 已安装：pip3 OK"
else
    echo "未安装，正在安装..."
    apt install -y python3-pip
fi

# ----------------------------
#  检测 git
# ----------------------------
echo -n "🧪 检测 Git ... "
if command -v git >/dev/null 2>&1; then
    echo "✔ 已安装"
else
    echo "未安装，正在安装..."
    apt install -y git
fi

# ----------------------------
#  检测 screen（可选）
# ----------------------------
echo -n "🧪 检测 screen ... "
if command -v screen >/dev/null 2>&1; then
    echo "✔ 已安装"
else
    echo "未安装，正在安装..."
    apt install -y screen
fi

# ----------------------------
#  安装 Python 依赖库
# ----------------------------
echo -e "\n📦 正在安装 Python 依赖库...\n"

pip3 install --upgrade pip
pip3 install telethon backports.zoneinfo python-dotenv

echo -e "\n🎉 所有依赖已安装完成！\n"

# ----------------------------
#  提示下一步
# ----------------------------
cat <<EOF

============================================
  ✅ 环境检测与安装完成！
============================================

✔ Python3 已就绪
✔ pip3 已就绪
✔ Telethon 已安装
✔ git 可用于克隆你的 GitHub 代码
✔ screen 可后台运行脚本

接下来请执行以下命令开始配置你的脚本：

1. 克隆你的项目：
   git clone https://github.com/xl78482/telegram.git

2. 进入目录：
   cd telegram

3. 运行你的脚本：
   python3 telegram.py

📌 建议你设置环境变量（第一次运行会提示输入）：
export TG_API_ID=123456
export TG_API_HASH=xxxxxxxxxxxx
export TG_BOT_TOKEN=yyyyyyyyyyyy
export TG_OWNER_ID=123456789

💡 如需后台运行，请使用：
screen -S tg-clock python3 telegram.py

============================================
EOF