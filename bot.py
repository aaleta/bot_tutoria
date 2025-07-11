import csv
import sys

import requests
import datetime
from io import StringIO
from dotenv import dotenv_values


class ReminderBot:
    """
    A simple bot to send reminders to a Telegram chat using the Telegram Bot API.
    """
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message):
        try:
            response = requests.post(
                url = f"https://api.telegram.org/bot{self.token}/sendMessage",
                data = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                },
                timeout=100
            ).json()
            return response
        except Exception as e:
            print(str(e))
            return {'error': str(e)}

def fetch_sheet_csv(sheet_id):
    """
    Fetches the CSV content from a Google Sheets URL.
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    response = requests.get(url)
    response.raise_for_status()
    csv_text = response.content.decode('utf-8')
    return list(csv.DictReader(StringIO(csv_text)))


def format_spanish_date(date):
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    return f"{date.day} de {meses[date.month - 1]}"

def build_message(row, today):
    """Builds a reminder message based on the row and today's date"""
    r_type = row['type'].strip().lower()
    title = row['title'].strip()
    notify_days = int(row.get('notify_days', 0))

    description = row.get('description', '').strip()
    url = row.get('url', '').strip()

    # Parse dates
    start_date = datetime.datetime.strptime(row['start_date'], '%d/%m/%Y').date() if row['start_date'] else None
    end_date = datetime.datetime.strptime(row['end_date'], '%d/%m/%Y').date() if row['end_date'] else None

    msg = ''
    if r_type == 'window':
        # Event body
        body = f"\n<b>{title}</b>\n"
        if description:
            body += f"\n{description}\n"
        body += f"\n🗓 Del {format_spanish_date(start_date)} al {format_spanish_date(end_date)}\n"
        if url:
            body += f"\n🌐 {url}\n"

        if start_date == today:
            msg += "📣 <b>Empieza hoy</b>\n"
            msg += body

        if end_date and (end_date - today).days == notify_days:
            plural = 's' if notify_days > 1 else ''
            msg += f"⏳ <b>Termina en {notify_days} día{plural}</b>\n"
            msg += body

        if end_date  == today:
            msg += f"⚠️ <b>Termina hoy</b>\n"
            msg += body

    elif r_type == 'single':
        # Event body
        body = f"\n<b>{title}</b>\n"
        if description:
            body += f"\n{description}\n"
        body += f"\n🗓 {format_spanish_date(end_date)}\n"
        if url:
            body += f"\n🌐 {url}\n"

        if end_date and (end_date - today).days == notify_days:
            plural_n = 'n' if notify_days > 1 else ''
            plural_s = 's' if notify_days > 1 else ''
            msg += f"🔔 <b>Falta{plural_n} {notify_days} día{plural_s}</b>\n"
            msg += body

        elif end_date == today:
            msg += f"📣 <b>¡Es hoy!</b>\n"
            msg += body

    if len(msg) > 0:
        return msg

    return None

if __name__ == "__main__":
    config = dotenv_values(".env")

    BOT_TOKEN = config["TELEGRAM_BOT_TOKEN"]
    CHAT_ID = config["TELEGRAM_CHAT_ID"]
    PRODUCTION = config["MODE"] == 'PRODUCTION'
    SHEET_ID = config["SHEET_ID"]

    bot = ReminderBot(BOT_TOKEN, CHAT_ID)

    today = datetime.date.today() if PRODUCTION else datetime.datetime.strptime(sys.argv[1], '%d/%m/%Y').date()

    rows = fetch_sheet_csv(SHEET_ID)
    messages = [msg for row in rows if (msg := build_message(row, today)) is not None]

    print(f"Found {len(messages)} messages to send for {today.strftime('%d/%m/%Y')}")
    for message in messages:
        print(f"Sending message")
        response = bot.send_message(message)
        print("Telegram API response:", response['ok'])
