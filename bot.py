#!/usr/bin/env python3
"""
P2P USDT Trading Platform Telegram Bot
"""

import os
import logging
import asyncio
import requests
from typing import Dict, Any
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_bot_token_here')
ADMIN_ID = int(os.getenv('TELEGRAM_ADMIN_ID', '123456789'))
API_BASE_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
RELEASE_SECRET = os.getenv('RELEASE_SECRET', 'secure_key_here')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class P2PTradingBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("post_trade", self.post_trade_command))
        self.application.add_handler(CommandHandler("confirm_payment", self.confirm_payment_command))
        self.application.add_handler(CommandHandler("release_funds", self.release_funds_command))
        self.application.add_handler(CommandHandler("my_deals", self.my_deals_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for text messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_text = f"""
🎉 Welcome to P2P USDT Trading Bot, {user.first_name}!

Your secure platform for USDT trading in Ethiopia.

Commands:
• /help - Get detailed help
• /post_trade - Create a new trade offer
• /confirm_payment #TRADE_CODE - Confirm ETB payment received
• /my_deals - View your active deals
• /release_funds #TRADE_CODE - (Admin only) Release USDT

How it works:
1️⃣ Browse listings on our website
2️⃣ Create deals and get trade codes
3️⃣ Use this bot to confirm payments
4️⃣ Admin releases USDT after confirmation

🔗 Platform: Visit our website
💬 Support: Contact admin

Happy trading! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 View Listings", url="http://localhost:3000/listings")],
            [InlineKeyboardButton("➕ Post Trade", callback_data="post_trade")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 *P2P USDT Trading Bot Help*

*Commands:*

🏠 `/start` - Welcome message and main menu

📝 `/post_trade` - Start creating a new trade offer
   Example: `/post_trade`

✅ `/confirm_payment #EZ104` - Confirm ETB payment received
   Example: `/confirm_payment #EZ104`
   ⚠️ Only sellers can confirm payments

💰 `/release_funds #EZ104` - Release USDT (Admin only)
   Example: `/release_funds #EZ104`

📊 `/my_deals` - View your active deals

👨‍💼 `/admin` - Admin panel (Admin only)

*Trading Process:*
1. Create or find a trade on the website
2. Seller sends USDT to escrow wallet
3. Buyer sends ETB to seller
4. Seller confirms payment via `/confirm_payment`
5. Admin releases USDT via `/release_funds`

*Important Notes:*
• Trade codes are case-sensitive (e.g., #EZ104)
• Trades expire in 90 minutes
• 1.5% commission applies to all trades
• Always verify counterparty details

Need help? Contact @admin_telegram
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def post_trade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /post_trade command"""
        keyboard = [
            [InlineKeyboardButton("💰 Sell USDT", callback_data="trade_sell")],
            [InlineKeyboardButton("🛒 Buy USDT", callback_data="trade_buy")],
            [InlineKeyboardButton("🌐 Use Website", url="http://localhost:3000/post-ad")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
📝 *Create New Trade*

Choose your trade type or use our website for more options:

• *Sell USDT* - You have USDT, want ETB
• *Buy USDT* - You have ETB, want USDT

For advanced options like payment methods and limits, use our website.
        """
        
        await update.message.reply_text(
            text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def confirm_payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /confirm_payment command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a trade code.\n\n"
                "Usage: `/confirm_payment #EZ104`",
                parse_mode='Markdown'
            )
            return
        
        trade_code = context.args[0].upper()
        if not trade_code.startswith('#'):
            trade_code = '#' + trade_code
        
        user_id = update.effective_user.id
        
        try:
            # Call backend API to confirm payment
            response = requests.post(
                f"{API_BASE_URL}/confirm-payment",
                json={
                    "trade_code": trade_code,
                    "user_id": user_id,
                    "notes": f"Payment confirmed via Telegram by user {user_id}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    await update.message.reply_text(
                        f"✅ *Payment Confirmed!*\n\n"
                        f"Trade: `{trade_code}`\n"
                        f"Status: Waiting for admin to release USDT\n\n"
                        f"The admin has been notified and will release the USDT shortly.",
                        parse_mode='Markdown'
                    )
                    
                    # Notify admin
                    await self.notify_admin(
                        f"💰 *Payment Confirmed*\n\n"
                        f"Trade: `{trade_code}`\n"
                        f"User: {update.effective_user.first_name} (@{update.effective_user.username})\n"
                        f"Action: Use `/release_funds {trade_code}` to release USDT"
                    )
                else:
                    await update.message.reply_text(f"❌ Error: {data.get('message', 'Unknown error')}")
            else:
                await update.message.reply_text("❌ Failed to confirm payment. Please try again or contact admin.")
                
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            await update.message.reply_text("❌ Network error. Please try again later.")
    
    async def release_funds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /release_funds command (Admin only)"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a trade code.\n\n"
                "Usage: `/release_funds #EZ104`",
                parse_mode='Markdown'
            )
            return
        
        trade_code = context.args[0].upper()
        if not trade_code.startswith('#'):
            trade_code = '#' + trade_code
        
        try:
            # Call backend API to release funds
            response = requests.post(
                f"{API_BASE_URL}/admin/release-funds",
                json={
                    "trade_code": trade_code,
                    "release_secret": RELEASE_SECRET,
                    "notes": f"Funds released via Telegram by admin {user_id}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    trade_data = data.get('data', {})
                    await update.message.reply_text(
                        f"✅ *Funds Released Successfully!*\n\n"
                        f"Trade: `{trade_code}`\n"
                        f"USDT Amount: `{trade_data.get('usdt_amount', 'N/A')}`\n"
                        f"Commission: `{trade_data.get('commission', 'N/A')}`\n\n"
                        f"The buyer has received their USDT.",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(f"❌ Error: {data.get('message', 'Unknown error')}")
            else:
                await update.message.reply_text("❌ Failed to release funds. Please check the trade code and try again.")
                
        except Exception as e:
            logger.error(f"Error releasing funds: {e}")
            await update.message.reply_text("❌ Network error. Please try again later.")
    
    async def my_deals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /my_deals command"""
        user_id = update.effective_user.id
        
        # For demo purposes, show a placeholder message
        # In production, this would query the backend for user's deals
        text = """
📊 *Your Active Deals*

Currently, this feature requires backend integration with user authentication.

To view your deals:
1. Visit our website: [P2P Trading Platform](http://localhost:3000)
2. Navigate to your account/profile section
3. View your trade history and active deals

For immediate assistance with specific trades, contact @admin_telegram with your trade code.
        """
        
        keyboard = [
            [InlineKeyboardButton("🌐 Visit Website", url="http://localhost:3000")],
            [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/admin_telegram")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command (Admin only)"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 Pending Deals", callback_data="admin_pending")],
            [InlineKeyboardButton("📈 Platform Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("🌐 Admin Panel", url="http://localhost:3000/admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
👨‍💼 *Admin Panel*

Welcome, Administrator!

*Quick Actions:*
• View pending deals awaiting fund release
• Check platform statistics
• Access web admin panel

*Commands:*
• `/release_funds #TRADE_CODE` - Release USDT
• `/admin` - Show this panel
        """
        
        await update.message.reply_text(
            text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "help":
            await self.help_command(update, context)
        elif query.data == "post_trade":
            await self.post_trade_command(update, context)
        elif query.data in ["trade_sell", "trade_buy"]:
            trade_type = "sell" if query.data == "trade_sell" else "buy"
            await query.edit_message_text(
                f"🌐 *Create {trade_type.title()} Trade*\n\n"
                f"Please visit our website to create a detailed {trade_type} offer:\n"
                f"[Create Trade Ad](http://localhost:3000/post-ad)\n\n"
                f"You can specify amount, rate, payment methods, and more!",
                parse_mode='Markdown'
            )
        elif query.data == "admin_pending":
            if query.from_user.id == ADMIN_ID:
                await self.show_pending_deals(query)
            else:
                await query.edit_message_text("❌ Access denied.")
        elif query.data == "admin_stats":
            if query.from_user.id == ADMIN_ID:
                await self.show_platform_stats(query)
            else:
                await query.edit_message_text("❌ Access denied.")
    
    async def show_pending_deals(self, query):
        """Show pending deals for admin"""
        try:
            response = requests.get(f"{API_BASE_URL}/admin/pending-deals?status=paid")
            if response.status_code == 200:
                data = response.json()
                deals = data.get('data', [])
                
                if not deals:
                    text = "✅ No pending deals requiring fund release."
                else:
                    text = f"📊 *Pending Fund Releases* ({len(deals)} deals)\n\n"
                    for deal in deals[:5]:  # Show first 5 deals
                        text += f"• `{deal.get('trade_code')}` - {deal.get('usdt_amount')} USDT\n"
                    
                    if len(deals) > 5:
                        text += f"\n... and {len(deals) - 5} more deals"
                    
                    text += f"\n\nUse `/release_funds #TRADE_CODE` to release funds."
            else:
                text = "❌ Failed to fetch pending deals."
        except Exception as e:
            text = "❌ Network error while fetching deals."
        
        await query.edit_message_text(text, parse_mode='Markdown')
    
    async def show_platform_stats(self, query):
        """Show platform statistics for admin"""
        try:
            # Fetch basic stats from API
            listings_response = requests.get(f"{API_BASE_URL}/listings")
            
            if listings_response.status_code == 200:
                listings_data = listings_response.json()
                total_listings = listings_data.get('total', 0)
                
                text = f"""
📈 *Platform Statistics*

📋 Total Active Listings: {total_listings}
💰 Commission Rate: 1.5%
⏱️ Trade Timeout: 90 minutes

For detailed analytics, visit the web admin panel.
                """
            else:
                text = "❌ Failed to fetch platform statistics."
        except Exception as e:
            text = "❌ Network error while fetching statistics."
        
        await query.edit_message_text(text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        text = update.message.text
        
        # Check if message contains a trade code
        if '#' in text and any(word.startswith('#') for word in text.split()):
            trade_code = next(word for word in text.split() if word.startswith('#'))
            
            keyboard = [
                [InlineKeyboardButton("✅ Confirm Payment", callback_data=f"confirm_{trade_code}")],
                [InlineKeyboardButton("📊 Check Status", callback_data=f"status_{trade_code}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"I detected trade code `{trade_code}`.\n\n"
                f"What would you like to do?",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            # Default response for unrecognized messages
            await update.message.reply_text(
                "I didn't understand that command. Use /help to see available commands."
            )
    
    async def notify_admin(self, message: str):
        """Send notification to admin"""
        try:
            await self.application.bot.send_message(
                chat_id=ADMIN_ID,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")
    
    def run(self):
        """Start the bot"""
        logger.info("Starting P2P Trading Bot...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = P2PTradingBot()
    bot.run()

