# EN
# Library_Fast_Bot
# created with DeepSeek (only DeepSeek write code and documentation, I just came up with an idea.)
# Documentation

## first you need install library telegram 
pip install python-telegram-bot 
## then 
from Library_Fast_Bot import bot
## then 
bot.token = "your token"
## at the end, you need to add 
bot.run()

## example code
from Library_Fast_Bot import bot
bot.token = "yout Token"
bot.clickStart("your text")
bot.run()


Overview

The TelegramBot class provides a comprehensive framework for building Telegram bots with support for:

    Command handling

    Inline keyboards

    Reply keyboards

    User sessions

    Button navigation history

    Message handlers

Initialization
python

bot = TelegramBot(token=None)

    token: Optional Telegram bot token (can also be set via TELEGRAM_BOT_TOKEN environment variable)

Basic Configuration
Start Message
python

# Simple start message
bot.clickStart("Hello! I'm a bot.")

# Start with inline buttons
bot.clickStartUnderBtn("Welcome!", ("Button 1", "callback1"), ("Button 2", "callback2"))

# Start with reply keyboard
bot.clickStartBtn("Main Menu", "Option 1", "Option 2")

Command Handling
Add Commands
python

# Add command with response
bot.add_command("help", "Here's some help information")

# Add command with callback
bot.add_command("info", lambda update, ctx: "Info response")

# Add command description (for /help)
bot.add_hint_command("help", "Get help information")

Remove Commands
python

# Remove specific command
bot.clearCommand("help")

# Remove all commands
bot.clearCommand()

Message Handling
Text Message Responses
python

# Respond to exact message match
bot.if_message("hello", "Hi there!")

# Respond with callback
bot.if_message("time", lambda update, ctx: f"Current time: {datetime.now()}")

Global Fallback Response
python

# Handle any unmatched message
bot.global_response = "I didn't understand that"

Button Management
Inline Buttons
python

# Add buttons under specific message
bot.add_buttonUnderMessage("Select option:", 
                         ("Option 1", "opt1"), 
                         ("Option 2", "opt2"))

# Or using add_button
bot.add_button("Button Text", "response", 
              after_message="trigger message", 
              inline=True)

Reply Keyboard Buttons
python

# Add reply keyboard buttons
bot.add_button("Button Text", "response", 
              after_message="trigger message")

Button Handlers
python

# Handle button clicks
bot.button_handlers["opt1"] = "You chose Option 1"
bot.button_handlers["opt2"] = lambda update, ctx: "Callback response"

Remove Buttons
python

# Remove all buttons
bot.clearBtn()

# Remove buttons under specific message
del_btn = bot.del_btn("message text")
await del_btn(update, context)

# Remove reply keyboard
del_keyboard = bot.del_reply_keyboard()
await del_keyboard(update, context)

User Sessions
python

# Store user data
bot.set_user_data(user_id, "key", "value")

# Retrieve user data
value = bot.get_user_data(user_id, "key", default=None)

Button Groups
python

# Create button group
bot.create_button_group("options")

# Add button to group
callback = bot.add_to_button_group("options", "Choice 1", "response1")

Advanced Features
Navigation History

The bot automatically maintains button navigation history for each user, allowing "back" functionality.
Error Handling

The bot includes built-in error handling that ignores empty text errors.
Debug Mode
python

bot.debug_user_data = True  # Prints user interaction info

Running the Bot
python

# Start the bot
bot.run()

Example Usage
python

# Initialize bot
bot = TelegramBot()

# Configure start message with buttons
bot.clickStartUnderBtn("Welcome to my bot!",
                      ("Help", "help_btn"),
                      ("Info", "info_btn"))

# Add button handlers
bot.button_handlers["help_btn"] = "Help information here"
bot.button_handlers["info_btn"] = lambda update, ctx: f"Bot info at {datetime.now()}"

# Add command
bot.add_command("start", "Restarting bot...")
bot.add_hint_command("start", "Restart the bot")

# Add message handler
bot.if_message("hello", "Hi there!")

# Run the bot
bot.run()

Notes

    The bot automatically handles:

        Command registration with Telegram

        Button click events

        Message parsing

        User session management

    All text comparisons are case-insensitive.

    The framework includes protection against empty message errors.

## at the end, you need to add - bot.run()
created with DeepSeek

# RU
Library_Fast_Bot
создан с помощью DeepSeek (только в DeepSeek пишут код и документацию, мне просто пришла в голову идея.)
Документация
сначала вам нужно установить библиотеку telegram
pip, установить python-telegram-bot

затем
из Library_Fast_Bot импортируйте бота

затем
bot.token = "ваш токен"

в конце вам нужно добавить
bot.run()

пример кода
из Library_Fast_Bot импортируйте бота-бота.токен = "ваш токен" bot.clickStartBot("ваш текст") bot.run()

Обзор

Класс TelegramBot предоставляет комплексную платформу для создания ботов Telegram с поддержкой:

Обработки команд

Встроенных клавиатур

Клавиатуры для ответа

Пользовательские сессии

История навигации по кнопкам

Обработчики сообщений
python для инициализации

bot = TelegramBot(токен=Нет)

токен: Дополнительный токен Telegram-бота (также может быть установлен с помощью переменной окружения TELEGRAM_BOT_TOKEN)
Базовая конфигурация Запускает сообщение на python

Просто запустите сообщение
бота.Нажмите "Начать" ("Привет! Я бот").

Начните с встроенных кнопок
bot.clickStartUnderBtn("Добро пожаловать!", ("Кнопка 1", "обратный вызов1"), ("Кнопка 2", "обратный вызов2"))

Начните с ответа клавиатурного
бота.Нажмите STARTBTN("Главное меню", "Опция 1", "Опция 2")

Обработка команд Добавление команд python

Добавить команду с
ботом-ответчиком.add_command("справка", "Вот некоторая справочная информация")

Добавить команду с
ботом-ответчиком.add_command("информация", лямбда-обновление, ctx: "Информационный ответ")

Добавить описание команды (для /help)
bot.add_hint_command("справка", "Получение справочной информации")

Удалить команды python

Удалить конкретную команду
bot.clearCommand("справка")

Удалите все команды
bot.clearCommand()

Обработка текстовых сообщений на python

Ответьте на точное совпадение сообщений
bot.if_message("привет", "Всем привет!")

Ответьте обратным вызовом
bot.if_message("время", лямбда-обновление, ctx: f"Текущее время: {datetime.now()}")

Глобальный резервный ответ python

Обработает любое несогласованное сообщение
бота.global_response = "Я этого не понял"

Управление встроенными кнопками python

Добавьте кнопки под конкретным сообщением
бота.add_buttonUnderMessage("Выберите опцию:", ("Опция 1", "opt1"), ("Опция 2", "opt2"))

Или с помощью add_button
bot.add_button("Текст кнопки", "ответ", after_message="инициирующее сообщение", inline=True)

Кнопки клавиатуры для ответа на python

Добавить кнопки клавиатуры для ответа
bot.add_button("Текст кнопки", "ответ", after_message="триггерное сообщение")

Обработчики кнопок на python

Обрабатывать нажатия кнопок
bot.button_handlers["opt1"] = "Вы выбрали вариант 1" bot.button_handlers["opt2"] = лямбда-обновление, ctx: "Ответ на обратный вызов"

Удалить кнопки python

Удалить все кнопки
bot.clearBtn()

Удалить кнопки под конкретным сообщением
del_btn = bot.del_btn("текст сообщения") дождаться del_btn(обновление, контекст)

Удалить клавиатуру
ответа del_keyboard = bot.del_reply_keyboard(), дождаться del_keyboard(обновление, контекст)

Пользовательские сессии python

Хранить пользовательские данные
bot.set_user_data(идентификатор пользователя, "ключ", "значение")

Получить
значение пользовательских данных = bot.get_user_data(идентификатор пользователя, "ключ", по умолчанию=Нет)

Группы кнопок python

Создать группу кнопок
bot.create_button_group("параметры")

Добавить кнопку в группу
обратного вызова = bot.add_to_button_group("параметры", "Выбор 1", "ответ 1")

Расширенные возможности История навигации

Бот автоматически ведет историю навигации по кнопкам для каждого пользователя, что позволяет выполнять функцию "возврата". Обработка ошибок

Бот включает встроенную обработку ошибок, которая игнорирует ошибки с пустым текстом. Режим отладки python

bot.debug_user_data = True # Выводит информацию о взаимодействии с пользователем

Запускаем бота на python

Запускаем бота
bot.run()

Пример использования на python

Инициализируем бота
bot = TelegramBot()

Настройте запуск сообщения с помощью кнопок
bot.clickStartUnderBtn("Добро пожаловать в мой бот!", ("Справка", "help_btn"), ("Информация", "info_btn"))

Добавить обработчики кнопок
bot.button_handlers["help_btn"] = "Справочная информация здесь" bot.button_handlers["info_btn"] = лямбда-обновление, ctx: f"Информация о боте в {datetime.now()}"

Добавить команду
bot.add_command("запуск", "Перезапуск бота...") bot.add_hint_command("запуск", "Перезапуск бота")

Добавьте обработчик сообщений
bot.if_message("привет", "Всем привет!")

Запустите бота
bot.run()

Записи

Бот автоматически обрабатывает:

    Регистрацию команды в Telegram

    События, связанные с нажатием кнопки

    Анализ сообщений

    Управление сессиями пользователей

Все текстовые сравнения выполняются без учета регистра.

Фреймворк включает защиту от ошибок в пустых сообщениях.
в конце вам нужно добавить - bot.run()
создано с помощью DeepSeek
