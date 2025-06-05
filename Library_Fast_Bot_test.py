from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
import os
from typing import Dict, List, Tuple, Optional, Union, Any


class TelegramBot:

    debug_user_data = False

    def __init__(self, token: Optional[str] = None):
        """Initialize the Telegram bot with optional token parameter."""
        self.token = token or os.getenv("TOKEN")
        self.start_message = "Hello! I'm a bot."
        self.start_markup: Optional[InlineKeyboardMarkup] = None
        self.reply_markup: Optional[ReplyKeyboardMarkup] = None
        self.message_handlers: Dict[str, str] = {}
        self.button_handlers: Dict[str, Dict[str, Any]] = {}
        self.reply_keyboards: Dict[str, Dict[str, Any]] = {}
        self.commands: Dict[str, str] = {}
        self.command_hints: Dict[str, str] = {}
        self.reply_messages: Dict[str, Dict[str, Any]] = {}
        self.back_handlers: Dict[str, Dict[str, Any]] = {}  # Stores custom back handlers

    def clickStartBot(self, text: str) -> None:
        """Set simple start message without buttons."""
        self.start_message = text
        self.start_markup = None
        self.reply_markup = None

    def clickStartBotUnderBtn(self, **kwargs) -> None:
        """
        Set start message with inline buttons under it.
        Usage: text="Message", option1="callback1", option2="callback2", ...
        """
        self.start_message = kwargs.get('text', "Hello! I'm a bot.")
        buttons = [(k, v) for k, v in kwargs.items() if k != 'text']

        if buttons and len(buttons) <= 6:
            keyboard = [
                [InlineKeyboardButton(btn_text, callback_data=callback_data)]
                for btn_text, callback_data in buttons[:6]
            ]
            self.start_markup = InlineKeyboardMarkup(keyboard)
            for _, callback_data in buttons:
                self.button_handlers[callback_data] = {"text": f"You chose {callback_data}"}
        else:
            self.start_markup = None

    def clickStartBotBtn(self, **kwargs) -> None:
        """
        Set start message with reply keyboard buttons.
        Usage: text="Message", option1=dict(text="Answer1", buttons=[...]),
               option2="Answer2", ...
        """
        self.start_message = kwargs.get('text', "Hello! I'm a bot.")
        buttons = []

        for btn_text, value in kwargs.items():
            if btn_text == 'text':
                continue

            if isinstance(value, str):
                # Simple button: "option": "answer"
                buttons.append((btn_text, value))
                self.reply_messages[btn_text.lower()] = {"text": value}
            elif isinstance(value, dict):
                # Advanced button: "option": {"text": "...", "buttons": [...]}
                buttons.append((btn_text, value.get('text', btn_text)))
                self.reply_messages[btn_text.lower()] = value

                # Add back button to nested keyboards
                if 'buttons' in value:
                    if 'back_handler' in value:
                        back_data = f"back_{value['back_handler']}"
                        value['buttons'].append(("Back", back_data))
                    else:
                        value['buttons'].append(("Back", "previous_menu"))

        if buttons and len(buttons) <= 6:
            keyboard = [
                [KeyboardButton(btn_text)]
                for btn_text, _ in buttons[:6]
            ]
            self.reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        else:
            self.reply_markup = None

    def back_btn(self, back_id: str, return_text: str, buttons: List[Tuple[str, str]]) -> None:
        """
        Define custom back button behavior.
        Usage: back_btn("back1", "Main menu:", [("Option 1", "Response 1"), ("Option 2", "Response 2")])
        """
        self.back_handlers[f"back_{back_id}"] = {
            "text": return_text,
            "buttons": buttons
        }

    def add_button(self, **kwargs) -> None:
        """
        Add button with nested options and back functionality.
        Usage: trigger="trigger text",
               option1=dict(text="Answer1", buttons=[...], back_handler="back1"),
               option2="Answer2",
               ...
        """
        trigger = kwargs.get('trigger', '').lower()
        if not trigger:
            return

        if trigger not in self.reply_keyboards:
            self.reply_keyboards[trigger] = {"buttons": []}

        for btn_text, value in kwargs.items():
            if btn_text == 'trigger':
                continue

            if isinstance(value, str):
                # Simple button: "option": "answer"
                self.reply_keyboards[trigger]["buttons"].append((btn_text, value))
                self.reply_messages[btn_text.lower()] = {"text": value}
            elif isinstance(value, dict):
                # Advanced button with nested options
                self.reply_keyboards[trigger]["buttons"].append((btn_text, value.get('text', btn_text)))
                self.reply_messages[btn_text.lower()] = value

                # Add back button to nested keyboards
                if 'buttons' in value:
                    if 'back_handler' in value:
                        back_data = f"back_{value['back_handler']}"
                        value['buttons'].append(("Back", back_data))
                    else:
                        value['buttons'].append(("Back", "previous_menu"))

    def if_message(self, received_text: str, response_text: str) -> None:
        """Add handler for specific text messages."""
        self.message_handlers[received_text.lower()] = response_text

    def add_command(self, command: str, response: str) -> None:
        """Add handler for bot command."""
        self.commands[command] = response

    def add_hint_command(self, command: str, hint: str) -> None:
        """Add description for bot command (shown in /help)."""
        self.command_hints[command] = hint

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        if self.start_markup:
            await update.message.reply_text(
                self.start_message,
                reply_markup=self.start_markup
            )
        elif self.reply_markup:
            await update.message.reply_text(
                self.start_message,
                reply_markup=self.reply_markup
            )
        else:
            await update.message.reply_text(self.start_message)

    async def button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline button clicks."""
        query = update.callback_query
        await query.answer()
        callback_data = query.data

        # Print user info to console
        if (bot.debug_user_data):
            user = update.effective_user
            user_info = (
                f"User clicked button: {callback_data}\n"
                f"Name: {user.full_name}\n"
                f"Username: @{user.username}" if user.username else "Username: Not specified"
            )
            print("\n" + "=" * 50)
            print(user_info)
            print("=" * 50 + "\n")

        # Handle custom back buttons
        if callback_data.startswith("back_"):
            if callback_data in self.back_handlers:
                back_data = self.back_handlers[callback_data]
                keyboard = [
                    [InlineKeyboardButton(btn_text, callback_data=callback)]
                    for btn_text, callback in back_data["buttons"]
                ]
                await query.edit_message_text(
                    text=back_data["text"],
                    reply_markup=InlineKeyboardMarkup(keyboard))
                return

        # Handle standard back button
        if callback_data == "previous_menu":
            await query.edit_message_text(
                text=self.start_message,
                reply_markup=self.start_markup)
            return

        if callback_data in self.button_handlers:
            response = self.button_handlers[callback_data]

            if isinstance(response, dict) and 'buttons' in response:
                # Show buttons
                keyboard = [[InlineKeyboardButton(btn, callback_data=data)]
                            for btn, data in response['buttons']]
                await query.edit_message_text(
                    text=response.get('text', callback_data),
                    reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                # Simple text response
                await query.edit_message_text(
                    text=response.get('text', callback_data))
        else:
            await query.edit_message_text(text="Unknown command")

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle bot commands."""
        command = update.message.text[1:].split()[0].lower()
        if command in self.commands:
            await update.message.reply_text(self.commands[command])
        else:
            await update.message.reply_text("Unknown command")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all text messages."""
        user_text = update.message.text.lower()
        user = update.effective_user

        # Print user info to console
        if (bot.debug_user_data):
            # Print user info to console
            user_info = (
                f"User sent message: {update.message.text}\n"
                f"Name: {user.full_name}\n"
                f"Username: @{user.username}" if user.username else "Username: Not specified"
            )
            print("\n" + "=" * 50)
            print(user_info)
            print("=" * 50 + "\n")

        # Handle back button
        if user_text == "back" or user_text == "previous_menu":
            if self.reply_markup:
                await update.message.reply_text(
                    self.start_message,
                    reply_markup=self.reply_markup)
            else:
                await update.message.reply_text(self.start_message)
            return

        # Check exact matches first
        if user_text in self.reply_messages:
            response = self.reply_messages[user_text]

            if isinstance(response, dict) and 'buttons' in response:
                # Show buttons
                buttons = response['buttons']
                keyboard = [[KeyboardButton(btn)] for btn, _ in buttons]
                await update.message.reply_text(
                    response.get('text', "Please choose:"),
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            else:
                # Simple text response
                answer = response.get('text', response) if isinstance(response, dict) else response
                await update.message.reply_text(answer)
            return

        # Check trigger messages
        for trigger, data in self.reply_keyboards.items():
            if trigger.lower() in user_text:
                buttons = data.get('buttons', [])
                keyboard = [[KeyboardButton(btn)] for btn, _ in buttons]
                await update.message.reply_text(
                    data.get('text', "Please choose:"),
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return

        # Check other message handlers
        if user_text in self.message_handlers:
            await update.message.reply_text(self.message_handlers[user_text])
        else:
            await update.message.reply_text("I don't understand this command.")

    async def setup_commands(self, application: Application) -> None:
        """Set up bot commands menu."""
        if self.command_hints:
            commands = [
                BotCommand(command, description)
                for command, description in self.command_hints.items()
            ]
            await application.bot.set_my_commands(commands)

    def run(self) -> None:
        """Start the bot."""
        if not self.token:
            raise ValueError("Token is not set!")
        application = Application.builder().token(self.token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))

        if self.commands:
            application.add_handler(MessageHandler(filters.COMMAND, self.handle_command))

        if self.button_handlers:
            application.add_handler(CallbackQueryHandler(self.button_click))

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Set up commands menu
        application.add_handler(CommandHandler("setup", self.setup_commands))

        print("Bot is starting...")
        application.run_polling()

# Создаем экземпляр бота для экспорта
if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()

bot = TelegramBot()