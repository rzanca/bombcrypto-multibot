import telegram
from telegram import *
from telegram.ext import *
from configuration import Configuration

class Telegram:

  def __init__(self, login_method: None, search_for_workable_heroes: None, refresh_heroes_positions_method: None, balance_method: None):
    self.active = Configuration.telegram['active']
    if self.active:
      self.token = Configuration.telegram['token']
      self.chatid = Configuration.telegram['chatid']
      self.login_method = login_method
      self.search_for_workable_heroes = search_for_workable_heroes
      self.refresh_heroes_positions_method = refresh_heroes_positions_method
      self.balance_method = balance_method

      if int(len(self.token)) > 10 and int(len(self.chatid) >=5):
        self.bot = self.criar_bot_telegram()
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.message_handler))

        self.telsendtext('''
        /start Iniciar Bot
        ''')
        self.updater.start_polling()
        print('>>---> Notificações no Telegram habilitadas.\n')
      else:
        print('>>---> Notificações no Telegram desabilitadas.\n')

  def start_command(self, update: Update, context: CallbackContext):
    buttons = [
      [KeyboardButton("Login")], 
      [KeyboardButton("Send Heroes To Work")],
      [KeyboardButton("Refresh Heroes Positions")],
      [KeyboardButton("Balance")]
    ]

    context.bot.send_message(chat_id=update.effective_chat.id, text="Bem vindo!", reply_markup=ReplyKeyboardMarkup(buttons))

  def message_handler(self, update: Update, context: CallbackContext):
    if "Login" in update.message.text:
      self.login_method(True)
    elif "Send Heroes To Work" in update.message.text:
      self.search_for_workable_heroes(True)
    elif "Refresh Heroes Positions" in update.message.text:
      self.search_for_workable_heroes(True)
    elif "Balance" in update.message.text:
      self.balance_method(True)

  def criar_bot_telegram(self):
    return telegram.Bot(token=self.token)

  def telsendtext(self, bot_message, num_try=0):
    if not self.active:
      return
    try:
        return self.bot.send_message(chat_id=self.chatid, text=bot_message)
    except:
      if num_try == 1:
          self.bot = self.criar_bot_telegram()
          return self.telsendtext(bot_message, 1)
      return 0

  def telsendphoto(self, photo_path, num_try=0):
      if not self.active:
        return
      try:
          return self.bot.send_photo(chat_id=self.chatid, photo=open(photo_path, 'rb'))
      except:
        if num_try == 1:
            self.bot = self.criar_bot_telegram()
            return self.telsendphoto(photo_path, 1)
        return 0