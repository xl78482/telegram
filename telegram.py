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

TIMEZONE = "Asia/Shanghai"

# 精确对齐每分钟 00 秒更新（毫秒级）
UPDATE_PRECISE = True

# 环境变量
api_id = int(os.getenv("TG_API_ID", "0"))
api_hash = os.getenv("TG_API_HASH", "")
bot_token = os.getenv("TG_BOT_TOKEN", "")
owner_id = int(os.getenv("TG_OWNER_ID", "0"))

# 安全检查
if not api_id or not api_hash:
    raise SystemExit("❌ TG_API_ID / TG_API_HASH 未设置")
if not bot_token:
    raise SystemExit("❌ TG_BOT_TOKEN 未设置")
if not owner_id:
    raise SystemExit("❌ TG_OWNER_ID 未设置")

# Telethon 初始化
client = TelegramClient("user_session", api_id, api_hash)
bot = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)


# ============================================
#                 日志系统（美化）
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format="✨ %(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("tg-clock")

def log(section, text):
    logger.info(f"[{section}] {text}")


# ============================================
#           高级正则（更安全、兼容更多昵称）
# ============================================

# 匹配日期 + 时间 + emoji（兼容各种奇怪情况）
TIME_TAIL_RE = re.compile(
    r"(20\d{2}-\d\d-\d\d \d\d:\d\d) [\u2600-\U0001FAFF]$"
)


# ============================================
#            全套表盘 emoji（24 级）
# ============================================

CLOCKS = [
    "🕛","🕧","🕐","🕜","🕑","🕝","🕒","🕞",
    "🕓","🕟","🕔","🕠","🕕","🕡","🕖","🕢",
    "🕗","🕣","🕘","🕤","🕙","🕥","🕚","🕦"
]

def clock_for(hour, minute):
    return CLOCKS[(hour % 12) * 2 + (1 if minute >= 30 else 0)]


# ============================================
#        精准对齐算法（误差补偿）
# ============================================

async def wait_until(target_time):
    """毫秒级精准等待，使更新卡点更准"""
    while True:
        now = datetime.now().timestamp()
        remain = target_time - now
        if remain <= 0:
            return
        # 根据剩余时间决定 sleep 精度（低功耗）
        await asyncio.sleep(min(remain, 0.2))


# ============================================
#           主昵称更新时间循环（旗舰版）
# ============================================

async def update_loop():
    tz = ZoneInfo(TIMEZONE)
    me = await client.get_me()
    base_name = me.first_name

    log("启动", "昵称更新循环已开始")

    while True:
        try:
            now = datetime.now(tz)
            next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)

            if UPDATE_PRECISE:
                # 精准对齐下一个分钟
                await wait_until(next_minute.timestamp())
            else:
                # 简单低精度 sleep
                await asyncio.sleep(60 - now.second)

            now = datetime.now(tz)
            time_str = now.strftime("%Y-%m-%d %H:%M")
            emoji = clock_for(now.hour, now.minute)

            # 获取当前昵称
            me = await client.get_me()
            raw = me.first_name or ""

            # 清理旧时间，提取纯原名
            cleaned = TIME_TAIL_RE.sub("", raw).strip()

            new_name = f"{cleaned} {time_str} {emoji}"

            # 更新昵称
            await client(UpdateProfileRequest(first_name=new_name))

            log("更新时间", f"{new_name}")

        except errors.FloodWaitError as e:
            log("限频", f"等待 {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            log("异常恢复", f"{e}")
            await asyncio.sleep(3)


# ============================================
#       Bot 扩展控制（全新增强版）
# ============================================

START_TIME = time.time()

@bot.on(events.NewMessage)
async def bot_handler(event):
    if event.sender_id != owner_id:
        return

    text = event.raw_text.strip().lower()

    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)

    if text == "/status":
        uptime = int(time.time() - START_TIME)
        msg = (
            f"🟢 *脚本状态*\n\n"
            f"⏱ 北京时间：`{now.strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"📡 运行时长：`{uptime}s`\n"
            f"⚙️ 精准更新：`{UPDATE_PRECISE}`\n"
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
#                 主入口
# ============================================

async def main():
    await client.start()
    asyncio.create_task(update_loop())
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())