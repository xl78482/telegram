#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import asyncio
import logging
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except:
    from backports.zoneinfo import ZoneInfo

from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest


# =====================================================
#             配置文件自动持久化（后台稳定核心）
# =====================================================

ENV_FILE = ".env"

def save_env(data: dict):
    with open(ENV_FILE, "w") as f:
        for k, v in data.items():
            f.write(f"{k}={v}\n")


def load_env():
    if not os.path.exists(ENV_FILE):
        return None
    cfg = {}
    with open(ENV_FILE, "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                cfg[k] = v
    return cfg


def check_config():
    """
    第一次运行需要输入并写入 .env，
    后台运行（无输入设备）禁止 input()。
    """
    # 若存在 .env → 直接读取
    if os.path.exists(ENV_FILE):
        return load_env()

    # 若是后台运行，则拒绝 input()
    if not os.isatty(0):
        print("❌ 后台运行检测到缺失配置文件 .env！")
        print("👉 请先前台运行一次： python3 telegram.py")
        exit(1)

    print("✨ 第一次运行，请填写配置信息（将写入 .env）")

    cfg = {}
    cfg['TG_API_ID'] = input("请输入你的 Telegram API ID: ").strip()
    cfg['TG_API_HASH'] = input("请输入你的 Telegram API Hash: ").strip()
    cfg['TG_BOT_TOKEN'] = input("请输入你的 Telegram Bot Token: ").strip()
    cfg['TG_OWNER_ID'] = input("请输入你的 Telegram 数字 ID: ").strip()

    save_env(cfg)
    print("🎉 配置保存完成，以后不会再出现输入提示！")

    return cfg


config = check_config()

api_id = int(config["TG_API_ID"])
api_hash = config["TG_API_HASH"]
bot_token = config["TG_BOT_TOKEN"]
owner_id = int(config["TG_OWNER_ID"])


# =====================================================
#                登录提示汉化
# =====================================================

def chinese_telethon_patches():
    """
    覆盖 Telethon 默认英文提示
    """
    from telethon.client.auth import AuthMethods

    AuthMethods._input_phone = lambda self: input("📱 请输入你的手机号（如 +86xxxxxxxx）： ")
    AuthMethods._input_code = lambda self, *args, **kwargs: input("🔑 请输入收到的验证码： ")
    AuthMethods._input_password = lambda self, *args, **kwargs: input("🔒 你的账号开启了二步验证，请输入密码： ")


chinese_telethon_patches()


# =====================================================
#                Telegram 客户端
# =====================================================

client = TelegramClient("user_session", api_id, api_hash)
bot = TelegramClient("bot_session", api_id, api_hash)


# =====================================================
#                     日志系统
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="✨ %(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("tg-clock")

def log(section, text):
    logger.info(f"[{section}] {text}")


# =====================================================
#              去除旧时间戳
# =====================================================

TIME_TAIL_RE = re.compile(r"(20\d{2}-\d\d-\d\d \d\d:\d\d) [\u2600-\U0001FAFF]$")


# =====================================================
#                     表盘 Emoji
# =====================================================

CLOCKS = [
    "🕛","🕧","🕐","🕜","🕑","🕝","🕒","🕞",
    "🕓","🕟","🕔","🕠","🕕","🕡","🕖","🕢",
    "🕗","🕣","🕘","🕤","🕙","🕥","🕚","🕦"
]

def clock_for(hour, minute):
    return CLOCKS[(hour % 12) * 2 + (1 if minute >= 30 else 0)]


# =====================================================
#                等待下一个整分钟
# =====================================================

async def wait_until(ts):
    while True:
        now = time.time()
        remain = ts - now
        if remain <= 0:
            return
        await asyncio.sleep(min(0.2, remain))


# =====================================================
#             ★★★ 主循环（自动更新昵称）★★★
# =====================================================

update_task = None
update_running = False

async def update_loop():
    global update_running
    update_running = True

    tz = ZoneInfo("Asia/Shanghai")
    await client.start()  # 登录

    log("启动", "昵称时间更新循环已开始")

    while update_running:
        try:
            now = datetime.now(tz)
            next_m = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
            await wait_until(next_m.timestamp())

            now = datetime.now(tz)
            time_str = now.strftime("%Y-%m-%d %H:%M")
            emoji = clock_for(now.hour, now.minute)

            me = await client.get_me()
            raw = me.first_name or ""
            cleaned = TIME_TAIL_RE.sub("", raw).strip()

            new_name = f"{cleaned} {time_str} {emoji}"
            await client(UpdateProfileRequest(first_name=new_name))

            log("更新时间", new_name)

        except errors.FloodWaitError as e:
            log("限频", f"等待 {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            log("异常", f"{e}")
            await asyncio.sleep(3)


def restart_update_loop():
    global update_task, update_running

    update_running = False
    if update_task:
        update_task.cancel()

    update_task = asyncio.create_task(update_loop())
    log("重启", "昵称更新循环已重启")


# =====================================================
#                    Bot 控制命令
# =====================================================

START_TIME = time.time()

@bot.on(events.NewMessage)
async def bot_handler(event):
    if event.sender_id != owner_id:
        return

    text = event.raw_text.strip().lower()
    tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(tz)

    if text == "/status":
        uptime = int(time.time() - START_TIME)
        await event.respond(
            f"🟢 *脚本运行状态*\n"
            f"⏰ 当前时间：`{now}`\n"
            f"⏱ 运行时长：`{uptime}s`\n"
            f"🔄 循环状态：`{'运行中' if update_running else '已停止'}`",
            parse_mode="markdown"
        )

    elif text == "/nickname":
        me = await client.get_me()
        await event.respond(f"👤 当前昵称：`{me.first_name}`", parse_mode="markdown")

    elif text == "/ping":
        await event.respond("🏓 Pong！脚本正常运行。")

    elif text == "/restart":
        await event.respond("♻️ 正在重启循环…")
        restart_update_loop()

    else:
        await event.respond(
            "📌 命令列表：\n"
            "/status - 查看运行状态\n"
            "/nickname - 昵称\n"
            "/ping - 测试连通性\n"
            "/restart - 重启时间循环"
        )


# =====================================================
#                    主入口（永不退出）
# =====================================================

async def main():
    await bot.start(bot_token=bot_token)
    restart_update_loop()
    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())