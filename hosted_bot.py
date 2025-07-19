#!/usr/bin/env python3
"""
P2P USDT Trading Bot - Hosted Version
"""
import os
import asyncio
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request, jsonify
import threading

# Configuration
TOKEN = '7649472727:AAFY8vv9RbhLOKg91F9JLyN4jqQLVmmM_o4'
ADMIN_ID = '340425758'
BACKEND_URL = 'http://192.168.1.103:5000'
FRONTEND_URL = 'http://192.168.1.103:5173'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'Bot is running', 'bot_token': TOKEN[:10] + '...', 'admin_id': ADMIN_ID}

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'P2P USDT Trading Bot'}

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_text = f"""🎉 Welcome to P2P USDT Trading Bot, {user.first_name}!

Your secure platform for USDT trading in Ethiopia.

Commands:
• /help - Get detailed help
• /admin - Admin panel (admin only)

🔗 Platform: {FRONTEND_URL}
💬 Support: Contact admin

Happy trading! 🚀"""
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = f"""📖 P2P USDT Trading Bot Help

Commands:
🏠 /start - Welcome message
❓ /help - This help message  
👑 /admin - Admin panel (admin only)

Platform: {FRONTEND_URL}
API: {BACKEND_URL}

Need help? Contact the admin!"""
    
    await update.message.reply_text(help_text)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user_id = str(update.effective_user.id)
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Access denied. Admin only command.")
        return
    
    admin_text = f"""👑 Admin Panel

Platform Status: ✅ Online
Frontend: {FRONTEND_URL}
Backend: {BACKEND_URL}

Admin ID: {ADMIN_ID}"""
    
    await update.message.reply_text(admin_text)

def run_flask():
    """Run Flask server in background"""
    app.run(host='0.0.0.0', port=8000, debug=False)

async def main():
    """Main bot function"""
    # Start Flask in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Create bot application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('admin', admin_command))
    
    # Send startup message to admin
    bot = Bot(TOKEN)
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text="🤖 Bot deployed successfully on free hosting! Your P2P USDT Trading Bot is now running. Try /start command!"
        )
        logger.info("Startup message sent to admin")
    except Exception as e:
        logger.error(f"Failed to send startup message: {e}")
    
    # Start polling
    logger.info("Starting bot polling...")
    await application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()

    print("🤖 P2P USDT Trading Bot - Starting...")
    print(f"Token: {TOKEN[:10]}...")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    print("🚀 Bot is starting up...")

    asyncio.get_event_loop().run_until_complete(main())


