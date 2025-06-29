"""
Clean Telegram bot handler for ROAR token monitoring only.
"""

import logging
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from dexscreener_monitor import DexScreenerMonitor
from image_generator import NotificationImageGenerator

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        """Initialize the Telegram bot."""
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # ROAR monitoring components
        self.uniswap_monitor = None
        self.image_generator = None
        self.notification_chat_ids = set()
        self.monitoring_task = None
        
        # Initialize image generator with uploaded background
        background_path = "attached_assets/Party Energy with a Cartoon Twist_1751143536514.png"
        if os.path.exists(background_path):
            self.image_generator = NotificationImageGenerator(background_path)
            logger.info("Loaded custom background image for notifications")
        else:
            logger.warning("Background image not found")
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command handlers only - no message handlers."""
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # ROAR monitoring commands (main functionality)
        self.application.add_handler(CommandHandler("roar_status", self.roar_status_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        if not update.message:
            return
            
        welcome_message = (
            "🐱 *Welcome to Roaring Kitty Monitor Bot!*\n\n"
            "I monitor the real ROAR token liquidity pool 24/7 and provide custom notifications.\n\n"
            "*Commands:*\n"
            "• `/roar_status` - Get current token status with custom image\n"
            "• `/subscribe` - Enable automatic buy notifications\n"
            "• `/unsubscribe` - Disable notifications\n"
            "• `/help` - Show detailed help\n\n"
            "*Monitoring:* `0xD8C978de79E12728e38aa952a6cB4166F891790f`\n\n"
            "Bot automatically tracks all buys and displays remaining tokens on your custom party background!"
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        if not update.message:
            return
            
        help_message = (
            "🐱 *Roaring Kitty Monitor Bot Help*\n\n"
            "*Available Commands:*\n"
            "• `/roar_status` - Get current token status with custom image\n"
            "• `/subscribe` - Enable automatic buy notifications\n"
            "• `/unsubscribe` - Disable notifications\n\n"
            "*Features:*\n"
            "• 24/7 real-time ROAR buy detection\n"
            "• Custom notification images with your party background\n"
            "• Remaining token count display\n"
            "• Authentic DexScreener data integration\n\n"
            "*Monitoring Contract:*\n"
            "`0xD8C978de79E12728e38aa952a6cB4166F891790f`\n\n"
            "The bot automatically tracks all buy transactions and shows remaining tokens on your custom party background image."
        )
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )

    async def roar_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /roar_status command."""
        if not update.message:
            return
            
        if not self.uniswap_monitor:
            await update.message.reply_text("⏳ *Monitoring starting up...*", parse_mode=ParseMode.MARKDOWN)
            return

        try:
            stats = await self.uniswap_monitor.get_current_stats()
            
            # Format the status message
            if stats:
                roar_tokens = stats.get('roar_tokens_left', 0)
                message = f"🐱 *ROAR Token Status*\n\n📊 *Tokens Left:* {roar_tokens:,.0f} ROAR"
                
                # Generate custom image if available
                if self.image_generator and roar_tokens > 0:
                    try:
                        image_data = self.image_generator.create_notification_image(roar_tokens)
                        if image_data:
                            await update.message.reply_photo(
                                photo=image_data,
                                caption=message,
                                parse_mode=ParseMode.MARKDOWN
                            )
                            return
                    except Exception as e:
                        logger.error(f"Failed to generate status image: {e}")
                
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ *Unable to fetch current status*", parse_mode=ParseMode.MARKDOWN)
                
        except Exception as e:
            logger.error(f"Error getting ROAR status: {e}")
            await update.message.reply_text("❌ *Error fetching status*", parse_mode=ParseMode.MARKDOWN)

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /subscribe command."""
        if not update.effective_chat:
            return
            
        chat_id = update.effective_chat.id
        self.notification_chat_ids.add(chat_id)
        
        await update.message.reply_text("🔔 *Subscribed to ROAR buy notifications!*", parse_mode=ParseMode.MARKDOWN)
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /unsubscribe command."""
        if not update.effective_chat:
            return
            
        chat_id = update.effective_chat.id
        self.notification_chat_ids.discard(chat_id)
        
        await update.message.reply_text("🔕 *Unsubscribed from notifications*", parse_mode=ParseMode.MARKDOWN)
    
    async def send_buy_notification(self, roar_tokens_left: float, buy_amount: float = 0, price_impact: float = 0):
        """Send buy notification to all subscribed chats."""
        if not self.notification_chat_ids:
            return
        
        # Format numbers for display
        if roar_tokens_left >= 1000000:
            roar_display = f"{roar_tokens_left/1000000:.2f}M"
        elif roar_tokens_left >= 1000:
            roar_display = f"{roar_tokens_left/1000:.2f}K"
        else:
            roar_display = f"{roar_tokens_left:.0f}"
        
        message = f"🚀 *ROAR Buy Detected!*\n\n📊 *Tokens Left:* {roar_display} ROAR"
        
        # Generate custom notification image
        image_data = None
        if self.image_generator:
            try:
                image_data = self.image_generator.create_notification_image(roar_tokens_left, buy_amount, price_impact)
            except Exception as e:
                logger.error(f"Failed to generate notification image: {e}")
        
        # Send to all subscribed chats
        for chat_id in self.notification_chat_ids.copy():
            try:
                if image_data:
                    image_data.seek(0)  # Reset stream position
                    await self.application.bot.send_photo(
                        chat_id=chat_id,
                        photo=image_data,
                        caption=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
            except Exception as e:
                logger.error(f"Failed to send notification to chat {chat_id}: {e}")
                # Remove invalid chat_id
                self.notification_chat_ids.discard(chat_id)

    async def _auto_start_monitoring(self):
        """Automatically start ROAR monitoring when bot launches."""
        try:
            # Initialize DexScreener monitor
            self.uniswap_monitor = DexScreenerMonitor(
                token_address="0xD8C978de79E12728e38aa952a6cB4166F891790f",
                notification_callback=self.send_buy_notification
            )
            
            # Initialize and start monitoring
            if await self.uniswap_monitor.initialize():
                self.monitoring_task = asyncio.create_task(self.uniswap_monitor.start_monitoring())
                logger.info("ROAR token monitoring started automatically on bot launch")
            else:
                logger.error("Failed to initialize ROAR monitoring on startup")
                
        except Exception as e:
            logger.error(f"Error starting automatic monitoring: {e}")

    def run(self):
        """Start the bot."""
        logger.info("Bot is starting...")
        
        # Auto-start monitoring when bot launches
        async def post_init(application):
            await self._auto_start_monitoring()
        
        self.application.post_init = post_init
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)