# P2P USDT Trading Telegram Bot

This Telegram bot provides an interface for managing USDT trades on the P2P trading platform.

## Features

- **Trade Management**: Create and manage trade offers
- **Payment Confirmation**: Sellers can confirm ETB payments received
- **Admin Controls**: Admin can release USDT funds
- **Notifications**: Real-time updates on trade status
- **User-Friendly Interface**: Inline keyboards and intuitive commands

## Commands

### User Commands
- `/start` - Welcome message and main menu
- `/help` - Detailed help and instructions
- `/post_trade` - Create a new trade offer
- `/confirm_payment #TRADE_CODE` - Confirm ETB payment received
- `/my_deals` - View active deals (requires web integration)

### Admin Commands
- `/release_funds #TRADE_CODE` - Release USDT to buyer
- `/admin` - Admin panel with statistics and controls

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Required Environment Variables**
   - `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
   - `TELEGRAM_ADMIN_ID` - Admin's Telegram user ID
   - `BACKEND_URL` - Backend API URL (default: http://localhost:8000)
   - `RELEASE_SECRET` - Secret key for fund release (must match backend)
   - `FRONTEND_URL` - Frontend URL (default: http://localhost:3000)

4. **Start the Bot**
   ```bash
   python3 start_bot.py
   # or directly
   python3 bot.py
   ```

## Bot Token Setup

1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token to your `.env` file

## Admin Setup

1. Get your Telegram user ID (use @userinfobot)
2. Set `TELEGRAM_ADMIN_ID` in `.env` file
3. Admin will have access to fund release and admin commands

## Integration with Backend

The bot integrates with the FastAPI backend through these endpoints:

- `POST /confirm-payment` - Confirm ETB payment
- `POST /admin/release-funds` - Release USDT funds
- `GET /admin/pending-deals` - Get pending deals
- `GET /listings` - Get platform statistics

## Usage Examples

### Confirming Payment (Seller)
```
/confirm_payment #EZ104
```

### Releasing Funds (Admin)
```
/release_funds #EZ104
```

### Getting Help
```
/help
```

## Security Features

- Admin-only commands with user ID verification
- Secure API integration with secret keys
- Input validation and error handling
- Logging of all actions

## Deployment

For production deployment:

1. Use a process manager like PM2 or systemd
2. Set up proper logging
3. Configure webhook instead of polling (optional)
4. Use environment variables for all secrets

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot token is correct
   - Verify bot is started with `/start`
   - Check network connectivity

2. **Admin commands not working**
   - Verify `TELEGRAM_ADMIN_ID` is correct
   - Check admin user ID format (should be numeric)

3. **API integration errors**
   - Verify backend is running
   - Check `BACKEND_URL` configuration
   - Verify `RELEASE_SECRET` matches backend

### Logs

The bot logs important events and errors. Check console output for debugging information.

## Contributing

1. Follow Python coding standards
2. Add proper error handling
3. Update documentation for new features
4. Test all commands before deployment

