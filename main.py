#!/usr/bin/env python3
"""
Flask wrapper for Telegram bot deployment
"""
import os
import asyncio
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('TELEGRAM_ADMIN_ID')
BACKEND_URL = os.getenv('BACKEND_URL', 'https://lnh8imcj5x3d.manus.space')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://fyqwgods.manus.space')

# Flask app
app = Flask(__name__)

# Global bot application
bot_application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_text = f"""🎉 Welcome to P2P USDT Trading Bot, {user.first_name}!

Your secure platform for USDT trading in Ethiopia.

Commands:
• /help - Get detailed help
• /admin - Admin panel (admin only)

How it works:
1️⃣ Browse listings on our website
2️⃣ Create deals and get trade codes
3️⃣ Use this bot to confirm payments
4️⃣ Admin releases USDT after confirmation

🔗 Platform: {FRONTEND_URL}
💬 Support: Contact admin

Happy trading! 🚀"""
    
    keyboard = [
        [InlineKeyboardButton("📋 View Listings", url=f"{FRONTEND_URL}/listings")],
        [InlineKeyboardButton("➕ Post Trade", url=f"{FRONTEND_URL}/post-ad")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = f"""📖 P2P USDT Trading Bot Help

Commands:
🏠 /start - Welcome message and main menu
❓ /help - This help message
👑 /admin - Admin panel (admin only)

Trading Process:
1. Visit our website to browse listings
2. Create a deal and get a trade code
3. Seller sends USDT to escrow wallet
4. Buyer sends ETB to seller
5. Seller confirms payment via bot
6. Admin releases USDT to buyer

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

Admin Commands:
• /start - Main menu
• /help - Help information
• /admin - This panel

To manage trades, use the web interface or API directly.

Admin ID: {ADMIN_ID}"""
    
    keyboard = [
        [InlineKeyboardButton("🌐 Open Frontend", url=FRONTEND_URL)],
        [InlineKeyboardButton("🔧 API Health", url=f"{BACKEND_URL}/health")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(admin_text, reply_markup=reply_markup)

def create_bot_application():
    """Create and configure the bot application"""
    global bot_application
    
    if bot_application is None:
        # Create application
        bot_application = Application.builder().token(TOKEN).build()
        
        # Add handlers
        bot_application.add_handler(CommandHandler("start", start))
        bot_application.add_handler(CommandHandler("help", help_command))
        bot_application.add_handler(CommandHandler("admin", admin_command))
        
        logger.info("Bot application created and configured")
    
    return bot_application

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "P2P USDT Trading Bot",
        "bot_token": TOKEN[:10] + "..." if TOKEN else "Not configured",
        "admin_id": ADMIN_ID,
        "frontend_url": FRONTEND_URL,
        "backend_url": BACKEND_URL
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook"""
    try:
        # Get the bot application
        application = create_bot_application()
        
        # Process the update
        update = Update.de_json(request.get_json(), application.bot)
        
        # Run the update processing in async context
        asyncio.run(application.process_update(update))
        
        return jsonify({"status": "ok"})
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Set the webhook URL"""
    try:
        webhook_url = request.json.get('webhook_url')
        if not webhook_url:
            return jsonify({"status": "error", "message": "webhook_url required"}), 400
        
        # Create bot instance
        bot = Bot(TOKEN)
        
        # Set webhook
        asyncio.run(bot.set_webhook(url=webhook_url))
        
        return jsonify({"status": "ok", "webhook_url": webhook_url})
    
    except Exception as e:
        logger.error(f"Set webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test_bot', methods=['POST'])
def test_bot():
    """Test bot by sending a message to admin"""
    try:
        bot = Bot(TOKEN)
        
        # Send test message to admin
        asyncio.run(bot.send_message(
            chat_id=ADMIN_ID,
            text="🤖 Bot deployed successfully! Your P2P USDT Trading Bot is now running on hosting service. Try /start command!"
        ))
        
        return jsonify({"status": "ok", "message": "Test message sent to admin"})
    
    except Exception as e:
        logger.error(f"Test bot error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🤖 P2P USDT Trading Bot - Flask Wrapper")
    print(f"Token: {TOKEN[:10]}..." if TOKEN else "Token: Not configured")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    
    # Create bot application
    create_bot_application()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

