#!/usr/bin/env python3
import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")
BACKEND_URL = os.getenv("BACKEND_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_text = f"""🎉 እንኳን ደህና መጡ ወደ P2P USDT ንግድ ቦት፣ {user.first_name}!

ይህ ቦት በኢትዮጵያ ውስጥ የታመነ እና ቀላል የUSDT መግዛትና ሽያጭ መድረክ ነው።

ትዕዛዞች:
• /help - መመሪያ መረጃ
{f"• /admin - አስተዳዳሪ መቆጣጠሪያ (ለአስተዳዳሪ ብቻ)" if str(user.id) == ADMIN_ID else ""}

እንዴት ነው የሚሰራው?
1️⃣ ዝርዝሮችን በድህረ ገጻችን ይመልከቱ  
2️⃣ የግዢ ወይም የሽያጭ ዝርዝር ይሙሉ እና የንግድ ኮድ ይቀበሉ  
3️⃣ በቦቱ ውስጥ ክፍያ ያረጋግጡ  
4️⃣ አስተዳዳሪ ኮንፋርሜሽን ካገኘ በኋላ USDT ይልቃል

🔗 መድረክ: [ድህረ ገጽ ለመመልከት እዚህ ይጫኑ]({FRONTEND_URL})  
💬 ድጋፍ: [@bekitesttelegram](https://t.me/bekitesttelegram)

📌 ማሳሰቢያ፡ በግዢና ሽያጭ ላይ ምንም ወጪ የለም።"""

    
    keyboard = [
        [InlineKeyboardButton("📋 View Listings", url=f"{FRONTEND_URL}/listings")],
        [InlineKeyboardButton("➕ Post Trade", url=f"{FRONTEND_URL}/post-ad")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """📖 P2P USDT Trading Bot Help

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

def main():
    """Start the bot"""
    print("🤖 Starting P2P USDT Trading Bot...")
    print(f"Token: {TOKEN[:10]}...")
    print(f"Admin ID: {ADMIN_ID}")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Start the bot
    print("✅ Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

