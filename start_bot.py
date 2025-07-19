#!/usr/bin/env python3
"""
Startup script for P2P USDT Trading Telegram Bot
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_ADMIN_ID',
        'BACKEND_URL',
        'RELEASE_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🤖 P2P USDT Trading Telegram Bot")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("⚠️  No .env file found. Creating from template...")
        template_file = Path(__file__).parent / '.env.template'
        if template_file.exists():
            import shutil
            shutil.copy(template_file, env_file)
            print(f"✅ Created .env file at {env_file}")
            print("📝 Please edit the .env file with your bot token and configuration.")
            return
        else:
            print("❌ No .env template found. Please create .env file manually.")
            return
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment
    if not check_environment():
        return
    
    # Import and start bot
    try:
        from bot import P2PTradingBot
        bot = P2PTradingBot()
        print("🚀 Starting bot...")
        bot.run()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    main()

