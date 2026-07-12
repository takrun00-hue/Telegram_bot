import asyncio
import random
import logging
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    FloodWaitError, ChatWriteForbiddenError, UserBannedInChannelError,
    ChannelPrivateError, SlowModeWaitError, PeerFloodError,
    UsernameInvalidError
)
from messages import AFGHANCOIN_MSG, AFGHANFOLLOWERS_MSG

API_ID     = int(os.environ["TG_API_ID"])
API_HASH   = os.environ["TG_API_HASH"]
TG_SESSION = os.environ["TG_SESSION"]
ADMIN_ID   = int(os.environ.get("ADMIN_CHAT_ID", "7993801735"))
DELAY      = int(os.environ.get("DELAY_SECONDS", "60"))
POST_HOUR  = int(os.environ.get("POST_HOUR", "10"))

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

def load_groups():
    with open("groups.txt", "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]

async def send_ad(client, group, message):
    try:
        await client.send_message(group, message, parse_mode="md", link_preview=False)
        log.info(f"✅ {group}")
        return True
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 10)
        return False
    except SlowModeWaitError as e:
        await asyncio.sleep(e.seconds + 5)
        return False
    except PeerFloodError:
        await asyncio.sleep(3600)
        return False
    except (ChatWriteForbiddenError, UserBannedInChannelError, ChannelPrivateError, UsernameInvalidError):
        log.warning(f"❌ {group}")
        return False
    except Exception as e:
        log.error(f"❌ {group}: {e}")
        return False

async def run_campaign(client, message, label):
    groups = load_groups()
    ok = fail = 0
    for i, group in enumerate(groups, 1):
        result = await send_ad(client, group, message)
        if result: ok += 1
        else: fail += 1
        await asyncio.sleep(DELAY + random.randint(5, 25))
    return ok, fail

async def notify(client, text):
    try:
        await client.send_message(ADMIN_ID, text, parse_mode="md")
    except:
        pass

async def daily_job(client):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    await notify(client, f"🤖 ربات شروع شد\n⏰ {now}")
    ok1, fail1 = await run_campaign(client, AFGHANCOIN_MSG, "AfghanCoins")
    await asyncio.sleep(120)
    ok2, fail2 = await run_campaign(client, AFGHANFOLLOWERS_MSG, "AfghanFollowers")
    await notify(client, f"📊 گزارش\n🪙 AfghanCoins: ✅{ok1} ❌{fail1}\n📈 AfghanFollowers: ✅{ok2} ❌{fail2}")

async def main():
    client = TelegramClient(StringSession(TG_SESSION), API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        log.error("❌ Session نامعتبر!")
        return
    me = await client.get_me()
    log.info(f"🤖 لاگین: {me.first_name}")
    ran_today = False
    while True:
        now = datetime.now()
        if now.hour == POST_HOUR and now.minute == 0 and not ran_today:
            await daily_job(client)
            ran_today = True
        if now.hour == 0 and now.minute == 0:
            ran_today = False
        await asyncio.sleep(30)

asyncio.run(main())
