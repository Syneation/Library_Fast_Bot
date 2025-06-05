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
from typing import Dict, List, Tuple, Optional, Union, Any, Callable


class TelegramBot:
    debug_user_data = False

    def __init__(self, token: Optional[str] = None):
        """Initialize the Telegram bot with optional token parameter."""
        self.token = token or os.getenv("TOKEN")
        self.start_message = "Hello! I'm a bot."
        self.start_markup: Optional[InlineKeyboardMarkup] = None
        self.reply_markup: Optional[ReplyKeyboardMarkup] = None
        self.message_handlers: Dict[str, Union[str, Callable]] = {}
        self.button_handlers: Dict[str, Union[str, Tuple[str, List[Tuple[str, str]]], Callable]] = {}
        self.reply_keyboards: Dict[str, List[Tuple[str, str]]] = {}
        self.commands: Dict[str, Union[str, Callable]] = {}
        self.command_hints: Dict[str, str] = {}
        self.reply_messages: Dict[str, Union[str, Callable]] = {}
        self.button_history: Dict[int, List[Dict[str, Any]]] = {}
        self.global_response: Optional[Union[str, Callable]] = None
        self.application: Optional[Application] = None
        self.last_message: Optional[str] = None
        self.message_checkers: Dict[str, Callable] = {}

    def clickStartBot(self, text: str) -> None:
        """Set simple start message without buttons."""
        self.start_message = text
        self.start_markup = None
        self.reply_markup = None

    def clickStartBotUnderBtn(self, text: str, *buttons: Tuple[str, str]) -> None:
        """Set start message with inline buttons under it."""
        self.start_message = text
        if buttons and len(buttons) <= 6:
            keyboard = [
                [InlineKeyboardButton(btn_text, callback_data=callback_data)]
                for btn_text, callback_data in buttons[:6]
            ]
            self.start_markup = InlineKeyboardMarkup(keyboard)
            for _, callback_data in buttons:
                self.button_handlers[callback_data] = callback_data
        else:
            self.start_markup = None

    def clickStartBotBtn(self, text: str, *buttons: Union[str, Tuple[str, str]]) -> None:
        """
        Set start message with reply keyboard buttons.
        Buttons can be either simple (text) or with follow-up buttons (text, response, buttons).
        """
        self.start_message = text
        if buttons and len(buttons) <= 6:
            keyboard = [
                [KeyboardButton(btn_text if isinstance(btn_text, str) else btn_text[0])]
                for btn_text in buttons[:6]
            ]
            self.reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            for button in buttons:
                if isinstance(button, tuple) and len(button) >= 2:
                    btn_text, response = button[:2]
                    self.reply_messages[btn_text.lower()] = response

                    if len(button) == 3 and isinstance(button[2], list):
                        self.reply_keyboards[response] = button[2]
                        for sub_btn, sub_response in button[2]:
                            self.reply_messages[sub_btn.lower()] = sub_response
        else:
            self.reply_markup = None

    def if_message(self, message_text: str, response: Optional[Union[str, Callable]] = None) -> bool:
        """
        Dual function:
        1. If response is specified - registers a handler (text or callback)
           Callback signature: func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str
        2. Returns True if the last message matches message_text
        """
        if response is not None:
            self.message_handlers[message_text.lower()] = response

        if self.last_message is None:
            return False
        return self.last_message.lower() == message_text.lower()

    def add_message_checker(self, message_text: str, callback: Callable) -> None:
        """Adds a custom check for a message"""
        self.message_checkers[message_text.lower()] = callback

    def add_button(self, button_text: str, after_message: str, response: Union[str, Callable],
                   update: Optional[Update] = None, context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> None:
        """
        Улучшенный метод добавления кнопки с возможностью немедленного обновления интерфейса

        Args:
            button_text: Текст на кнопке
            after_message: Сообщение, после которого показывается кнопка
            response: Ответ при нажатии (текст или функция)
            update: Объект Update (если нужно немедленное обновление)
            context: Объект Context (если нужно немедленное обновление)
        """
        # Добавляем кнопку в систему
        if after_message not in self.reply_keyboards:
            self.reply_keyboards[after_message] = []

        self.reply_keyboards[after_message].append((button_text, response))
        self.reply_messages[button_text.lower()] = response

        # Если переданы update и context - обновляем интерфейс немедленно
        if update is not None and context is not None:
            self._update_interface(update, context)

    def _update_interface(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Внутренний метод для обновления интерфейса"""
        current_text = update.message.text
        if current_text in self.reply_keyboards:
            buttons = self.reply_keyboards[current_text]
            keyboard = [[KeyboardButton(btn)] for btn, _ in buttons]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            update.message.reply_text(
                "Интерфейс обновлен:",
                reply_markup=reply_markup
            )

    def add_command(self, command: str, response: Union[str, Callable]) -> None:
        """Add handler for bot command (text or callback)."""
        self.commands[command] = response
        if command not in self.command_hints:
            self.command_hints[command] = response[:100] if isinstance(response, str) else command

    def add_hint_command(self, command: str, hint: str) -> None:
        """Add description for bot command (shown in /help)."""
        self.command_hints[command] = hint
        if command not in self.commands:
            self.commands[command] = ""

    async def _process_response(self, response: Union[str, Callable],
                                update: Update,
                                context: ContextTypes.DEFAULT_TYPE) -> str:
        """Process response that can be either text or callback."""
        if callable(response):
            return response(update, context)
        return response

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user_id = update.effective_user.id
        self.button_history[user_id] = []

        await self.setup_commands_menu(context.bot)

        reply_text = await self._process_response(self.start_message, update, context)

        if self.start_markup:
            await update.message.reply_text(reply_text, reply_markup=self.start_markup)
        elif self.reply_markup:
            await update.message.reply_text(reply_text, reply_markup=self.reply_markup)
        else:
            await update.message.reply_text(reply_text)

    async def button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline button clicks."""
        query = update.callback_query
        await query.answer()
        callback_data = query.data
        user = query.from_user

        if self.debug_user_data:
            user_info = (
                f"User clicked button: {callback_data}\n"
                f"Name: {user.full_name}\n"
                f"Username: @{user.username}" if user.username else "Username: Not specified"
            )
            print("\n" + "=" * 50)
            print(user_info)
            print("=" * 50 + "\n")

        if callback_data == "previous_menu":
            if user.id in self.button_history and self.button_history[user.id]:
                previous_state = self.button_history[user.id].pop()
                await query.edit_message_text(
                    text=previous_state['text'],
                    reply_markup=previous_state['markup']
                )
                return
            await query.edit_message_text(text="You're at the main menu")
            return

        if callback_data in self.button_handlers:
            response = self.button_handlers[callback_data]
            if user.id not in self.button_history:
                self.button_history[user.id] = []

            self.button_history[user.id].append({
                'text': query.message.text,
                'markup': query.message.reply_markup
            })

            if isinstance(response, tuple):
                text, buttons = response
                reply_text = await self._process_response(text, update, context)
                keyboard = [[InlineKeyboardButton(btn, callback_data=data)] for btn, data in buttons]
                await query.edit_message_text(
                    text=reply_text,
                    reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                reply_text = await self._process_response(response, update, context)
                await query.edit_message_text(text=reply_text)
        else:
            await query.edit_message_text(text="Unknown command")

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle bot commands."""
        command = update.message.text[1:].split()[0].lower()
        if command in self.commands:
            response = await self._process_response(self.commands[command], update, context)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Unknown command")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all text messages."""
        user_text = update.message.text
        self.last_message = user_text
        user_text_lower = user_text.lower()
        user = update.effective_user

        if self.debug_user_data:
            user_info = (
                f"User sent message: {user_text}\n"
                f"Name: {user.full_name}\n"
                f"Username: @{user.username}" if user.username else "Username: Not specified"
            )
            print("\n" + "=" * 50)
            print(user_info)
            print("=" * 50 + "\n")

        # Handle global response
        if self.global_response is not None:
            response = await self._process_response(self.global_response, update, context)
            await update.message.reply_text(response)
            return

        if user_text_lower in self.message_checkers:
            await self.message_checkers[user_text_lower](update, context)
            return

        # Handle back button
        if user_text_lower in ("back", "previous_menu"):
            if user.id in self.button_history and self.button_history[user.id]:
                previous_state = self.button_history[user.id].pop()
                await update.message.reply_text(
                    text=previous_state.get('text', "Previous menu"),
                    reply_markup=previous_state.get('markup')
                )
                return
            await update.message.reply_text("You're at the main menu")
            return

        # Handle exact matches
        if user_text_lower in self.reply_messages:
            response = await self._process_response(self.reply_messages[user_text_lower], update, context)

            if user.id not in self.button_history:
                self.button_history[user.id] = []

            self.button_history[user.id].append({
                'text': user_text,
                'markup': update.message.reply_markup
            })

            if response in self.reply_keyboards:
                buttons = self.reply_keyboards[response]
                keyboard = [[KeyboardButton(btn)] for btn, _ in buttons]
                await update.message.reply_text(
                    response,
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            else:
                await update.message.reply_text(response)
            return

        # Handle trigger messages
        for trigger_msg, buttons in self.reply_keyboards.items():
            if trigger_msg.lower() in user_text_lower:
                if user.id not in self.button_history:
                    self.button_history[user.id] = []

                self.button_history[user.id].append({
                    'text': user_text,
                    'markup': update.message.reply_markup
                })

                keyboard = [[KeyboardButton(btn)] for btn, _ in buttons]
                await update.message.reply_text(
                    "Please choose:",
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return

        # Handle other message handlers
        if user_text_lower in self.message_handlers:
            response = await self._process_response(self.message_handlers[user_text_lower], update, context)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("I don't understand this command.")

    async def setup_commands_menu(self, bot) -> None:
        """Set up bot commands menu."""
        if self.command_hints:
            commands = [BotCommand(command, description) for command, description in self.command_hints.items()]
            await bot.set_my_commands(commands)

    async def setup_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Command handler to setup commands menu."""
        await self.setup_commands_menu(context.bot)
        await update.message.reply_text("Commands menu has been updated.")

    def run(self) -> None:
        """Start the bot."""
        if not self.token:
            raise ValueError("Token is not set!")
        self.application = Application.builder().token(self.token).build()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("setup", self.setup_commands))

        if self.commands:
            self.application.add_handler(MessageHandler(filters.COMMAND, self.handle_command))

        if self.button_handlers:
            self.application.add_handler(CallbackQueryHandler(self.button_click))

        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        print("Bot is starting...")
        self.application.run_polling()


# Create bot instance for export
if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()

bot = TelegramBot()