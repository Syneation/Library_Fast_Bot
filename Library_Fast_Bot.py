import asyncio
import os

from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)

from typing import (
    Callable,
    Optional,
    Union,
    List,
)

class TelegramBot:
    """Initialize bot setting"""
    def __init__(self, token=None):
        self.token = token or os.getenv("TOKEN")
        self.start_message = "Hello, I'm Bot :)."
        self._initial_buttons = None # for save start  btn
        self._initial_buttons_inline = None # for save start btn inline
        self._initial_start_message = None # for save start msg
        self.last_message = {} # last message for delete or edit message

        self.debug_LBF_and_code = False

        self._processing_task = None  # Track the processing task
        self._should_process = True  # Control flag for processing loop

        self._current_update = None
        self._current_context = None
        self._current_chat_id = None

        # for debug chat_id, user_name, username and full_name
        self._tmp_chat_id = None
        self._tmp_user_name = None
        self._tmp_username = None
        self._tmp_full_name = None
        self._tmp_user_id = None

        self.debug_user_data = False
        self._current_user = None

        self.default_message = None
        self.is_default_send_msg = False
        self.repl_msg_user = False

        self.commands = {}
        self.command_hints = {}

        self._msg_to_send = None
        self._msg_to_send_answer = None
        self.pending_message = {} # For storing messages by chat_id
        self.message_callbacks = {}
        self.current_user_text = None
        self.message_handlers = []
        self.buttons = []
        self.inline = False # checking for buttons above the text or just buttons
        self.buttons_handlers = {} # for save callback_data

    # Wrapper to support functions without parameters
    def _wrap_callback(self, callback):
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Save context first
            self._current_update = update
            self._current_context = context
            self._current_user = update.effective_user

            # Determine chat_id from either message or callback_query
            if update.message:
                self._current_chat_id = update.message.chat_id
            elif update.callback_query and update.callback_query.message:
                self._current_chat_id = update.callback_query.message.chat_id
            else:
                self._current_chat_id = None

            try:
                if asyncio.iscoroutinefunction(callback):
                    result = await callback(update, context)
                else:
                    result = callback(update, context)
            except TypeError:
                if asyncio.iscoroutinefunction(callback):
                    result = await callback()
                else:
                    result = callback()

            await self._process_pending_message()
            return result

        return wrapped

    """After click start"""
    def start_bot(self, text):
        self.start_message = text

    """command before start"""
    def start_bot_btn(self, text: str, buttons: Union[Callable, list]):
        self.start_message = text
        self._initial_start_message = text
        self._initial_buttons_inline = False  # Explicitly set to False for regular buttons

        if buttons is not None:
            processed_buttons = []
            for item in buttons:
                if isinstance(item, tuple) and len(item) == 2:
                    btn_text, handler = item
                    processed_buttons.append((btn_text, btn_text))
                    # Register the handler properly
                    self.message_callbacks[btn_text.lower()] = (self._wrap_callback(handler), (), {})
                else:
                    # If just a string is passed
                    btn_text = item[0] if isinstance(item, tuple) else item
                    processed_buttons.append((btn_text, btn_text))
                    # Register a default handler
                    self.message_callbacks[btn_text.lower()] = (self._wrap_callback(lambda: None), (), {})

                    if len(processed_buttons) > 16:
                        raise ValueError("Error start_bot_btn: max 16 buttons!")

            self.buttons = processed_buttons
            self._initial_buttons = processed_buttons.copy()
            self.inline = False  # Ensure this is set to False for regular buttons

    """Inline buttons after start"""

    def start_bot_btn_inline(self, message: str, buttons: list):
        """Initialize bot with inline buttons menu that will be preserved on /start"""
        if not message.strip():
            raise ValueError("Message cannot be empty")

        # Save initial state
        self._initial_start_message = message
        self._initial_buttons_inline = True
        self._initial_buttons = []
        self._initial_button_handlers = {}  # Dictionary to store original handlers

        # Clear any existing button state
        self.buttons = []
        self.buttons_handlers.clear()
        self.inline = True

        # Process buttons
        for i, (btn_text, handler) in enumerate(buttons):
            callback_data = f"btn_{i}"
            self._initial_buttons.append((btn_text, callback_data))
            self._initial_button_handlers[callback_data] = handler  # Save original handler

        # Set current state to match initial state
        self.start_message = message
        self.buttons = self._initial_buttons.copy()

        # Register handlers with proper closure
        for callback_data, handler in self._initial_button_handlers.items():
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              func=handler, cb_data=callback_data):
                try:
                    self._current_update = update
                    self._current_context = context
                    if update.callback_query and update.callback_query.message:
                        self._current_chat_id = update.callback_query.message.chat_id

                    # Execute handler
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()

                    # Process pending messages
                    await self._process_pending_message()
                except Exception as e:
                    if self.debug_LBF_and_code:
                        print(f"Button handler error ({cb_data}): {e}")

            self.buttons_handlers[callback_data] = wrapper

    """Send And answerForMessage"""

    async def _send_message_ordered(self, chat_id: int, text: str, update: Update):
        """Sends messages in order with a delay"""
        if not chat_id:
            chat_id = self._tmp_chat_id # get chat id user

        await asyncio.sleep(0.3)  # Slight delay between messages
        await self._current_context.bot.send_message(chat_id=chat_id, text=text)

    def send_message(self, text: str, chat_id: int = None):
        """Orderly sending of messages"""
        chat_id = chat_id or self._current_chat_id

        if hasattr(self, '_current_context') and self._current_context:
            asyncio.create_task(self._send_message_ordered(chat_id, text, update=Update))

    async def stop(self):
        """Cleanup when bot stops"""
        self._should_process = False

        # Canceling the message processing task
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                if self.debug_LBF_and_code:
                    print(f"Error stopping message processor: {e}")

        # Clearing the queue
        if hasattr(self, '_message_queue') and self._message_queue:
            while not self._message_queue.empty():
                self._message_queue.get_nowait()
                self._message_queue.task_done()

        self._processing_task = None
        self._message_queue = None

    def answer_message(self, text: str, chat_id: int = None):
        """Sends answer"""
        if hasattr(self, '_current_update') and self._current_update:
            # if user input chat id
            if chat_id:
                asyncio.create_task(
                    self._current_context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_to_message_id=self._current_update.message.message_id
                    )
                )
            else:
                asyncio.create_task(
                    self._current_update.message.reply_text(
                        text=text,
                        reply_to_message_id=self._current_update.message.message_id
                    )
                )
        else:
            # else save msg for send later
            if chat_id:
                if chat_id not in self.pending_message:
                    self.pending_message[chat_id] = []
                self.pending_message[chat_id].append(('answer', text))
            else:
                if not hasattr(self, '_msg_to_send_answer'):
                    self._msg_to_send_answer = []
                self._msg_to_send_answer.append(text)

    async def _process_pending_message(self):
        """send all waiting messages"""
        if not hasattr(self, '_current_update') or not self._current_update:
            return

        current_chat_id = self._current_update.effective_chat.id

        # send without chat id
        if hasattr(self, '_msg_to_send') and self._msg_to_send:
            # if we use a func in send_message
            if isinstance(self._msg_to_send, list):
                for msg in self._msg_to_send:
                    await self._current_update.message.reply_text(msg)
                self._msg_to_send = None
            # if no func
            else:
                await self._current_update.message.reply_text(self._msg_to_send)
                self._msg_to_send = None

        # send answer for msg
        if hasattr(self, '_msg_to_send_answer') and self._msg_to_send_answer:
            if isinstance(self._msg_to_send_answer, list):
                for msg in self._msg_to_send_answer:
                    await self._current_update.message.reply_text(
                        text=msg,
                        reply_to_message_id=self._current_update.message.message_id
                    )
            else:
                await self._current_update.message.reply_text(
                    text=self._msg_to_send_answer,
                    reply_to_message_id=self._current_update.message.message_id
                )
            self._msg_to_send_answer = None

        # send message for chat_id
        if current_chat_id in self.pending_message:
            for msg in self.pending_message[current_chat_id]:
                if isinstance(msg, tuple) and msg[0] == 'answer':
                    await self._current_update.message.reply_text(
                        text=msg[1],
                        reply_to_message_id=self._current_update.message.message_id
                    )
                else:
                    await self._current_update.message.reply_text(msg)

            self.pending_message[current_chat_id] = []

    """End Send And answer For Message and delete and edit"""

    """btn add"""

    async def _refresh_interface(self, msg: str, clear_first: bool = True):
        """Refresh the current interface with updated buttons"""
        if not hasattr(self, '_current_update') or not self._current_update:
            return

        try:
            # Get the message object
            message = None
            if self._current_update.message:
                message = self._current_update.message
            elif hasattr(self._current_update,
                         'callback_query') and self._current_update.callback_query and self._current_update.callback_query.message:
                message = self._current_update.callback_query.message

            if not message:
                return

            # Create new keyboard markup
            reply_markup = None
            if self.buttons:
                if self.inline:
                    keyboard = [
                        [InlineKeyboardButton(text, callback_data=data)
                         for text, data in self.buttons if text.strip()]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                else:
                    # For regular buttons
                    keyboard = [[KeyboardButton(text)] for text, _ in self.buttons]
                    reply_markup = ReplyKeyboardMarkup(
                        keyboard,
                        resize_keyboard=True,
                        one_time_keyboard=False
                    )

            # For regular messages (not callback queries)
            if not hasattr(self._current_update, 'callback_query'):
                await message.reply_text(
                    text=msg,
                    reply_markup=reply_markup
                )
            else:
                # For callback queries, edit the existing message
                try:
                    keyboard = [
                        [InlineKeyboardButton(text, callback_data=data)
                         for text, data in self.buttons if text.strip()]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await message.edit_text(
                        text=msg,
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    try:
                        keyboard = [
                            [InlineKeyboardButton(text, callback_data=data)
                             for text, data in self.buttons if text.strip()]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await message.reply_text(
                            text=msg,
                            reply_markup=reply_markup
                        )
                    except Exception as e:
                        if self.debug_LBF_and_code:
                            print(f"Error editing message: {e}")

        except Exception as e:
            print(f"Error in _refresh_interface: {e}")

    def add_buttons(self, message: str, buttons: list):
        if not message.strip():
            raise ValueError("Error add_button: please input a message")

        # Saving the initial state
        self._initial_start_message = message
        self._initial_buttons = []
        self._initial_buttons_inline = False

        # Setting the current state
        self.start_message = message
        self.buttons = []
        self.message_callbacks.clear()
        self.inline = False

        # Processing the buttons
        for btn in buttons:
            if isinstance(btn, tuple) and len(btn) == 2:
                btn_text, handler = btn
                self.buttons.append((btn_text, btn_text))
                self.message_callbacks[btn_text.lower()] = (self._wrap_callback(handler), (), {})
                self._initial_buttons.append((btn_text, btn_text))
            else:
                btn_text = btn[0] if isinstance(btn, tuple) else btn
                self.buttons.append((btn_text, btn_text))
                self.message_callbacks[btn_text.lower()] = (self._wrap_callback(lambda: None), (), {})
                self._initial_buttons.append((btn_text, btn_text))

        # Forced interface update
        if hasattr(self, '_current_update') and self._current_update:
            if self._current_update.message:
                asyncio.create_task(self._show_buttons(message))

    async def _show_buttons(self, message: str):
        """Shows buttons in the current chat"""
        try:
            keyboard = [[KeyboardButton(text)] for text, _ in self.buttons]
            reply_markup = ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                one_time_keyboard=False
            )

            await self._current_update.message.reply_text(
                text=message,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Error showing buttons: {e}")

    def add_buttons_inline(self, message: str, buttons: list):
        """
        Add inline buttons with handler functions
        Format: bot.add_buttons_inline("msg", [("btn_text", func), ("btn_text2", func2)])
        """
        if not message.strip():
            raise ValueError("Error add_buttons_inline: please input a message")

        # Save current message and buttons
        self.start_message = message
        self.buttons = []
        self.buttons_handlers.clear()

        # Process buttons with proper closure
        for i, (btn_text, handler) in enumerate(buttons):
            callback_data = f"btn_{i}"
            self.buttons.append((btn_text, callback_data))

            # Create wrapper with proper closure
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              func=handler, cb_data=callback_data):
                try:
                    self._current_update = update
                    self._current_context = context
                    if update.callback_query and update.callback_query.message:
                        self._current_chat_id = update.callback_query.message.chat_id

                    # Execute handler
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()

                    # Process pending messages
                    await self._process_pending_message()
                except Exception as e:
                    if self.debug_LBF_and_code:
                        print(f"Button handler error ({cb_data}): {e}")

            self.buttons_handlers[callback_data] = wrapper

        # Update interface immediately if there's an active chat
        if hasattr(self, '_current_update') and self._current_update:
            asyncio.create_task(self._refresh_interface(message))

    """End add btn"""

    """get info about user"""

    @property
    def get_user_full_name(self):
        if self._current_user or self._tmp_full_name:
            return self._tmp_full_name
        return None

    def get_user_name(self):
        if self._current_user or self._tmp_user_name:
            return self._tmp_user_name

        return None

    def get_user_id(self):
        if self._current_user or self._tmp_user_id:
            return self._tmp_user_id
        return None

    def get_user_username(self):
        if self._current_user or self._tmp_username:
            return self._tmp_username
        return None

    def get_user_chat_id(self):
        if self._current_user or self._tmp_chat_id:
            return self._tmp_chat_id
        return None

    def get_user_info(self):
        if self._current_user:
            res = f"""
    ======================================================================
    User: {self._current_user.full_name}
    ID: {self._current_user.id}
    Chat_id: {self._tmp_chat_id}
    Username: @{self._current_user.username}
    ======================================================================
                """
            return res
        return None


    """start"""
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            """get user data"""
            self._tmp_username = update.effective_user.username
            self._tmp_user_name = update.effective_user.first_name
            self._tmp_full_name = update.effective_user.full_name
            self._tmp_chat_id = update.effective_chat.id
            self._tmp_user_id = update.effective_user.id
            
            # get name user (if you need)
            tmp_check_get_user = False

            if "get_username" in self.start_message:
                self.start_message = self.start_message.replace("get_username", self._tmp_username, 1)
                tmp_check_get_user = True

            if "get_user_name" in self.start_message:
                self.start_message = self.start_message.replace("get_user_name", self._tmp_user_name, 1)
                tmp_check_get_user = True

            if "get_user_fullname" in self.start_message:
                self.start_message = self.start_message.replace("get_user_fullname", self._tmp_full_name, 1)
                tmp_check_get_user = True


            # Restore initial state
            if tmp_check_get_user:
                pass
            elif hasattr(self, '_initial_buttons'):
                self.buttons = self._initial_buttons.copy()
            elif hasattr(self, '_initial_buttons_inline'):
                self.inline = self._initial_buttons_inline
            elif hasattr(self, '_initial_start_message'):
                self.start_message = self._initial_start_message

            # For inline buttons
            if self.inline and self.buttons:
                keyboard = [
                    [InlineKeyboardButton(text, callback_data=data)
                     for text, data in self.buttons]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    text=self.start_message,
                    reply_markup=reply_markup
                )
            # For regular buttons
            elif not self.inline and self.buttons:
                keyboard = [[KeyboardButton(text)] for text, _ in self.buttons]
                reply_markup = ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
                await update.message.reply_text(
                    text=self.start_message,
                    reply_markup=reply_markup
                )
            # No buttons
            else:
                await update.message.reply_text(self.start_message)

        except Exception as e:
            print(f"Error in start handler: {e}")
            await update.message.reply_text("An error occurred. Please try again.")

    async def button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()  # Important to answer callback query first

        self._current_update = update
        self._current_context = context
        self._current_chat_id = query.message.chat_id

        callback_data = query.data

        if callback_data in self.buttons_handlers:
            try:
                handler = self.buttons_handlers[callback_data]
                await handler(update, context)
            except Exception as e:
                print(f"Error in button_click handler: {e}")
                await query.message.reply_text("An error occurred while processing the command")

    """Command if_message"""
    def if_message(self, message: Union[str, List[str]], response: Union[Callable, str, None] = None, *args, **kwargs):
        if response is not None:
            wrapped_response = self._wrap_callback(response) # Wrapping the callback in our function

            if isinstance(message, list): # If message is a list of words
                for msg in message:
                    self.message_callbacks[msg.lower()] = (self._wrap_callback(response), args, kwargs)
            else:
                self.message_callbacks[message.lower()] = (response, args, kwargs)
         # if there is no message verification
        else:
            if isinstance(message, list):
                return self.current_user_text in [m.lower() for m in message]
            else:
                return self.current_user_text == message.lower()




    """default message"""
    def set_default_message(self, message: str, is_def_send_msg: bool = False, reply_msg_user: bool = False):
        self.default_message = message
        self.is_default_send_msg = is_def_send_msg
        self.repl_msg_user = reply_msg_user

    """add command"""
    def add_command(self, command: str, answer: Union[Callable, str, None] = None, *args, **kwargs):
        """
        Adds a simple command that outputs text
        :param command: command name(for example "/help")
        :param answer: text to output when the command is invoked
        """
        if not command.startswith('/'):
            command = '/' + command

        """handler for command"""
        async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            self._current_update = update
            self._current_context = context

            if callable(answer):
                try:
                    # for func that expect update/context
                    if asyncio.iscoroutinefunction(answer):
                        await answer(update, context, *args, **kwargs)
                    else:
                        answer(update, context, *args, **kwargs)
                except TypeError:
                    # for func without parameters
                    if asyncio.iscoroutinefunction(answer):
                        await answer()
                    else:
                        answer()

            elif isinstance(answer, str):
                await update.message.reply_text(answer)

            await self._process_pending_message()

        self.commands[command] = command_handler

    """add hint command"""
    def add_hint_command(self, command: str, info: str):
        """
        Adds a hint for the command
        :param command: the name of the command (for example "/info")
        :param info: description of the hint command
        """
        if not command.startswith('/'):
            command = '/' + command
        self.command_hints[command] = info

    """Text Message Handler"""
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.current_user_text = update.message.text.lower()

        self._current_update = update
        self._current_context = context
        self._current_user = update.effective_user

        """check debug user"""
        if self.debug_user_data:
            user = update.effective_user
            user_info = (
                f"User: {user.full_name}\n",
                f"ID: {user.id}\n",
                f"Chat_id: {update.effective_chat.id}",
                f"Username: @{user.username}" if user.username else "Username: Not specified"
            )
            print("\n" + "=" * 70)
            print(user_info)
            print("=" * 70 + "\n")

        # for send message
        # process the incoming message
        if self.current_user_text in self.message_callbacks:
            response, args, kwargs = self.message_callbacks[self.current_user_text]

            """handle message (send_message and send_message_answer)"""
            if callable(response):
                try:
                    if asyncio.iscoroutinefunction(response):
                        await response(update, context, *args, **kwargs)
                    else:
                        response(*args, **kwargs)
                except TypeError:
                    response()

            elif isinstance(response, str):
                await update.message.reply_text(response)

        elif self.default_message is not None:
            if self.repl_msg_user :
                await update.message.reply_text(
                    text=self.default_message,
                    reply_to_message_id=update.message.message_id
                )
            elif self.is_default_send_msg:
                await update.message.reply_text(self.default_message)
            else:
                print(self.default_message)

        # then process pending messages
        await self._process_pending_message()
    """run"""
    def run(self):
        if not self.token:
            return ValueError("Token is not set")

        print("Bot starting...")
        application = Application.builder().token(self.token).build()

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # add handle command
        for command, handler in self.commands.items():
            application.add_handler(CommandHandler(command[1:], handler))

        # add hint for command
        async def set_commands():
            if self.command_hints:
                commands_list = [BotCommand(command[1:], description)
                                for command, description in self.command_hints.items()]
                await application.bot.set_my_commands(commands_list)

        loop.create_task(set_commands())

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_click))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        print("the bot is running")
        application.run_polling()

"""For use bot. Example: bot.start()"""
bot = TelegramBot()
