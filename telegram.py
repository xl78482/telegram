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
from telethon.tl.functions.account import UpdateProfileRequest

# ============================================
#                配置区域
# ============================================

def check_config():
    config = {}

    config['TG_API_ID'] = os.getenv("TG_API_ID") or input("请输入你的 Telegram API ID: ")
    config['TG_API_HASH'] = os.getenv("TG_API_HASH") or input("请输入你的 Telegram API Hash: ")
    config['TG_BOT_TOKEN'] = os.getenv("TG_BOT_TOKEN") or input("请输入你的 Telegram Bot Token: ")
    config['TG_OWNER_ID'] = os.getenv("TG_OWNER_ID") or input("请输入你的 Telegram 数字 ID: ")

    if not all(config.values()):
        raise SystemExit("配置不完整，请提供所有必需的配置信息。")

    return config


# 获取配置
config = check_config()

api_id = int(config['TG_API_ID'])
api_hash = config['TG_API_HASH']
bot_token = config['TG_BOT_TOKEN']
owner_id = int(config['TG_OWNER_ID'])

client = TelegramClient("user_session", api_id, api_hash)
bot = TelegramClient("bot_session", api_id, api_hash)


# ============================================
#                 日志系统
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format="✨ %(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("tg-clock")

def log(section, text):
    logger.info(f"[{section}] {text}")


# ============================================
#           高级正则（更安全）
# ============================================

TIME_TAIL_RE = re.compile(
    r"(20\d{2}-\d\d-\d\d \d\d:\d\d) [\u2600-\U0001FAFF]$"
)


# ============================================
#            表盘 emoji
# ============================================

CLOCKS = [
    "🕛","🕧","🕐","🕜","🕑","🕝","🕒","🕞",
    "🕓","🕟","🕔","🕠","🕕","🕡","🕖","🕢",
    "🕗","🕣","🕘","🕤","🕙","🕥","🕚","🕦"
]

def clock_for(hour, minute):
    return CLOCKS[(hour % 12) * 2 + (1 if minute >= 30 else 0)]


# ============================================
#        精准等待
# ============================================

async def wait_until(target_time):
    while True:
        now = datetime.now().timestamp()
        remain = target_time - now
        if remain <= 0:
            return
        await asyncio.sleep(min(remain, 0.2))


# ============================================
#         主昵称更新循环
# ============================================

async def update_loop():
    tz = ZoneInfo("Asia/Shanghai")

    await client.start()
    me = await client.get_me()
    base_name = me.first_name

    log("启动", "昵称更新循环已开始")

    while True:
        try:
            now = datetime.now(tz)
            next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)

            await wait_until(next_minute.timestamp())

            now = datetime.now(tz)
            time_str = now.strftime("%Y-%m-%d %H:%M")
            emoji = clock_for(now.hour, now.minute)

            me = await client.get_me()
            raw = me.first_name or ""
            cleaned = TIME_TAIL_RE.sub("", raw).strip()

            new_name = f"{cleaned} {time_str} {emoji}"

            await client(UpdateProfileRequest(first_name=new_name))

            log("更新时间", f"{new_name}")

        except errors.FloodWaitError as e:
            log("限频", f"等待 {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            log("异常恢复", f"{e}")
            await asyncio.sleep(3)



# ============================================
#         Bot 控制模块
# ============================================

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
        msg = (
            f"🟢 *脚本状态*\n\n"
            f"⏱ 北京时间：`{now.strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"📡 运行时长：`{uptime}s`\n"
        )
        await event.respond(msg, parse_mode="markdown")

    elif text == "/nickname":
        me = await client.get_me()
        await event.respond(f"👤 当前昵称：`{me.first_name}`", parse_mode="markdown")

    elif text == "/ping":
        await event.respond("🏓 Pong！脚本正常运行中。")

    elif text == "/restart":
        await event.respond("♻️ 正在重启更新循环…")
        asyncio.create_task(update_loop())

    else:
        await event.respond(
            "📌 命令列表：\n"
            "/status - 查看状态\n"
            "/nickname - 查看当前昵称\n"
            "/ping - 测试脚本响应\n"
            "/restart - 重启更新循环"
        )


# ============================================
#                 主入口（已修复）
# ============================================

async def main():
    await bot.start(bot_token=bot_token)

    asyncio.create_task(update_loop())

    await bot.run_until_disconnected()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())