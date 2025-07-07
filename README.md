# Reminders Bot

This is a simple bot that sends reminders to a Telegram group based on the information from in a Google Sheet.

## Installation

1. Clone the repository
2. Install the requirements (tested with Python 3.12)
3. Create a `.env` file with the following content:
```
TELEGRAM_BOT_TOKEN=your_api_id
TELEGRAM_CHAT_ID=your_chat_id
MODE=DEVELOPMENT
SHEET_ID=your_sheet_id
```
4. Run the bot with a test date like 01/01/2000: `python3 bot.py 01/01/2000`

## Usage

In production mode, the bot will send the reminders based on the current date. Call the program once a day with a cron job or similar scheduler.