# Library_Fast_Bot
# EN 
# This bot is designed to easily create a telegram bot. 
# why do I need a library?
## if you know any library for a telegram bot, but don't want to write a lot of code for a simple bot, or if you don't know any library for a telegram bot or programming language, but want to create a simple bot, you can use this library (but you'll have to do a little bit study the documentation)

# Documentation

# what do you need to get started

## install pycharm or any python ide
## create a new project
## install the telegram bot library 
```
pip install python-telegram-bot
```
## move the library to the project folder
in the file with your code that you need to add. 
```
from Library_Fast_Bot import bot
bot.token = "YOUR TOKEN"
#here is your code
bot.run()
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
this is the basic structure for running a bot, where it says #here is your code, which you can write using the functions of my library and just python code.
## and now you can use the library

# after pressing the "Start" button.
```
bot.start_bot("message") # simply outputs a message to the chat after writing the command (/start) or when the start
bot button is pressed.start_bot_btn("message", [("button 1", func), ("button 2", functionwo)]) # after the /start command, it outputs a message with the usual buttons (the functions specify what to do after pressing the button)
bot.start_bot_btn_inline("message", [("button 3", funcThree), ("button 4", funcFour)]) # after the /start command, it displays a message with inline buttons (the functions specify what to do after pressing the button)
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
- ( start_bot() ) -> after pressing the "Start" button, a message is displayed
- ( start_bot_btn() ) -> after clicking, a message is displayed, as well as buttons
- ( start_bot_btn_inline() ) -> after clicking, a message is displayed, as well as inline buttons (if you specify bot.add_buttons_inline() in the function -> then you will change the message to a new one )

# adding buttons (add_buttons() / add_buttons_inline() )
```
bot.add_buttons("message 1", [("button 1", func), ("button 2", functionwo)]) # when writing this function, 2 regular buttons are created (up to 16 can be created)
bot.add_buttons_inline("message 2", [("button3", funcThree), ("button4", funcFour)]) # when writing this function, 2 inline buttons are created 
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
- add buttons better in functions
- bot.add_buttons() -> when writing this function, 2 regular buttons are created (up to 16 can be created) -> when clicked, the functions will be called
- bot.add_buttons_inline() -> when writing this function, 2 inline buttons are created -> when clicked, the functions will be called (if the function has add_buttons_inline(), then the text will change)

# if_message
```
#1 Lambda
bot.if_message("message", lambda: print("lambda message response"))

#2 Test the response
bot.if_message ("message", "reply to message")

#3 Registering
the def test() function:
print("reply to message")
...

bot.if_message("message", test)
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
these are all if_message commands that you can use (write functions without -> () )

# use_def_msg, set_default_message
```
# sending a telegram chat message (simple reply, no reply to the message)
bot.set_default_message("your text", True, False) # last False optional

# sending a telegram chat message (with a reply to the message)
bot.set_default_message("your text", True, True)

# sending a message to the console
bot.set_default_message("your text", False) # the last False is optional

```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
commands to output a message with an unknown command

# debug_user_data
```
bot.debug_LBF_and_code = True # if you want the errors that try except catches to be output to the console
bot.debug_user_data = True # if you want to get information about the user in the console every time

# you can also get the user's data in string format using the
following print(bot.get_user_name) commands # getting the user's name

print(bot.get_user_id) # get the user id

print(bot.get_user_username()) # get the user's username

print(bot.get_user_full_name()) # get the full username

print(bot.get_user_info()) # output to the console User, ID, Chat_id, Username -> only then, you will call the function
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
- a command to output data about users (ID, full name and username)
- when you use bot.debug_user_data = True, your console will display User, ID, Chat_id and Username

# send_message / answer_message
```
def testOne():
    print("GOOD")
    bot.send_message("TEST1")

async def testTwo(update: Update, context: : ContextTypes.DEFAULT_TYPE):
    bot.send_message("TEST2")

def optTwo():
    bot.answer_message("GOOD2")

def optTest():
  bot.send_message("msg", 123)

bot.start_bot_btn("Hello :)", ["opt", "opt2"])

bot.if_message("opt", testOne)
bot.if_message("t2", TestTwo)
bot.if_message("opt2", optTwo)
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- send_message -> function for sending a message to a chat 
- answer_message -> function to send a message to the chat with a reply to the user's messages  
- (you can use the usual functions to use send_message() and answer_message() and also with the update, context parameters)
- bot.send_message("msg", 123) sending a message only to this chat id (123 <- chat id)

# adding commands and hints for them (add_command() / add_hint_command())
```
add_command("command1", "command 1 does something") # now, when writing /command1, a message will be displayed that is in 2nd quotes (you can also write a function ONLY WITHOUT -> () )
add_command("command2", func)

add_hint_command("command1", "hint for command 1") # now, when you click on the menu button, a prompt for command1 will appear, in the 2nd quotation marks it will show what the command is doing
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
functions for creating commands


# The bot is designed to quickly write small telegram bots.

# RU
# Этот бот предназначен для простого создания telegram-бота. 
# зачем мне нужна библиотека?
## если вы знаете какую-либо библиотеку для telegram-бота, но не хотите писать много кода для простого бота, или если вы не знаете никакой библиотеки для telegram-бота или язык программирования, но хотите создать простого бота, вы можете использовать эту библиотеку (но придется немного изучить документацию)

# Документация

# что вам нужно для начала работы

## установите pycharm или любую ide python
## создайте новый проект
## установите библиотеку telegram-бота 
```
pip install python-telegram-bot
```
## переместите библиотеку в папку проекта
в файле с вашим кодом, который вам нужно добавить. 
```
  from Library_Fast_Bot import bot
  bot.token = "ВАШ ТОКЕН"
  #здесь ваш код
  bot.run()
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
это базовая структура для запуска бота, где написано #здесь ваш код, который вы можете написать, используя функции моей библиотеки и просто код на python.
## и теперь вы можете использовать библиотеку

# после нажатия кнопки "Старт".
```
bot.start_bot("сообщение") # просто выводит в чат сообщение, после написание команды (/start) или когда нажата кнопка start
bot.start_bot_btn("сообщение", [("кнопка 1", func), ("кнопка 2", funcTwo)]) # после команды /start выводит сообщение с обычными кнопками (в функциях указывается, что делать после нажатие кнопки)
bot.start_bot_btn_inline("сообщение", [("кнопка 3", funcThree), ("кнопка 4", funcFour)]) # после команды /start выводит сообщение с inline кнопками (в функциях указывается, что делать после нажатие кнопки) 
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
- ( start_bot() ) -> после нажатия кнопки "Старт" выводиться сообщение
- ( start_bot_btn() ) -> после нажатие выводиться сообщение, а также и кнопки
- ( start_bot_btn_inline() ) -> после нажатие выводиться сообщение, а также и inline кнопки (если в функции вы укажите bot.add_buttons_inline() -> тогда у вас поменяется сообщение на новое )

# добавление кнопок (add_buttons() / add_buttons_inline() )
```
bot.add_buttons("сообщение 1", [("кнопка1", func), ("кнопка2", funcTwo)]) # при написание этой функции создются 2 обычный кнопки (можно создать до 16)
bot.add_buttons_inline("сообщение 2", [("кнопка3", funcThree), ("кнопка4", funcFour)]) # при написание этой функции создются 2 inline кнопки 
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
- кнопки добавляить лучше в функциях
- bot.add_buttons() -> при написание этой функции создются 2 обычный кнопки (можно создать до 16) -> при нажатие на которых, будут вызыватся функции
- bot.add_buttons_inline() -> при написание этой функции создются 2 inline кнопки -> при нажатие на которых, будут вызыватся функции (если в функции будет add_buttons_inline() тогда текст поменяется)

# if_message
```
#1 Лямбда
bot.if_message("сообщение", lambda: print("ответ на сообщение в виде лямбды"))

#2 Протестируйте ответ
bot.if_message ("сообщение", "ответ на сообщение")

#3 Регистрация функции
def test():
    print("ответ на сообщение")
    ...

bot.if_message("сообщение", test)
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
это все команды if_message которые вы можете использовать ( функции писать без -> () )

# use_def_msg, set_default_message
```
# отправка сообщение в чат телеграмм (простой ответ, без ответа на сообщение)
bot.set_default_message("ваш текст", True, False) # последний False не обязателен

# отправка сообщение в чат телеграмм (с ответом на сообщение)
bot.set_default_message("ваш текст", True, True)

# отправка сообщение в консоль
bot.set_default_message("ваш текст", False) # последний False не обязателен

```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
команды для вывода сообщение при неизвестной команды

# debug_user_data
```
bot.debug_LBF_and_code = True # если хотите, чтобы ошибки которые ловит try except выводились в консоль
bot.debug_user_data = True # если хотите получать каждый раз информацию о пользователе в консоле

# также вы можете получить данные пользователя в формате string с помощью таких команд
print(bot.get_user_name) # получение имя пользователя

print(bot.get_user_id) # получить id пользователя

print(bot.get_user_username()) # получить username пользователя

print(bot.get_user_full_name()) # получить полное имя пользователя

print(bot.get_user_info()) # вывести в консоль User, ID, Chat_id, Username -> только тогда, вы вызовите функцию
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
- команда для вывода данных о пользователи (ID, full name and username)
- когда вы используете bot.debug_user_data = True, в вашей консоле выведится User, ID, Chat_id and Username

# send_message / answer_message
```
def testOne():
    print("GOOD")
    bot.send_message("TEST1")

async def testTwo(update: Update, context: : ContextTypes.DEFAULT_TYPE):
    bot.send_message("TEST2")

def optTwo():
    bot.answer_message("GOOD2")

def optTest():
  bot.send_message("msg", 123)

bot.start_bot_btn("Hello :)", ["opt", "opt2"])

bot.if_message("opt", testOne)
bot.if_message("t2", TestTwo)
bot.if_message("opt2", optTwo)
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
- send_message -> функция для отправки сообщение в чат 
- answer_message -> функция для отправки сообщение в чат с ответом на сообщения пользователя  
- (вы можете использовать обычные функции для использование send_message() и answer_message() и также с параметрами update, context)
- bot.send_message("msg", 123) отправка сообщения только на этот chat id (123 <- chat id)

# добавление команд и подсказок для них (add_command() / add_hint_command())
```

add_command("command1", "команда 1 делает что-то") # теперь при написание /command1 будет выводится сообщение которые во 2-ых кавычках (можно также написать функцию ТОЛЬКО БЕЗ -> () )
add_command("command2", func)

add_hint_command("command1", "подсказка для команды 1") # теперь при нажатие на кнопку меню появиться подсказка для command1, во 2-ых кавычках будет показываться, что делает команда
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
функции для создания команд


# бот создан для быстрого написания небольших telegram ботов. 
