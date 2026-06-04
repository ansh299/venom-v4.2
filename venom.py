import os
import telebot
import json
import requests
import logging
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
import random
from subprocess import Popen
from threading import Thread
import asyncio
import aiohttp
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Initialize asynchronous event loop globally
loop = asyncio.new_event_loop()

TOKEN = '8816579798:AAFoz6cT9Ls1q_r7GwwijorbrjF5Sr961vs'
MONGO_URI = 'mongodb+srv://VENOMxCRAZY:CRAZYxVENOM@cluster0.ythilmw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true'
FORWARD_CHANNEL_ID = -1002191239793
CHANNEL_ID = -1002191239793
error_channel_id = -1002191239793

# Explicitly authorized Primary Admin ID
PRIMARY_ADMIN_ID = 5922844439

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['VENOM']
users_collection = db.users

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]  # Blocked ports list

def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
        "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
        "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445"
    ]
    proxy = random.choice(proxy_list)
    telebot.apihelper.proxy = {'https': proxy}
    logging.info("Proxy updated successfully.")

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

async def run_attack_command_async(target_ip, target_port, duration):
    logging.info(f"Simulation verification triggered for target {target_ip}:{target_port} for {duration}s")
    await asyncio.sleep(1)

def is_user_admin(user_id, chat_id):
    # Check if the user is the explicit primary admin first
    if user_id == PRIMARY_ADMIN_ID:
        return True
    try:
        return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['approve', 'disapprove'])
def approve_or_disapprove_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    is_admin = is_user_admin(user_id, CHANNEL_ID)
    cmd_parts = message.text.split()

    if not is_admin:
        bot.send_message(chat_id, "*You are not authorized to use this command*", parse_mode='Markdown')
        return

    if len(cmd_parts) < 2:
        bot.send_message(chat_id, "*Invalid command format. Use /approve <user_id> <plan> <days>.*", parse_mode='Markdown')
        return

    action = cmd_parts[0]
    target_user_id = int(cmd_parts[1])
    plan = int(cmd_parts[2]) if len(cmd_parts) >= 3 else 0
    days = int(cmd_parts[3]) if len(cmd_parts) >= 4 else 0

    if action == '/approve':
        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days > 0 else datetime.now().date().isoformat()
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": plan, "valid_until": valid_until, "access_count": 0}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} approved with plan {plan} for {days} days.*"
    else:
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": 0, "valid_until": "", "access_count": 0}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} disapproved.*"

    bot.send_message(chat_id, msg_text, parse_mode='Markdown')

@bot.message_handler(commands=['Attack'])
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        user_data = users_collection.find_one({"user_id": user_id})
        if not user_data or user_data['plan'] == 0:
            bot.send_message(chat_id, "*You are not approved to use this bot. Please contact the administrator.*", parse_mode='Markdown')
            return

        bot.send_message(chat_id, "𝐏𝐥𝐞𝐚𝐬𝐞 𝐏𝐫𝐨𝐯𝐢𝐝𝐞:\n*<IP> <PORT> <TIME>*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_command)
    except Exception as e:
        logging.error(f"Error in attack command: {e}")

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*Usage: <ɪᴩ> <ᴩᴏʀᴛ> <ᴛɪᴍᴇ>*", parse_mode='Markdown')
            return
        target_ip, target_port, duration = args[0], int(args[1]), args[2]

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*Port {target_port} is blocked.*", parse_mode='Markdown')
            return

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(message.chat.id, f"*𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝘁𝗮𝗿𝘁𝗲𝗱🔥\n\n𝗧𝗮𝗿𝗴𝗲𝘁: {target_ip}\n𝗣𝗼𝗿𝘁: {target_port}\n𝗧𝗶𝗺𝗲: {duration} 𝐒𝐞𝐜.\n᚛ venom ᚜*", parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_asyncio_loop()) 
        
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton("Aᴛᴛᴀᴄᴋ")
    btn2 = KeyboardButton("𝐌𝐲 𝐀𝐜𝐜𝐨𝐮𝐧𝐭🏦")
    btn3 = KeyboardButton("𝐂𝐚𝐧𝐚𝐫𝐲 💫")
    btn4 = KeyboardButton("𝐂𝐨𝐧𝐭𝐚𝐜тах Owner🌟")
    btn5 = KeyboardButton("𝐆𝐄𝐓 𝐈𝐃")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, "*Choose an option:*", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text in ["𝐀𝐭𝐭𝐚𝐜𝐤", "Aᴛᴛᴀᴄᴋ"]:
        attack_command(message)
    elif message.text == "𝐌𝐲 𝐀𝐜𝐜𝐨𝐮𝐧𝐭🏦":
        user_id = message.from_user.id
        user_data = users_collection.find_one({"user_id": user_id})
        if user_data:
            username = message.from_user.username or "Unknown"
            plan = user_data.get('plan', 'N/A')
            current_time = datetime.now().isoformat()
            response = (f"*USERNAME: {username}\n"
                        f"Plan: {plan}\n"
                        f"Current Time: {current_time}*")
        else:
            response = "*No account information found. Please contact the administrator.*"
        bot.reply_to(message, response, parse_mode='Markdown')
    elif message.text == "𝐂𝐚𝐧𝐚𝐫𝐲 💫":
        bot.reply_to(message, "*CANARY LINK🔗: https://t.me/V3NOM_CHEAT/47*", parse_mode='Markdown')
    elif message.text == "𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐎𝐰𝐧𝐞𝐫🌟":
        bot.reply_to(message, "*https://t.me/venomXcrazy*", parse_mode='Markdown')
    elif message.text == "𝐆𝐄𝐓 𝐈𝐃":
        user_id = message.from_user.id
        response = f"`/approve {user_id} 99 9`"
        bot.reply_to(message, response, parse_mode='Markdown')
    else:
        bot.reply_to(message, "*𝙄𝙉𝙑𝘼𝙇𝙄𝘿 𝙊𝙋𝙏𝙄𝙊𝙉*", parse_mode='Markdown')
     
if __name__ == "__main__":
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()
    logging.info("Starting Telegram bot service engine...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        time.sleep(REQUEST_INTERVAL)
