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
from typing import Dict, List, Tuple, Optional, Union


class TelegramBot:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TOKEN")
        self.start_message = "Привет! Я бот."
        self.start_markup: Optional[InlineKeyboardMarkup] = None
        self.reply_markup: Optional[ReplyKeyboardMarkup] = None
        self.message_handlers: Dict[str, str] = {}
        self.button_handlers: Dict[str, str] = {}
        self.reply_keyboards: Dict[str, List[Tuple[str, str]]] = {}
        self.commands: Dict[str, str] = {}
        self.command_hints: Dict[str, str] = {}
        self.reply_messages: Dict[str, str] = {}

    def clickStartBot(self, text: str) -> None:
        self.start_message = text
        self.start_markup = None
        self.reply_markup = None

    def clickStartBotUnderBtn(self, text: str, *buttons: Tuple[str, str]) -> None:
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

    def clickStartBotBtn(self, text: str, *buttons: Tuple[str, str]) -> None:
        self.start_message = text
        if buttons and len(buttons) <= 6:
            keyboard = [
                [KeyboardButton(btn_text)]
                for btn_text, _ in buttons[:6]
            ]
            self.reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            for btn_text, response in buttons:
                self.reply_messages[btn_text.lower()] = response
        else:
            self.reply_markup = None

    def if_message(self, received_text, response_text):
        """Добавляет обработчик текстовых сообщений"""
        self.message_handlers[received_text.lower()] = response_text

    def add_button(self, trigger_message: str, button_text: str, response_text: str) -> None:
        if trigger_message not in self.reply_keyboards:
            self.reply_keyboards[trigger_message] = []
        self.reply_keyboards[trigger_message].append((button_text, response_text))
        self.reply_messages[button_text.lower()] = response_text

    def add_command(self, command: str, response: str) -> None:
        self.commands[command] = response

    def add_hint_command(self, command: str, hint: str) -> None:
        self.command_hints[command] = hint

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        query = update.callback_query
        await query.answer()
        callback_data = query.data
        if callback_data in self.button_handlers:
            await query.edit_message_text(text=self.button_handlers[callback_data])
        else:
            await query.edit_message_text(text="Неизвестная команда")

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command = update.message.text[1:].split()[0].lower()  # Приводим команду к нижнему регистру
        if command in self.commands:
            await update.message.reply_text(self.commands[command])
        else:
            await update.message.reply_text("Неизвестная команда")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_text = update.message.text.lower()

        # Проверяем сначала точные совпадения
        if user_text in self.reply_messages:
            await update.message.reply_text(self.reply_messages[user_text])
            return

        # Затем проверяем триггерные сообщения
        for trigger_msg, buttons in self.reply_keyboards.items():
            if trigger_msg.lower() in user_text:
                keyboard = [
                    [KeyboardButton(btn_text)]
                    for btn_text, _ in buttons
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                await update.message.reply_text(
                    "Выберите вариант:",
                    reply_markup=reply_markup
                )
                return

        # Проверяем другие обработчики сообщений
        if user_text in self.message_handlers:
            await update.message.reply_text(self.message_handlers[user_text])
        else:
            await update.message.reply_text("Я не понимаю команду.")

    async def setup_commands(self, application: Application) -> None:
        if self.command_hints:
            commands = [
                BotCommand(command, description)
                for command, description in self.command_hints.items()
            ]
            await application.bot.set_my_commands(commands)

    def run(self) -> None:
        if not self.token:
            raise ValueError("Токен не установлен!")
        application = Application.builder().token(self.token).build()

        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start))

        if self.commands:
            application.add_handler(MessageHandler(filters.COMMAND, self.handle_command))

        if self.button_handlers:
            application.add_handler(CallbackQueryHandler(self.button_click))

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Настраиваем команды бота
        application.add_handler(CommandHandler("setup", self.setup_commands))

        print("Бот запускается...")
        application.run_polling()


# Создаем экземпляр бота для экспорта
if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()

bot = TelegramBot()