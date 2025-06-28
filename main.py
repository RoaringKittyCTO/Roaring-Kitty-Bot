#!/usr/bin/env python3
"""
Main entry point for the Telegram Python REPL bot.
"""

import os
import logging
from bot_handler_new import TelegramBot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """Start the Telegram bot."""
    # Get bot token from environment variable
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'your_bot_token_here')
    
    if bot_token == 'your_bot_token_here':
        logger.error("Please set the TELEGRAM_BOT_TOKEN environment variable")
        return
    
    # Initialize and start the bot
    bot = TelegramBot(bot_token)
    logger.info("Starting Telegram Python REPL bot...")
    bot.run()

if __name__ == '__main__':
    main()
