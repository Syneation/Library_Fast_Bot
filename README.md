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
bot.clickStartBot("your text")
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

