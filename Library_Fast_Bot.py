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
import random
import string
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
import telegram.error


class TelegramBot:
    debug_user_data = False

    def __init__(self, token: Optional[str] = None):
        """Initialize the Telegram bot with optional token parameter."""
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.start_message = "Hello! I'm a bot."
        self.start_markup: Optional[InlineKeyboardMarkup] = None  # Inline buttons under start message
        self.reply_markup: Optional[ReplyKeyboardMarkup] = None  # Reply keyboard buttons
        self.message_handlers: Dict[str, Union[str, Callable]] = {}  # Text message handlers
        self.button_handlers: Dict[str, Union[str, Callable]] = {}  # Button click handlers
        self.commands: Dict[str, Callable] = {}  # Command handlers
        self.command_hints: Dict[str, str] = {}  # Command descriptions for /help
        self.reply_keyboards: Dict[str, List[Tuple[str, str]]] = {}  # Reply keyboards
        self.under_message_buttons: Dict[str, List[Tuple[str, str]]] = {}  # Inline buttons under messages
        self.reply_messages: Dict[str, Union[str, Callable]] = {}  # Responses for reply buttons
        self.button_history: Dict[int, List[Dict[str, Any]]] = {}  # User button navigation history
        self.global_response: Optional[Union[str, Callable]] = None  # Global fallback response
        self.application: Optional[Application] = None  # Main bot application
        self.last_message: Optional[str] = None  # Last received message
        self.message_checkers: Dict[str, Callable] = {}  # Special message validators
        self.user_sessions: Dict[int, Dict[str, Any]] = {}  # User-specific data storage
        self.button_groups: Dict[str, List[Tuple[str, str]]] = {}  # Groups of related buttons

    def clearBtn(self) -> None:
        """Remove all buttons (both inline and reply keyboards) from the bot."""
        self.start_markup = None
        self.reply_markup = None
        self.reply_keyboards.clear()
        self.under_message_buttons.clear()
        self.reply_messages.clear()
        self.button_history.clear()

    def clearCommand(self) -> None:
        """Remove all registered commands from the bot."""
        self.commands.clear()
        self.command_hints.clear()

    def clearAll(self) -> None:
        """Completely reset the bot - remove all buttons, commands and handlers."""
        self.clearBtn()
        self.clearCommand()
        self.message_handlers.clear()
        self.button_handlers.clear()
        self.global_response = None
        self.message_checkers.clear()
        self.user_sessions.clear()
        self.button_groups.clear()

    async def add_button(self, button_text: str, response: Union[str, Callable],
                         after_message: Optional[str] = None,
                         update: Optional[Update] = None,
                         context: Optional[ContextTypes.DEFAULT_TYPE] = None,
                         inline: bool = False) -> None:
        """
        Add a button to the interface with error handling
        Args:
            button_text: Text displayed on the button (must be non-empty)
            response: Response when button is clicked (text or callback, must be non-empty for inline buttons)
            after_message: Message that triggers these buttons (must be specified)
            update: Telegram update object (optional)
            context: Callback context (optional)
            inline: Whether to create inline button (default False)
        """
        if not after_message:
            raise ValueError("after_message must be specified")

        if not button_text:
            raise ValueError("button_text cannot be empty")

        if inline and not response:
            raise ValueError("response cannot be empty for inline buttons")

        try:
            if inline:
                # For inline buttons
                if after_message.lower() not in self.under_message_buttons:
                    self.under_message_buttons[after_message.lower()] = []

                callback_data = f"btn_{self._generate_callback()}"
                self.under_message_buttons[after_message.lower()].append((button_text, callback_data))

                # Store the handler with proper response
                self.button_handlers[callback_data] = response if response else button_text.lower()
            else:
                # For reply keyboard buttons
                if after_message not in self.reply_keyboards:
                    self.reply_keyboards[after_message] = []

                self.reply_keyboards[after_message].append((button_text, response))
                self.reply_messages[button_text.lower()] = response if response else " "

            # Update interface if update context is provided
            if update is not None and context is not None:
                await self._update_interface(update, context, inline)
        except Exception as e:
            print(f"Error adding button: {e}")

    async def _update_interface(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                inline: bool = False) -> None:
        """
        Update the interface with current buttons
        Args:
            update: Telegram update object
            context: Callback context
            inline: Whether to update inline buttons (default False)
        """
        try:
            if inline:
                if update.message.text.lower() in self.under_message_buttons:
                    buttons = self.under_message_buttons[update.message.text.lower()]
                    keyboard = [[InlineKeyboardButton(btn, callback_data=cb) for btn, cb in buttons]]

                    # Remove previous message with buttons if exists
                    if update.message.reply_markup:
                        try:
                            await context.bot.delete_message(
                                chat_id=update.effective_chat.id,
                                message_id=update.message.message_id
                            )
                        except:
                            pass

                    # Send new message with buttons
                    await update.message.reply_text(
                        text=update.message.text if update.message.text.strip() else " ",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            else:
                if update.message.text in self.reply_keyboards:
                    buttons = self.reply_keyboards[update.message.text]
                    keyboard = [[KeyboardButton(btn)] for btn, _ in buttons]

                    # Remove previous keyboard if exists
                    try:
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=update.message.message_id
                        )
                    except:
                        pass

                    # Send new keyboard
                    await update.message.reply_text(
                        text=update.message.text if update.message.text.strip() else " ",
                        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                    )
        except telegram.error.BadRequest as e:
            if "Text must be non-empty" not in str(e):
                print(f"Error updating interface: {e}")
        except Exception as e:
            print(f"Error updating interface: {e}")

    def clickStart(self, text: str) -> None:
        """Set simple start message without any buttons."""
        self.start_message = text
        self.start_markup = None
        self.reply_markup = None

    def clickStartUnderBtn(self, text: str, *buttons: Tuple[str, str]) -> None:
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

    def clickStartBtn(self, text: str, *buttons: Union[str, Tuple[str, str]]) -> None:
        """Set start message with reply keyboard buttons."""
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

    def clearCommand(self, command: str) -> None:
        """Remove a specific command from the bot."""
        command = command.lower().lstrip('/')
        self.commands.pop(command, None)
        self.command_hints.pop(command, None)

    def del_btn(self, message_text: Optional[str] = None) -> Callable:
        """
        Returns a function to remove buttons under a message
        Args:
            message_text: Specific message to remove buttons from (None for all)
        Returns:
            Async function that removes the buttons
        """

        async def _delete_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
            if message_text:
                # Remove buttons for specific message
                self.under_message_buttons.pop(message_text.lower(), None)
            else:
                # Remove all message buttons
                self.under_message_buttons.clear()

            # Remove current message with buttons if exists
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except:
                pass

            return "Buttons removed"  # Can return empty string

        return _delete_buttons

    def del_reply_keyboard(self) -> Callable:
        """Returns a function that removes reply keyboard"""

        async def _delete_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
            # Send empty keyboard to remove current one
            await update.message.reply_text(
                text=" ",
                reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
            )
            return ""

        return _delete_keyboard

    def if_message(self, message_text: str, response: Optional[Union[str, Callable]] = None) -> Union[bool, None]:
        """
        Register message handler or check last message
        Args:
            message_text: Text to match
            response: Response handler (text or callback)
        Returns:
            bool if checking last message, None if registering handler
        """
        if response is not None:
            self.message_handlers[message_text.lower()] = response
            return None
        return self.last_message and self.last_message.lower() == message_text.lower()

    def if_message_addBtn(self, message_text: str, response_text: str) -> None:
        """
        Add reply buttons for specific message without 'Please choose' prompt
        Args:
            message_text: Trigger message text
            response_text: Response text to show with buttons
        """
        self.reply_messages[message_text.lower()] = response_text
        if response_text not in self.reply_keyboards:
            self.reply_keyboards[response_text] = []

    def if_message_addBtn(self, message_text: str, response_text: str) -> None:
        """Add reply buttons for specific message without 'Please choose' prompt."""
        self.reply_messages[message_text.lower()] = response_text
        if response_text not in self.reply_keyboards:
            self.reply_keyboards[response_text] = []

    def add_button(self, button_text: str, response: Union[str, Callable],
                   after_message: Optional[str] = None,
                   update: Optional[Update] = None,
                   context: Optional[ContextTypes.DEFAULT_TYPE] = None,
                   inline: bool = False) -> None:
        """Add button to the interface"""
        if after_message is None:
            raise ValueError("after_message must be specified")

        if inline:
            if after_message not in self.under_message_buttons:
                self.under_message_buttons[after_message.lower()] = []
            callback_data = f"btn_{self._generate_callback()}"
            self.under_message_buttons[after_message.lower()].append((button_text, callback_data))
            self.button_handlers[callback_data] = response
        else:
            if after_message not in self.reply_keyboards:
                self.reply_keyboards[after_message] = []
            self.reply_keyboards[after_message].append((button_text, response))
            self.reply_messages[button_text.lower()] = response

        if update is not None and context is not None:
            self._update_interface(update, context, inline)

    def _generate_callback(self) -> str:
        """Generate unique callback identifier"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    async def _update_interface(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                inline: bool = False) -> None:
        """Update the interface with current buttons"""
        current_text = update.message.text

        if inline:
            if current_text.lower() in self.under_message_buttons:
                buttons = self.under_message_buttons[current_text.lower()]
                keyboard = [[InlineKeyboardButton(btn, callback_data=cb) for btn, cb in buttons]]
                await update.message.reply_text(
                    current_text,
                    reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            if current_text in self.reply_keyboards:
                buttons = self.reply_keyboards[current_text]
                keyboard = [[KeyboardButton(btn)] for btn, _ in buttons]
                await update.message.reply_text(
                    "Interface updated:",
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # Новые функции для управления пользовательскими сессиями
    def set_user_data(self, user_id: int, key: str, value: Any) -> None:
        """Store user-specific data"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id][key] = value

    def get_user_data(self, user_id: int, key: str, default: Any = None) -> Any:
        """Retrieve user-specific data"""
        return self.user_sessions.get(user_id, {}).get(key, default)

    # Новые функции для работы с группами кнопок
    def create_button_group(self, group_name: str) -> None:
        """Create a named button group"""
        self.button_groups[group_name] = []

    def add_to_button_group(self, group_name: str, button_text: str, response: Union[str, Callable]) -> str:
        """Add button to a group and return callback_data"""
        if group_name not in self.button_groups:
            self.create_button_group(group_name)
        callback_data = f"grp_{group_name}_{len(self.button_groups[group_name])}"
        self.button_groups[group_name].append((button_text, callback_data))
        self.button_handlers[callback_data] = response
        return callback_data


    def add_buttonUnderMessage(self, message_text: str, *buttons: Tuple[str, str]) -> None:
        """
        Add inline buttons under specific message

        Args:
            message_text: The message text to add buttons under
            buttons: Up to 6 buttons as (button_text, callback_data) tuples
        """
        if not 1 <= len(buttons) <= 6:
            raise ValueError("You can add 1 to 6 buttons per message")

        self.under_message_buttons[message_text.lower()] = buttons

        # Auto-register button handlers
        for _, callback in buttons:
            if callback not in self.button_handlers:
                self.button_handlers[callback] = callback

    def _update_interface(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Internal method to update the interface"""
        current_text = update.message.text
        if current_text in self.reply_keyboards:
            buttons = self.reply_keyboards[current_text]
            keyboard = [[KeyboardButton(btn)] for btn, _ in buttons]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            update.message.reply_text(
                "Interface updated:",
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

    # --------------- Handler Functions ---------------
    async def _process_response(self, response: Union[str, Callable],
                                update: Update,
                                context: ContextTypes.DEFAULT_TYPE) -> str:
        """Process response that can be either text or callback."""
        if callable(response):
            return await response(update, context)
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
        try:
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

            # Handle under-message buttons
            if user_text_lower in self.under_message_buttons:
                buttons = self.under_message_buttons[user_text_lower]
                keyboard = [[InlineKeyboardButton(btn, callback_data=cb)] for btn, cb in buttons]
                await update.message.reply_text(
                    user_text,
                    reply_markup=InlineKeyboardMarkup(keyboard))
                return

            # Handle global response
            if self.global_response is not None:
                response = await self._process_response(self.global_response, update, context)
                if response and str(response).strip():  # Проверяем, что response не пустой
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
                        reply_markup=previous_state.get('markup'))
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
                    # Отправляем сообщение только если response не пустой
                    if response and str(response).strip():
                        await update.message.reply_text(
                            response,
                            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                    else:
                        await update.message.reply_text(
                            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                else:
                    if response and str(response).strip():  # Проверяем, что response не пустой
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
                    # Отправляем сообщение только если trigger_msg не пустой
                    if trigger_msg and str(trigger_msg).strip():
                        await update.message.reply_text(
                            trigger_msg,
                            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                    else:
                        await update.message.reply_text(
                            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                    return

            # Handle other message handlers
            if user_text_lower in self.message_handlers:
                response = await self._process_response(self.message_handlers[user_text_lower], update, context)
                if response and str(response).strip():  # Проверяем, что response не пустой
                    await update.message.reply_text(response)
            else:
                await update.message.reply_text("I don't understand this command.")

        except Exception as e:
            if "Text must be non-empty" not in str(e):  # Игнорируем только ошибку пустого текста
                print(f"Error in handle_message: {e}")

    async def setup_commands_menu(self, bot) -> None:
        """Set up bot commands menu."""
        if self.command_hints:
            commands = [BotCommand(command, description) for command, description in self.command_hints.items()]
            await bot.set_my_commands(commands)

    async def setup_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Command handler to setup commands menu."""
        await self.setup_commands_menu(context.bot)
        await update.message.reply_text("Commands menu has been updated.")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик ошибок."""
        if isinstance(context.error, telegram.error.BadRequest) and "Text must be non-empty" in str(context.error):
            return  # Игнорируем эту ошибку
        print(f"Exception while handling an update: {context.error}")

    # --------------- Bot Execution ---------------
    def run(self) -> None:
        """Start the bot and begin polling for updates."""
        if not self.token:
            raise ValueError("Token is not set!")

        print("Bot is starting...")
        self.application = Application.builder().token(self.token).build()

        # Add error handler
        self.application.add_error_handler(self.error_handler)

        # Register command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("setup", self.setup_commands))

        if self.commands:
            self.application.add_handler(MessageHandler(filters.COMMAND, self.handle_command))

        if self.button_handlers:
            self.application.add_handler(CallbackQueryHandler(self.button_click))

        # Register text message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        print("Bot is running...")
        self.application.run_polling()

# Create bot instance for export
if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()

# Global bot instance
bot = TelegramBot()