import telebot
import requests
import random
import time
import threading
import json
import os
import logging
from telebot import types

API_TOKEN = '7630980959:AAHVeedkDDYeFSam3pm9OSnlpc-WutMXlCE'  # Replace with your bot's token
bot = telebot.TeleBot(API_TOKEN)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

owner_id = 6590816421  # Owner's user ID
owner_username = '@Nonsecularmuslim'

# Admin's proxies (to be used as defaults)
admin_proxies = [
    "103.49.202.252:80", "103.145.68.202:8181", "106.15.207.21:9530",
    "156.233.87.217:3128", "156.228.84.179:3128", "154.213.204.103:3128",
    # Add your own proxy here
    "YOUR_PROXY:PORT",  # Add your specific proxy here
]

# Data structures to store user data
user_data = {}
max_daily_checks = 500
premium_checks = 10000  # Premium daily checks
log_file = 'bot_log.txt'  # File for logging
service_endpoints = {
    "Netflix": "https://www.netflix.com",
    "Spotify": "https://www.spotify.com",
    "Hotmail": "https://www.hotmail.com",
    "Disney": "https://www.disney.com",
    "TradingView": "https://www.tradingview.com",
    "Crunchyroll": "https://www.crunchyroll.com",
}

# Initialize log file
if not os.path.isfile(log_file):
    with open(log_file, 'w') as f:
        f.write("Bot Log Initialized\n")

# Helper Functions
def log_to_file(message):
    with open(log_file, 'a') as f:
        f.write(f"{message}\n")

def load_user_data():
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as f:
            return json.load(f)
    return {}

def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)

def initialize_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "checks_today": 0,
            "proxies": [],
            "is_premium": False,
            "service_checks": {service: 0 for service in service_endpoints.keys()},
            "daily_limits": {service: max_daily_checks for service in service_endpoints.keys()}
        }
        save_user_data()

def reset_daily_checks():
    for user_id in user_data.keys():
        user_data[user_id]["checks_today"] = 0
        for service in service_endpoints.keys():
            user_data[user_id]["service_checks"][service] = 0
    save_user_data()

# Welcome Message
def send_welcome_message(message):
    welcome_text = (
        "🎉 Welcome to the Multi-Service Checker Bot! 🎉\n\n"
        "This bot allows you to check your accounts for various streaming services.\n"
        "Here's how to use it:\n"
        "1. Send your account details in the format:\n"
        "service:email:password\n\n"
        "2. Make sure to join our private channel and the @f2wnet channel for full access.\n\n"
        "Let's get started! 🚀"
    )
    bot.send_video(message.chat.id, "https://t.me/F2W_HACKEr/2", caption=welcome_text)

# Commands Handlers
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    initialize_user(user_id)
    send_welcome_message(message)

@bot.message_handler(commands=['checkNetflix'])
def check_netflix(message):
    user_id = message.from_user.id
    initialize_user(user_id)
    bot.reply_to(message, "Please send your Netflix account in the format: email:password")

@bot.message_handler(commands=['checkSpotify'])
def check_spotify(message):
    user_id = message.from_user.id
    initialize_user(user_id)
    bot.reply_to(message, "Please send your Spotify account in the format: email:password")

@bot.message_handler(commands=['checkHotmail'])
def check_hotmail(message):
    user_id = message.from_user.id
    initialize_user(user_id)
    bot.reply_to(message, "Please send your Hotmail account in the format: email:password")

@bot.message_handler(commands=['checkDisney'])
def check_disney(message):
    user_id = message.from_user.id
    initialize_user(user_id)
    bot.reply_to(message, "Please send your Disney account in the format: email:password")

@bot.message_handler(commands=['checkTradingView'])
def check_tradingview(message):
    user_id = message.from_user.id
    initialize_user(user_id)
    bot.reply_to(message, "Please send your TradingView account in the format: email:password")

@bot.message_handler(commands=['checkCrunchyroll'])
def check_crunchyroll(message):
    user_id = message.from_user.id
    initialize_user(user_id)
    bot.reply_to(message, "Please send your Crunchyroll account in the format: email:password")

@bot.message_handler(func=lambda message: True)
def handle_account_check(message):
    user_id = message.from_user.id
    initialize_user(user_id)

    if ':' not in message.text:
        bot.reply_to(message, "❌ Please provide account details in the format: email:password.")
        return

    service = ''
    if message.reply_to_message and message.reply_to_message.text:
        if "netflix" in message.reply_to_message.text.lower():
            service = 'Netflix'
        elif "spotify" in message.reply_to_message.text.lower():
            service = 'Spotify'
        elif "hotmail" in message.reply_to_message.text.lower():
            service = 'Hotmail'
        elif "disney" in message.reply_to_message.text.lower():
            service = 'Disney'
        elif "tradingview" in message.reply_to_message.text.lower():
            service = 'TradingView'
        elif "crunchyroll" in message.reply_to_message.text.lower():
            service = 'Crunchyroll'

    if service:
        email, password = message.text.split(":", 1)
        response = check_account_with_proxies(service, email, password, user_data[user_id]["proxies"])

        if response["status"] == "valid":
            bot.reply_to(message, f"✅ Valid {service} account: {email}:{password}")
            user_data[user_id]["service_checks"][service] += 1
            user_data[user_id]["checks_today"] += 1
            save_user_data()
        else:
            bot.reply_to(message, f"❌ Invalid {service} account: {email}:{password} - {response['message']}")
    else:
        bot.reply_to(message, "❌ Please use the specific command to check an account or reply to the correct account format.")

def check_account_with_proxies(service, email, password, proxies):
    for proxy in proxies + admin_proxies:  # Combine user-specific and admin proxies
        try:
            url = service_endpoints[service]
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=5)
            if response.status_code == 200:
                return {"status": "valid"}
            else:
                return {"status": "invalid", "message": "Service responded with an error."}
        except requests.exceptions.RequestException as e:
            logging.error(f"Proxy {proxy} failed: {e}")
            continue  # Try the next proxy
    return {"status": "invalid", "message": "All proxies failed."}

@bot.message_handler(commands=['addproxy'])
def add_proxy(message):
    user_id = message.from_user.id
    initialize_user(user_id)

    try:
        proxy = message.text.split(maxsplit=1)[1]  # Get the proxy from the command
        if proxy:
            user_data[user_id]["proxies"].append(proxy)
            save_user_data()
            bot.reply_to(message, f"✅ Proxy added: {proxy}")
        else:
            bot.reply_to(message, "❌ Please provide a proxy in the format: /addproxy proxy:port")
    except IndexError:
        bot.reply_to(message, "❌ Please provide a proxy in the format: /addproxy proxy:port")

@bot.message_handler(commands=['removeproxy'])
def remove_proxy(message):
    user_id = message.from_user.id
    initialize_user(user_id)

    try:
        proxy = message.text.split(maxsplit=1)[1]  # Get the proxy from the command
        if proxy in user_data[user_id]["proxies"]:
            user_data[user_id]["proxies"].remove(proxy)
            save_user_data()
            bot.reply_to(message, f"✅ Proxy removed: {proxy}")
        else:
            bot.reply_to(message, f"❌ Proxy {proxy} not found in your list.")
    except IndexError:
        bot.reply_to(message, "❌ Please provide a proxy in the format: /removeproxy proxy:port")

@bot.message_handler(commands=['listproxies'])
def list_proxies(message):
    user_id = message.from_user.id
    initialize_user(user_id)

    if user_data[user_id]["proxies"]:
        proxies_list = "\n".join(user_data[user_id]["proxies"])
        bot.reply_to(message, f"🗂 Your Proxies:\n{proxies_list}")
    else:
        bot.reply_to(message, "❌ You have no proxies added.")

@bot.message_handler(commands=['commands'])
def show_commands(message):
    commands_text = (
        "📜 Available Commands:\n"
        "/checkNetflix - Check Netflix account\n"
        "/checkSpotify - Check Spotify account\n"
        "/checkHotmail - Check Hotmail account\n"
        "/checkDisney - Check Disney account\n"
        "/checkTradingView - Check TradingView account\n"
        "/checkCrunchyroll - Check Crunchyroll account\n"
        "/addproxy proxy:port - Add a proxy\n"
        "/removeproxy proxy:port - Remove a proxy\n"
        "/listproxies - List all added proxies\n"
        "/commands - Show this command list\n"
        "/status - Check your current account status"
    )
    bot.reply_to(message, commands_text)

@bot.message_handler(commands=['status'])
def status(message):
    user_id = message.from_user.id
    initialize_user(user_id)

    status_message = (
        f"👤 User ID: {user_id}\n"
        f"📊 Total Checks Today: {user_data[user_id]['checks_today']}\n"
        f"🗂 Proxies Added: {len(user_data[user_id]['proxies'])}\n"
    )
    bot.reply_to(message, status_message)

# Reset daily checks at midnight (12 AM)
def reset_job():
    while True:
        now = time.localtime()
        if now.tm_hour == 0 and now.tm_min == 0:
            reset_daily_checks()
            time.sleep(60)  # Wait a minute before checking again
        time.sleep(60)  # Check every minute

# Start the reset job in a separate thread
threading.Thread(target=reset_job, daemon=True).start()

bot.polling()g()