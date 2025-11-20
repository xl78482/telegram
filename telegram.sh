#!/bin/bash

###############################################
# Telegram 后台永不停止自动运行脚本（自动 systemd）
# 作者： @n456n
###############################################

APP_NAME="telegram"
SCRIPT_PATH="$(pwd)/telegram.py"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

echo "🛠 正在检查 python3..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ 未检测到 python3，正在安装..."
    apt update && apt install -y python3 python3-pip
fi

echo "📦 安装 telethon..."
pip3 install telethon backports.zoneinfo -q

echo "📝 正在创建 systemd 服务..."

sudo bash -c "cat > ${SERVICE_FILE}" <<EOF
[Unit]
Description=Telegram Nickname Auto Update
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${SCRIPT_PATH}
WorkingDirectory=$(pwd)
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 重载 systemd..."
sudo systemctl daemon-reload

echo "🚀 启动 Telegram 后台服务..."
sudo systemctl start ${APP_NAME}

echo "📌 设置开机自启..."
sudo systemctl enable ${APP_NAME}

echo ""
echo "🎉 已完成！脚本已自动后台运行，不会掉线！"
echo "🟢 查看运行状态："
echo "    sudo systemctl status ${APP_NAME}"
echo ""
echo "📜 查看实时日志："
echo "    sudo journalctl -fu ${APP_NAME}"
echo ""
echo "🔁 重启服务（更新代码后执行）："
echo "    sudo systemctl restart ${APP_NAME}"
echo ""
echo "✨ 现在你可以关闭终端，脚本会永久在后台运行。"