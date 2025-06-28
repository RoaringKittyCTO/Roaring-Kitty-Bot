"""
Enhanced Telegram bot handler for Python code execution and ROAR token monitoring.
"""

import logging
import html
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from code_executor import CodeExecutor
from dexscreener_monitor import DexScreenerMonitor
from image_generator import NotificationImageGenerator

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        """Initialize the Telegram bot."""
        self.token = token
        self.code_executor = CodeExecutor()
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
        """Setup command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("run", self.run_command))
        
        # ROAR monitoring commands
        self.application.add_handler(CommandHandler("start_roar", self.start_roar_command))
        self.application.add_handler(CommandHandler("stop_roar", self.stop_roar_command))
        self.application.add_handler(CommandHandler("roar_status", self.roar_status_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        
        # Message handler for code blocks
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        welcome_message = (
            "🐍 *Welcome to Python REPL & ROAR Monitor Bot!*\n\n"
            "I can execute Python code safely and monitor ROAR token buys.\n\n"
            "*Python Commands:*\n"
            "• `/run <code>` - Execute Python code\n"
            "• `/help` - Show help message\n\n"
            "*Roaring Kitty Monitoring:*\n"
            "• `/start_roar` - Monitor real Roaring Kitty token\n"
            "• `/roar_status` - Check current token status\n"
            "• `/subscribe` - Get buy notifications\n\n"
            "*Example:*\n"
            "`/run print('Hello, World!')`\n\n"
            "Send code in backticks or code blocks for execution."
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_message = (
            "🔧 *Bot Help*\n\n"
            "*Python REPL Commands:*\n"
            "• `/run <code>` - Execute Python code\n\n"
            "*ROAR Monitoring Commands:*\n"
            "• `/start_roar` - Start ROAR pool monitoring\n"
            "• `/stop_roar` - Stop monitoring\n"
            "• `/roar_status` - Get current pool status\n"
            "• `/subscribe` - Subscribe to buy notifications\n"
            "• `/unsubscribe` - Unsubscribe from notifications\n\n"
            "*Features:*\n"
            "• Safe Python code execution\n"
            "• Real-time ROAR buy detection\n"
            "• Custom notification images\n"
            "• Pool status tracking\n\n"
            "*Usage Examples:*\n"
            "`/run 2 + 2`\n"
            "```python\n"
            "for i in range(3):\n"
            "    print(f'Number: {i}')\n"
            "```"
        )
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def run_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /run command."""
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide Python code to execute.\n"
                "Example: `/run print('Hello, World!')`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        code = ' '.join(context.args)
        await self._execute_and_reply(update, code)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages (potential code blocks)."""
        if not update.message or not update.message.text:
            return
            
        message_text = update.message.text
        
        # Check for code blocks (triple backticks)
        if message_text.startswith('```') and message_text.endswith('```'):
            # Extract code from code block
            lines = message_text.split('\n')
            if len(lines) > 1:
                # Remove first line if it contains language specification
                if lines[0].strip() in ['```python', '```py', '```']:
                    lines = lines[1:]
                # Remove last line with closing backticks
                if lines[-1].strip() == '```':
                    lines = lines[:-1]
                
                code = '\n'.join(lines)
                await self._execute_and_reply(update, code)
            return
        
        # Check for inline code (single backticks)
        if message_text.startswith('`') and message_text.endswith('`'):
            code = message_text[1:-1]
            await self._execute_and_reply(update, code)
            return
        
        # If it looks like Python code, try to execute it
        python_keywords = ['print', 'import', 'def', 'class', 'for', 'while', 'if', '=']
        if any(keyword in message_text.lower() for keyword in python_keywords):
            await self._execute_and_reply(update, message_text)
        else:
            await update.message.reply_text(
                "🤔 This doesn't look like Python code. Use `/run <code>` or wrap your code in backticks.\n"
                "Type `/help` for more information."
            )
    
    async def _execute_and_reply(self, update: Update, code: str):
        """Execute code and send the result back to the user."""
        # Show typing indicator
        await update.message.chat.send_action('typing')
        
        try:
            result = self.code_executor.execute(code)
            
            if result['success']:
                output = result['output']
                if output.strip():
                    # Format output for Telegram
                    formatted_output = f"✅ *Output:*\n```\n{html.escape(output)}\n```"
                else:
                    formatted_output = "✅ *Code executed successfully* (no output)"
                
                await update.message.reply_text(
                    formatted_output,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                error_message = result['error']
                formatted_error = f"❌ *Error:*\n```\n{html.escape(error_message)}\n```"
                
                await update.message.reply_text(
                    formatted_error,
                    parse_mode=ParseMode.MARKDOWN
                )
        
        except Exception as e:
            logger.error(f"Unexpected error during code execution: {e}")
            await update.message.reply_text(
                f"❌ *Unexpected error:*\n```\n{html.escape(str(e))}\n```",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def start_roar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start_roar command to start ROAR monitoring."""
        try:
            # Initialize DexScreener monitor for real Roaring Kitty token
            roaring_kitty_address = "0xD8C978de79E12728e38aa952a6cB4166F891790f"
            self.uniswap_monitor = DexScreenerMonitor(
                token_address=roaring_kitty_address,
                notification_callback=self.send_buy_notification
            )
            
            # Start monitoring in background
            if self.monitoring_task:
                self.monitoring_task.cancel()
            
            self.monitoring_task = asyncio.create_task(self.uniswap_monitor.start_monitoring())
            
            await update.message.reply_text(
                "✅ *Roaring Kitty Monitoring Started*\n\n"
                f"🐱 Token: `{roaring_kitty_address[:8]}...`\n"
                "📊 Using DexScreener API for real-time data\n"
                "🔔 Use `/subscribe` for buy notifications\n\n"
                "I'll monitor the real Roaring Kitty token and show remaining tokens with your custom image!",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Failed to start ROAR monitoring: {e}")
            await update.message.reply_text(
                f"❌ Failed to start monitoring: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def stop_roar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /stop_roar command."""
        if self.uniswap_monitor:
            self.uniswap_monitor.stop_monitoring()
            if self.monitoring_task:
                self.monitoring_task.cancel()
            
            await update.message.reply_text("🛑 *ROAR monitoring stopped*", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ No monitoring is currently active", parse_mode=ParseMode.MARKDOWN)
    
    async def roar_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /roar_status command."""
        if not self.uniswap_monitor:
            await update.message.reply_text("❌ No monitoring is active. Use `/start_roar` to begin.", parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            stats = await self.uniswap_monitor.get_current_stats()
            roar_left = stats.get('roar_tokens_left', 0)
            
            # Format the number
            if roar_left >= 1000000:
                roar_display = f"{roar_left/1000000:.2f}M"
            elif roar_left >= 1000:
                roar_display = f"{roar_left/1000:.2f}K"
            else:
                roar_display = f"{roar_left:.2f}"
            
            status_message = (
                "📊 *Current ROAR Pool Status*\n\n"
                f"🚀 ROAR Tokens Left: *{roar_display}*\n"
                f"📈 Status: {stats.get('status', 'unknown')}\n"
                f"🔔 Subscribers: {len(self.notification_chat_ids)}"
            )
            
            await update.message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN)
            
            # Send custom image with ROAR information
            if self.image_generator:
                try:
                    image_data = self.image_generator.create_notification_image(roar_left)
                    await update.message.reply_photo(
                        photo=image_data,
                        caption=f"ROAR Pool Status: {roar_display} tokens remaining"
                    )
                except Exception as e:
                    logger.error(f"Failed to generate status image: {e}")
            
        except Exception as e:
            logger.error(f"Failed to get ROAR status: {e}")
            await update.message.reply_text(f"❌ Failed to get pool status: {str(e)}", parse_mode=ParseMode.MARKDOWN)
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /subscribe command."""
        if not update.effective_chat:
            return
            
        chat_id = update.effective_chat.id
        self.notification_chat_ids.add(chat_id)
        
        await update.message.reply_text(
            "🔔 *Subscribed to ROAR buy notifications!*\n\n"
            "You'll receive custom images showing remaining ROAR tokens when new buys happen.\n"
            "Your GameStop/ROAR party image will be used as the background!",
            parse_mode=ParseMode.MARKDOWN
        )
    
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
            roar_display = f"{roar_tokens_left:.2f}"
        
        message = f"🚀 *New ROAR Buy Detected!*\n\n"
        message += f"💰 ROAR Left: *{roar_display}*\n"
        
        if buy_amount > 0:
            message += f"📈 Buy Amount: `{buy_amount:.2f} ROAR`\n"
        
        if price_impact > 0:
            message += f"📊 Price Impact: `{price_impact:.2f}%`\n"
        
        # Generate notification image with your uploaded background
        image_data = None
        if self.image_generator:
            try:
                image_data = self.image_generator.create_notification_image(
                    roar_tokens_left, buy_amount if buy_amount > 0 else None, price_impact if price_impact > 0 else None
                )
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