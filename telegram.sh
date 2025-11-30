#!/bin/bash

echo "==========================================="
echo "     缔造者 Telegram 一键部署（作者@n456n）"
echo "==========================================="

cd "$(dirname "$0")"

# ------------------------------------
# 0. 自动赋予权限
# ------------------------------------
chmod +x *.sh 2>/dev/null
chmod +x *.py 2>/dev/null

# ------------------------------------
# 1. 检查系统类型
# ------------------------------------
if command -v apt >/dev/null 2>&1; then
    PKG_INSTALL="sudo apt install -y"
    PKG_UPDATE="sudo apt update -y"
elif command -v yum >/dev/null 2>&1; then
    PKG_INSTALL="sudo yum install -y"
    PKG_UPDATE="sudo yum makecache"
else
    echo "❌ 不支持的系统，请使用 Debian / Ubuntu / CentOS"
    exit 1
fi

# ------------------------------------
# 2. 安装 curl 或 wget（脚本下载依赖）
# ------------------------------------
if ! command -v curl >/dev/null 2>&1; then
    if ! command -v wget >/dev/null 2>&1; then
        echo "📦 curl / wget 不存在，正在安装..."
        eval "$PKG_UPDATE"
        eval "$PKG_INSTALL curl wget"
    fi
else
    echo "✔ curl 已安装"
fi

# ------------------------------------
# 3. 安装 Python3
# ------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "📦 python3 未安装，正在安装..."
    eval "$PKG_UPDATE"
    eval "$PKG_INSTALL python3"
else
    echo "✔ python3 已安装"
fi

# ------------------------------------
# 4. 安装 pip3
# ------------------------------------
if ! command -v pip3 >/dev/null 2>&1; then
    echo "📦 pip3 未安装，正在安装..."
    eval "$PKG_INSTALL python3-pip"
else
    echo "✔ pip3 已安装"
fi

# ------------------------------------
# 5. 安装 Python 依赖 telethon + aiohttp
# ------------------------------------
echo "🔍 检查 Python 依赖..."

REQS=("telethon" "aiohttp")

for pkg in "${REQS[@]}"; do
    python3 -c "import $pkg" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "📦 缺少依赖：$pkg → 正在安装..."
        pip3 install $pkg
    else
        echo "✔ 已存在：$pkg"
    fi
done

# ------------------------------------
# 6. 启动主程序
# ------------------------------------
echo ""
echo "🚀 启动 telegram.py..."
echo ""

python3 telegram.py
