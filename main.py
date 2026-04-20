# import discord
# from discord.ext import commands, tasks
# import requests
# import os
# import time
# import json
# import datetime
# from flask import Flask
# from threading import Thread

# # =======================
# # 🌐 WEB SERVER (ANTI-SLEEP)
# # =======================
# app = Flask('')

# @app.route('/')
# def home():
#     return "Multi-Function Bot is Online!"

# def run_web():
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port)

# def keep_alive():
#     t = Thread(target=run_web)
#     t.daemon = True
#     t.start()

# # =======================
# # 🔑 CONFIG & DISCORD SETUP
# # =======================
# TOKEN = os.getenv("DISCORD_TOKEN")
# WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# VC_CHANNEL_ID = 1486323364891987998
# REPORT_CHANNEL_ID = 1400530676218073280
# TARGET_USERS = [697788108611125399,1290655706877530148]
# NOTIFY_ID = 1005357318281641994

# intents = discord.Intents.default()
# intents.presences = True
# intents.members = True
# intents.message_content = True
# intents.voice_states = True

# bot = commands.Bot(command_prefix="!", intents=intents)

# # 📦 CACHE SYSTEM
# avatar_cache = {}
# status_cache = {}
# spotify_cache = {}
# start_time = time.time()

# def send_webhook(payload):
#     if not WEBHOOK_URL:
#         print("⚠️ WEBHOOK_URL is missing!")
#         return
#     try:
#         requests.post(WEBHOOK_URL, json=payload, timeout=5)
#     except Exception as e:
#         print(f"❌ Webhook Error: {e}")

# # =======================
# # 🎤 VC GUARDIAN FUNCTIONS
# # =======================
# async def join_vc():
#     channel = bot.get_channel(VC_CHANNEL_ID)
#     if not channel:
#         print(f"⚠️ Could not find VC Channel: {VC_CHANNEL_ID}")
#         return
    
#     # ตรวจสอบว่าบอทอยู่ในห้องหรือยัง ถ้ายังให้ connect
#     if not bot.voice_clients:
#         try:
#             vc = await channel.connect()
#             # ถ้ามีไฟล์เสียงเงียบให้เล่นเพื่อรักษาสถานะ แต่ถ้าไม่มีก็ไม่เป็นไร
#             if os.path.exists("silence.mp3"):
#                 vc.play(discord.FFmpegPCMAudio("silence.mp3"))
#             print(f"✅ Joined VC: {channel.name}")
#         except Exception as e:
#             print(f"VC Join Error: {e}")

# @tasks.loop(seconds=30)
# async def vc_guard():
#     # ตรวจสอบทุก 30 วินาทีว่าบอทยังอยู่ในห้องไหม
#     vc = discord.utils.get(bot.voice_clients)
#     if not vc or not vc.is_connected():
#         await join_vc()
# # =======================
# # 📡 TRACKER EVENTS
# # =======================

# @bot.event
# async def on_ready():
#     print(f'✅ Logged in as {bot.user}')
#     if not vc_guard.is_running(): vc_guard.start()
#     if not hourly_report.is_running(): hourly_report.start()
#     await join_vc()
    
#     # Initial Cache
#     for guild in bot.guilds:
#         for member in guild.members:
#             if member.id in TARGET_USERS:
#                 avatar_cache[member.id] = str(member.display_avatar.url)
#                 status_cache[member.id] = str(member.status)

# @bot.event
# async def on_presence_update(before, after):
#     if after.id not in TARGET_USERS: return

#     # --- Status Change ---
#     new_status = str(after.status)
#     if status_cache.get(after.id) != new_status:
#         status_cache[after.id] = new_status
#         status_map = {"online": "🟢 Online", "idle": "🌙 Idle", "dnd": "⛔ DND", "offline": "⚫ Offline"}
#         color_map = {"online": 0x00ff00, "idle": 0xFFD700, "dnd": 0xFF0000, "offline": 0x808080}
        
#         embed = {
#             "title": "📢 Status Change!",
#             "description": f"**{after.name}** เปลี่ยนสถานะเป็น **{status_map.get(new_status, new_status)}**",
#             "color": color_map.get(new_status, 0x808080),
#             "timestamp": discord.utils.utcnow().isoformat()
#         }
#         send_webhook({"content": f"<@{NOTIFY_ID}>", "embeds": [embed]})

#     # --- Spotify Tracker ---
#     current_spotify = next((act for act in after.activities if isinstance(act, discord.Spotify)), None)
#     if current_spotify:
#         song_id = f"{current_spotify.title}-{current_spotify.artist}"
#         if spotify_cache.get(after.id) != song_id:
#             spotify_cache[after.id] = song_id
#             embed = {
#                 "author": {"name": "Spotify Tracking", "icon_url": "https://cdn-icons-png.flaticon.com/512/174/174872.png"},
#                 "title": f"🎧 {after.name} กำลังฟังเพลง",
#                 "color": 0x1DB954,
#                 "thumbnail": {"url": current_spotify.album_cover_url},
#                 "fields": [
#                     {"name": "🎵 เพลง", "value": f"**{current_spotify.title}**", "inline": False},
#                     {"name": "👤 ศิลปิน", "value": current_spotify.artist, "inline": True},
#                     {"name": "💿 อัลบั้ม", "value": current_spotify.album, "inline": True}
#                 ],
#                 "footer": {"text": "Spotify Real-time Monitor"},
#                 "timestamp": discord.utils.utcnow().isoformat()
#             }
#             send_webhook({"content": f"<@{NOTIFY_ID}>", "embeds": [embed]})

# @bot.event
# async def on_user_update(before, after):
#     """ ตรวจสอบการเปลี่ยนรูปโปรไฟล์ (Global) """
#     if after.id not in TARGET_USERS: return

#     old_avatar = avatar_cache.get(after.id)
#     new_avatar = str(after.display_avatar.url)

#     if old_avatar != new_avatar:
#         avatar_cache[after.id] = new_avatar
#         embed = {
#             "title": "🖼️ New Avatar Detected!",
#             "description": f"**{after.name}** ได้ทำการเปลี่ยนรูปโปรไฟล์ใหม่",
#             "color": 0x9b59b6,
#             "image": {"url": new_avatar},
#             "thumbnail": {"url": old_avatar} if old_avatar else {},
#             "fields": [
#                 {"name": "👤 ผู้ใช้", "value": f"{after.name}#{after.discriminator}", "inline": True},
#                 {"name": "🆔 ID", "value": str(after.id), "inline": True}
#             ],
#             "footer": {"text": "รูปเล็กด้านขวาคือรูปเก่า | รูปใหญ่คือรูปใหม่"},
#             "timestamp": discord.utils.utcnow().isoformat()
#         }
#         send_webhook({"content": f"<@{NOTIFY_ID}>", "embeds": [embed]})

# @bot.event
# async def on_voice_state_update(member, before, after):
#     if member.id in TARGET_USERS:
#         if before.channel != after.channel:
#             msg = ""
#             color = 0x000000
#             if not before.channel:
#                 msg = f"📥 **{member.name}** เข้าห้อง **{after.channel.name}**"
#                 color = 0x2ecc71
#             elif not after.channel:
#                 msg = f"📤 **{member.name}** ออกจากห้อง **{before.channel.name}**"
#                 color = 0xe74c3c
#             else:
#                 msg = f"🔁 **{member.name}** ย้ายห้อง ➜ **{after.channel.name}**"
#                 color = 0xf1c40f
            
#             if msg:
#                 embed = {"description": msg, "color": color, "timestamp": discord.utils.utcnow().isoformat()}
#                 send_webhook({"content": f"<@{NOTIFY_ID}>", "embeds": [embed]})
    
#     if member.id == bot.user.id and after.channel is None:
#         await join_vc()

# @bot.command()
# async def uptime(ctx):
#     uptime_sec = int(time.time() - start_time)
#     hours, minutes = uptime_sec // 3600, (uptime_sec % 3600) // 60
#     await ctx.send(f"🕒 **Bot Uptime:** {hours}h {minutes}m")

# # =======================
# # 🚀 RUN BOT
# # =======================
# if __name__ == "__main__":
#     keep_alive()
#     if not TOKEN:
#         print("❌ CRITICAL ERROR: DISCORD_TOKEN is not set!")
#     else:
#         try:
#             bot.run(TOKEN)
#         except Exception as e:
#             print(f"❌ Critical Startup Error: {e}")



import discord
from discord.ext import commands, tasks
import requests
import os
import time
import json
import datetime
from flask import Flask
from threading import Thread

# =======================
# 🌐 WEB SERVER (ANTI-SLEEP)
# =======================
app = Flask('')

@app.route('/')
def home():
    return "Multi-Function Bot is Online!"

def run_web():
    # แก้ไข port ให้รองรับการรันบนหลาย Platform
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# =======================
# 🔑 CONFIG & DISCORD SETUP
# =======================
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

VC_CHANNEL_ID = 1486323364891987998
REPORT_CHANNEL_ID = 1400530676218073280
TARGET_USERS = [697788108611125399, 1290655706877530148, 1005357318281641994]
NOTIFY_ID = 1005357318281641994

# ตั้งค่า Intents (สำคัญ: ต้องเปิดใน Developer Portal ด้วย)
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 📦 CACHE SYSTEM
avatar_cache = {}
status_cache = {}
spotify_cache = {}
start_time = time.time()

def send_webhook(payload):
    if not WEBHOOK_URL or not WEBHOOK_URL.startswith("http"):
        print("⚠️ Webhook URL ไม่ถูกต้อง หรือไม่ได้ตั้งค่า")
        return
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"❌ Webhook Error: {e}")

# =======================
# 🎤 VC GUARDIAN (ระบบสิงห้อง)
# =======================
async def join_vc():
    try:
        channel = bot.get_channel(VC_CHANNEL_ID)
        if not channel:
            # ลอง fetch กรณี get_channel หาไม่เจอใน cache
            try:
                channel = await bot.fetch_channel(VC_CHANNEL_ID)
            except:
                print(f"⚠️ ไม่พบห้อง VC ID: {VC_CHANNEL_ID}")
                return
        
        # ตรวจสอบว่าบอทเชื่อมต่ออยู่หรือไม่
        guild = channel.guild
        vc = discord.utils.get(bot.voice_clients, guild=guild)
        
        if not vc or not vc.is_connected():
            await channel.connect(reconnect=True, timeout=20.0)
            print(f"✅ บอทสิงเข้าห้อง: {channel.name}")
        elif vc.channel.id != VC_CHANNEL_ID:
            await vc.move_to(channel)
            print(f"🔁 ย้ายบอทไปห้อง: {channel.name}")
            
    except Exception as e:
        print(f"❌ VC Join Error: {e}")

@tasks.loop(seconds=20)
async def vc_guard():
    await join_vc()

# =======================
# 📡 TRACKER & COMMANDS
# =======================

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    if not vc_guard.is_running(): 
        vc_guard.start()
    await join_vc()
    
    # Initial Cache สำหรับ Target Users
    for guild in bot.guilds:
        for member in guild.members:
            if member.id in TARGET_USERS:
                avatar_cache[member.id] = str(member.display_avatar.url)
                status_cache[member.id] = str(member.status)

@bot.command()
async def sp(ctx):
    uptime_sec = int(time.time() - start_time)
    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    minutes = (uptime_sec % 3600) // 60
    
    ping = round(bot.latency * 1000)
    
    if ping < 150:
        stability = "🟢 ต่ำมาก (เสถียรมาก)"
    elif ping < 350:
        stability = "🟡 ปานกลาง (อาจมีกระตุก)"
    else:
        stability = "🔴 สูง (เน็ตไม่คงที่)"

    embed = discord.Embed(title="📊 ระบบตรวจสอบสถานะบอท", color=0x3498db)
    embed.add_field(name="⏳ ระยะเวลาที่ออนไลน์", value=f"**{days}** วัน **{hours}** ชม. **{minutes}** นาที", inline=False)
    embed.add_field(name="📶 ค่าปิง (Latency)", value=f"{ping} ms", inline=True)
    embed.add_field(name="📉 โอกาสหลุด", value=stability, inline=True)
    
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    status_text = f"✅ สิงอยู่ที่: {vc.channel.name}" if vc and vc.is_connected() else "❌ หลุดจากห้อง (กำลังกลับเข้า)"
    embed.add_field(name="🎙️ สถานะ Voice", value=status_text, inline=False)
    
    embed.set_footer(text="เช็คสถานะ ณ เวลา")
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.event
async def on_presence_update(before, after):
    if after.id not in TARGET_USERS: return
    
    new_status = str(after.status)
    if status_cache.get(after.id) != new_status:
        status_cache[after.id] = new_status
        status_map = {"online": "🟢 Online", "idle": "🌙 Idle", "dnd": "⛔ DND", "offline": "⚫ Offline"}
        color_map = {"online": 0x00ff00, "idle": 0xFFD700, "dnd": 0xFF0000, "offline": 0x808080}
        
        embed = {
            "title": "📢 Status Change!", 
            "description": f"**{after.name}** เปลี่ยนเป็น **{status_map.get(new_status, new_status)}**", 
            "color": color_map.get(new_status, 0x808080), 
            "timestamp": discord.utils.utcnow().isoformat()
        }
        send_webhook({"content": f"<@{NOTIFY_ID}>", "embeds": [embed]})

@bot.event
async def on_user_update(before, after):
    if after.id not in TARGET_USERS: return

    old_avatar = avatar_cache.get(after.id)
    new_avatar = str(after.display_avatar.url)

    if old_avatar != new_avatar:
        avatar_cache[after.id] = new_avatar
        embed = {
            "title": "🖼️ New Avatar Detected!",
            "description": f"**{after.name}** ได้ทำการเปลี่ยนรูปโปรไฟล์ใหม่",
            "color": 0x9b59b6,
            "image": {"url": new_avatar},
            "thumbnail": {"url": old_avatar} if old_avatar else {},
            "fields": [
                {"name": "👤 ผู้ใช้", "value": f"{after.name}", "inline": True},
                {"name": "🆔 ID", "value": str(after.id), "inline": True}
            ],
            "footer": {"text": "รูปเล็กคือรูปเก่า | รูปใหญ่คือรูปใหม่"},
            "timestamp": discord.utils.utcnow().isoformat()
        }
        send_webhook({"content": f"<@{NOTIFY_ID}>", "embeds": [embed]})

@bot.event
async def on_voice_state_update(member, before, after):
    # บอทโดนเตะ หรือห้องไม่มีใครอยู่ ให้พยายามกลับเข้าห้อง
    if member.id == bot.user.id and after.channel is None:
        await join_vc()
    
    # แจ้งเตือนคนเข้า-ออกห้อง VC
    if member.id in TARGET_USERS and before.channel != after.channel:
        msg = ""
        color = 0x000000
        if not before.channel:
            msg = f"📥 **{member.name}** เข้าห้อง **{after.channel.name}**"
            color = 0x2ecc71
        elif not after.channel:
            msg = f"📤 **{member.name}** ออกจากห้อง **{before.channel.name}**"
            color = 0xe74c3c
        else:
            msg = f"🔁 **{member.name}** ย้ายห้อง ➜ **{after.channel.name}**"
            color = 0xf1c40f
            
        if msg:
            embed = {"description": msg, "color": color, "timestamp": discord.utils.utcnow().isoformat()}
            send_webhook({"content": f"<@{NOTIFY_ID}>", "embeds": [embed]})

# =======================
# 🚀 RUN BOT
# =======================
if __name__ == "__main__":
    keep_alive()
    if TOKEN:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"❌ Startup Error: {e}\n(ตรวจสอบว่าได้เปิด Intents ใน Discord Developer Portal หรือยัง?)")
    else:
        print("❌ ไม่พบ DISCORD_TOKEN ใน Environment Variables")
