# Library_Fast_Bot
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


## after pressing the start button
bot.clickStartBot("your text") #Just writes a message
bot.clickStartBotBtn("text", ("btn_text", "answer")) #creating a button after pressing (up to 6 buttons are possible)
bot.clickStartBotUnderBtn("text", ("btn_text", "answer")) #create a button under the text after clicking (up to 6 buttons are possible)

## at the end, you need to add - bot.run()
created with DeepSeek

# Documentation
