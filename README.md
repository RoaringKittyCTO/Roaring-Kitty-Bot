# Roaring Kitty Telegram Bot

A Telegram bot that monitors the real Roaring Kitty token and sends custom notifications with buy alerts.

## Features

- **Real-time Token Monitoring**: Tracks actual Roaring Kitty contract `0xD8C978de79E12728e38aa952a6cB4166F891790f`
- **Custom Notifications**: Generates images with your party background showing remaining token counts
- **Buy Detection**: Alerts when new purchases are detected via DexScreener API
- **Python REPL**: Safe code execution with security restrictions
- **24/7 Operation**: Designed for continuous monitoring

## Bot Commands

- `/start` - Welcome message and command overview
- `/start_roar` - Begin monitoring Roaring Kitty token
- `/roar_status` - Get current token status with custom image
- `/subscribe` - Enable buy notifications
- `/unsubscribe` - Disable notifications
- `/run <code>` - Execute Python code safely
- `/help` - Show detailed help

## Quick Deploy to Render

1. Fork this repository to your GitHub
2. Go to [render.com](https://render.com) and sign up
3. Create new Web Service from your GitHub repo
4. Add environment variable: `TELEGRAM_BOT_TOKEN`
5. Deploy automatically

See `RENDER_DEPLOYMENT.md` for detailed instructions.

## Local Development

```bash
# Install dependencies
pip install python-telegram-bot RestrictedPython Pillow requests web3

# Set environment variable
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Run bot
python main.py
```

## Architecture

- **DexScreener Integration**: Real-time token data
- **Custom Image Generation**: Party background with token counts
- **Secure Code Execution**: RestrictedPython sandbox
- **Subscription System**: Automated buy alerts

## Files Structure

```
├── main.py                    # Bot entry point
├── bot_handler_new.py         # Main bot logic
├── dexscreener_monitor.py     # Token monitoring via DexScreener API
├── image_generator.py         # Custom notification images
├── code_executor.py           # Safe Python execution
├── security_config.py         # Security restrictions
├── attached_assets/           # Background images
├── render.yaml               # Render deployment config
├── Dockerfile                # Container configuration
└── RENDER_DEPLOYMENT.md      # Deployment guide
```

## Security Features

- RestrictedPython for safe code execution
- Timeout mechanisms for code execution
- Restricted module imports
- No file system access for executed code
- Environment variable protection

## Monitoring Details

- **Token Contract**: `0xD8C978de79E12728e38aa952a6cB4166F891790f`
- **Data Source**: DexScreener API
- **Update Frequency**: Every 30 seconds
- **Notification Triggers**: New buy transactions detected

Your bot will continuously monitor real Roaring Kitty token activity and send personalized notifications with remaining token counts displayed on your custom party background.