#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================
#     缔造者时间同步系统（Cloud + Ultra-Time 混合版 · 最终增强版）
# ============================================================

import os
import sys
import json
import asyncio
import logging
import re
import aiohttp
import time
from datetime import datetime, timedelta

from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.network.connection import ConnectionTcpFull
from telethon.tl.functions.account import UpdateProfileRequest

# ------------------------------------------------------------
#                强制系统时区为北京时间
# ------------------------------------------------------------
os.environ["TZ"] = "Asia/Shanghai"
try:
    time.tzset()
except:
    pass

# ------------------------------------------------------------
#        Cloud-Time API（主源：淘宝 / 备源：京东）
# ------------------------------------------------------------
API_TAOBAO = "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"
API_JD     = "https://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5"

# ============================================================
#     ★ Ultra-Time 超级精准时间获取（核心升级）
# ============================================================

last_good_ts = None      # 真实毫秒时间缓存
smooth_ts = None         # 平滑时间链
ALPHA = 0.25             # 平滑系数（越小越稳定）


async def get_cloud_time():
    """
    双源获取时间 + RTT 半程延迟补偿 + 平滑算法（Ultra-Time）
    """
    global last_good_ts, smooth_ts

    ts_list = []

    # ====== 双源采样 ======
    for api in (API_TAOBAO, API_JD):
        try:
            t1 = time.perf_counter()

            async with aiohttp.ClientSession() as session:
                async with session.get(api, timeout=1.5) as resp:
                    data = await resp.json()

            t2 = time.perf_counter()
            rtt = (t2 - t1) * 1000 / 2     # 单边 RTT

            # 淘宝格式
            if "data" in data and "t" in data["data"]:
                ts = int(data["data"]["t"]) + rtt

            # 京东格式
            elif "currentTime2" in data:
                ts = int(data["currentTime2"]) + rtt

            else:
                continue

            ts_list.append(ts)

        except:
            continue

    # ====== 判断是否完全失败 ======
    if not ts_list:
        if last_good_ts:
            last_good_ts += 250     # 回退链向前推进
            return datetime.fromtimestamp(last_good_ts / 1000)
        return datetime.now()

    # ====== 多点采样取平均 ======
    raw_ts = sum(ts_list) / len(ts_list)

    # ====== 平滑算法 ======
    if smooth_ts is None:
        smooth_ts = raw_ts
    else:
        smooth_ts = ALPHA * raw_ts + (1 - ALPHA) * smooth_ts

    last_good_ts = smooth_ts

    return datetime.fromtimestamp(smooth_ts / 1000)



# ------------------------------------------------------------
#               日志系统（精简）
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="✨ %(asctime)s | %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("dizaozhe")


# ------------------------------------------------------------
#               ★ 强制使用 DC4（删除 DC2）★
# ------------------------------------------------------------
DC4_IP = "149.154.167.91"
DC4_PORT = 443

class ForceDC4(ConnectionTcpFull):
    host = DC4_IP
    port = DC4_PORT



# ------------------------------------------------------------
#               账号文件
# ------------------------------------------------------------
ACC_FILE = "account.json"

def save_acc(session, api_id, api_hash):
    json.dump(
        {"session": session, "api_id": api_id, "api_hash": api_hash},
        open(ACC_FILE, "w"),
        indent=2,
        ensure_ascii=False
    )

def load_acc():
    if os.path.exists(ACC_FILE):
        return json.load(open(ACC_FILE, "r"))
    return None



# ------------------------------------------------------------
#         ★ 中文账号登录流程（强制提示 + DC4）★
# ------------------------------------------------------------
async def login_process():

    print("\n====== 缔造者时间同步系统 ======\n")

    cfg = load_acc()
    if cfg:
        print("检测到已有账号配置：")
        print(f"API_ID   ：{cfg['api_id']}")
        print(f"API_HASH ：{cfg['api_hash'][:6]}****\n")
        print("1 = 使用现有配置")
        print("2 = 重新绑定账号\n")

        c = input("请选择 1 或 2： ").strip()
        if c == "1":
            client = TelegramClient(
                StringSession(cfg["session"]),
                cfg["api_id"],
                cfg["api_hash"],
                connection=ForceDC4
            )
            await client.connect()
            return client
        
        print("⚠️ 重新绑定，将删除旧配置\n")
        os.remove(ACC_FILE)

    # 绑定新账号
    api_id = int(input("🔢 API_ID： "))
    api_hash = input("🧬 API_HASH： ")
    phone = input("📱 手机号（例如 +86138xxxxxx）： ")

    client = TelegramClient(StringSession(), api_id, api_hash, connection=ForceDC4)
    await client.connect()

    print("⏳ 正在发送验证码…")
    await client.send_code_request(phone)

    code = input("🔑 请输入验证码： ")

    try:
        await client.sign_in(phone, code)
    except errors.SessionPasswordNeededError:
        pwd = input("🔒 二步验证密码： ")
        await client.sign_in(password=pwd)

    save_acc(client.session.save(), api_id, api_hash)
    print("🎉 账号绑定成功！\n")

    return client



# ------------------------------------------------------------
#               24 时钟图标
# ------------------------------------------------------------
CLOCKS = [
    "🕛","🕧","🕐","🕜","🕑","🕝","🕒","🕞",
    "🕓","🕟","🕔","🕠","🕕","🕡","🕖","🕢",
    "🕗","🕣","🕘","🕤","🕙","🕥","🕚","🕦"
]

def get_clock(h, m):
    return CLOCKS[(h * 2 + (1 if m >= 30 else 0)) % 24]



# ============================================================
#     ★ 修复叠加（终极 Regex，吞噬所有旧时间格式）
# ============================================================
TAIL_RE = re.compile(
    r"(?:\s*[｜│]?\s*\d{4}-\d\d-\d\d\s\d\d:\d\d\s[\U0001F550-\U0001F567])$"
)

def strip_old(name):
    return TAIL_RE.sub("", name).strip()



# ============================================================
#     ★ 59 秒更新下一分钟（绝对精准，不偏差）
# ============================================================
async def update_loop(client):

    print("⏳ 开始同步昵称（缔造者时间同步系统）…\n")

    while True:

        now = await get_cloud_time()

        # 更精准触发：59 秒 ±0.5s
        if 58.5 <= now.second + now.microsecond/1e6 <= 59.5:

            me = await client.get_me()
            base = strip_old(me.first_name or "")

            # 下一分钟（关键升级）
            next_min = now + timedelta(minutes=1)
            next_min = next_min.replace(second=0, microsecond=0)

            new_time = next_min.strftime("%Y-%m-%d %H:%M")
            icon = get_clock(next_min.hour, next_min.minute)

            # 去掉竖杠，只保留一个空格
            new_name = f"{base} {new_time} {icon}"

            try:
                await client(UpdateProfileRequest(first_name=new_name))
                print(f"✨ 更新成功 → {new_name}")
            except Exception as e:
                print(f"❌ 更新失败：{e}")

            await asyncio.sleep(1)

        await asyncio.sleep(0.25)



# ------------------------------------------------------------
#                  主入口
# ------------------------------------------------------------
async def main():

    print("\n🚀 缔造者时间同步系统🚀  启动中…\n")

    client = await login_process()
    me = await client.get_me()

    print(f"👤 登录成功：{me.first_name}\n")

    await update_loop(client)



if __name__ == "__main__":
    asyncio.run(main())
