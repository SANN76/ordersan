import os
import telebot
import requests
import shlex

# --- KONFIGURASI DARI ENVIRONMENT VARIABLES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8599094698:AAEGvWQBCTMjUEqOrkgX2ZCY7-W496AaweQ")
API_URL = os.environ.get("API_URL", "https://sprintpedia.id/api/v2")
API_KEY = os.environ.get("API_KEY", "9aa246-4ad68f-7d5576-5246ef-503a5a")
MY_TELEGRAM_ID = int(os.environ.get("MY_TELEGRAM_ID", "8804168720"))

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def is_authorized(message):
    return message.from_user.id == MY_TELEGRAM_ID


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Akses Ditolak. Bot ini bersifat pribadi.")
        return
    bot.reply_to(
        message,
        "👋 Halo Bos!\n\n"
        "Format order:\n"
        "`/order \"ID_LAYANAN\" JUMLAH LINK`\n\n"
        "Contoh:\n"
        "`/order \"2643\" 1000 https://instagram.com/username`",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['saldo'])
def cek_saldo(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Akses Ditolak.")
        return
    try:
        payload = {'key': API_KEY, 'action': 'balance'}
        r = requests.post(API_URL, data=payload, timeout=30)
        result = r.json()
        if 'balance' in result:
            bot.reply_to(message, f"💰 Saldo: `{result['balance']}`", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ Gagal cek saldo: `{result.get('error', 'Unknown')}`", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: `{str(e)}`", parse_mode='Markdown')


@bot.message_handler(commands=['order'])
def process_order(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Akses Ditolak.")
        return

    try:
        text = message.text.replace('/order', '', 1).strip()
        parts = shlex.split(text)

        if len(parts) != 3:
            bot.reply_to(
                message,
                "❌ Format salah!\n\n"
                "Gunakan: `/order \"ID_LAYANAN\" JUMLAH LINK`\n"
                "Contoh: `/order \"2643\" 1000 https://instagram.com/username`",
                parse_mode='Markdown'
            )
            return

        service_id, quantity, link = parts

        if not quantity.isdigit():
            bot.reply_to(message, "❌ Jumlah harus angka. Contoh: 1000")
            return

        if not (link.startswith("http://") or link.startswith("https://")):
            bot.reply_to(message, "❌ Link harus diawali http:// atau https://")
            return

        bot.reply_to(
            message,
            f"⏳ *Memproses pesanan...*\n\n"
            f"🆔 Layanan: `{service_id}`\n"
            f"🔢 Jumlah: `{quantity}`\n"
            f"🔗 Link: {link}",
            parse_mode='Markdown'
        )

        payload = {
            'key': API_KEY,
            'action': 'add',
            'service': service_id,
            'link': link,
            'quantity': quantity
        }

        response = requests.post(API_URL, data=payload, timeout=30)
        result = response.json()

        if 'order' in result:
            bot.reply_to(
                message,
                f"✅ *Pesanan Berhasil!*\n\n🆔 ID Order: `{result['order']}`",
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(
                message,
                f"❌ *Pesanan Gagal!*\n\nError: `{result.get('error', 'Unknown')}`",
                parse_mode='Markdown'
            )

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: `{str(e)}`", parse_mode='Markdown')


print("🤖 Bot Private berjalan...")
bot.polling(none_stop=True)
