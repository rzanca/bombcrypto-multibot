import time
import sys
import os
from cv2 import cv2
from os import listdir
from random import random, randint
from datetime import datetime

from src.logger import logger, loggerMapClicked
from configuration import Configuration
from autoui import AutoUI
from telegram_bot import Telegram
from screen_controls import ScreenControls
from instructions import instruction

class Bot:
  
  def __init__(self):
    self.images = self.load_images()
    self.windows = self.load_windows()

    self.telegram = Telegram(
      self.login, 
      self.search_for_workable_heroes, 
      self.refresh_heroes_positions, 
      self.go_balance, 
      self.send_screenshot, 
      self.refresh_page, 
      self.send_executions_infos,
      self.rest_all
    )
    self.hero_clicks = 0
    self.login_attempts = 0
    self.last_log_is_progress = False
    self.accounts = 0
    self.activeaccount = 0
    # self.accountslist = list(range(0, self.accounts)) 

  #region Configs

  def remove_suffix(self, input_string, suffix):
    if suffix and input_string.endswith(suffix):
      return input_string[:-len(suffix)]
    return input_string

  def load_images(self):
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[self.remove_suffix(file, '.png')] = cv2.imread(path)
    return targets

  def load_windows(self):
    windows = []
    t = Configuration.c['time_intervals']
    for window in ScreenControls.getWindowsWithTitle():
      if window.title.count('bombcrypto-multibot') >= 1:
          continue

      windows.append({
        'window': window,
        'login': 0,
        'heroes': 0,
        'balance': 0,
        'new_map': 0,
        'refresh_heroes': 0,
        'send_screenshot': t['send_screenshot'] * 60,
        'refresh_page': t['refresh_page'] * 60,
        'maps': []
      })

    return windows

  def add_randomness(self, n, randomn_factor_size=None):
    if randomn_factor_size is None:
      randomness_percentage = 0.1
      randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
      random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)

  #endregion

  #region Click de Botões

  def click_on_go_work(self):
    return ScreenControls.positions(self.images['go-work'], threshold=Configuration.threshold['go_to_work_btn'])

  def click_on_green_bar(self):
    return ScreenControls.positions(self.images['green-bar'], threshold=Configuration.threshold['green_bar'])

  def click_on_full_bar(self):
    return ScreenControls.positions(self.images['full-stamina'], threshold=Configuration.threshold['default'])

  def click_on_treasure_hunt(self, timeout=3):
    return ScreenControls.clickbtn(self.images['treasure-hunt-icon'], timeout=timeout)

  def click_on_x(self):
    return ScreenControls.clickbtn(self.images['x'])

  def click_on_go_back(self):
    return ScreenControls.clickbtn(self.images['go-back-arrow'])

  def click_on_heroes(self):
    return ScreenControls.clickbtn(self.images['hero-icon'])

  def click_on_send_all(self):
    return ScreenControls.positions(self.images['send-all'], threshold=Configuration.threshold['go_to_work_btn'])

  def click_on_rest_all(self):
    return ScreenControls.positions(self.images['rest-all'], threshold=Configuration.threshold['go_to_work_btn'])

  def click_on_balance(self):
    ScreenControls.clickbtn(self.images['consultar-saldo'])
    
  #endregion

  #region Painel Herói

  def scroll(self):
    hero_item_list = ScreenControls.positions(self.images['hero-item'], threshold=Configuration.threshold['common'])
    if len(hero_item_list) == 0:
        return
    x, y, w, h = hero_item_list[len(hero_item_list) - 1]
    ScreenControls.movetowithrandomness(x, y, 1)

    if not Configuration.c['use_click_and_drag_instead_of_scroll']:
        AutoUI.pyautogui.scroll(-Configuration.c['scroll_size'])
    else:
        AutoUI.pyautogui.dragRel(0, -Configuration.c['click_and_drag_amount'], 1, button='left')

  def rest_all(self):
    logger('⚒️ Colocando os heróis para dormir (seus vagabundos)', 'green')
    self.go_to_heroes()
    time.sleep(10)
    self.click_on_rest_all()
    time.sleep(10)
    self.go_to_treasure_hunt()
    
  def is_working(self, bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
      isbelow = y < (button_y + button_h)
      isabove = y > (button_y - button_h)
      if isbelow and isabove:
        return False
    return True

  def send_all(self):
    buttons = self.click_on_send_all()
    for (x, y, w, h) in buttons:
      ScreenControls.movetowithrandomness(x + (w / 2), y + (h / 2), 1)
      AutoUI.pyautogui.click()

  def send_green_bar_heroes_to_work(self):
    offset = 140

    green_bars = self.click_on_green_bar()
    logger('🟩 %d Barras verdes detectadas' % len(green_bars))
    buttons = self.click_on_go_work()
    logger('🆗 %d Botoes detectados' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
      if not self.is_working(bar, buttons):
        not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
      logger('🆗 %d Botoes com barra verde detectados' % len(not_working_green_bars))
      logger('👆 Clicando em %d heróis' % len(not_working_green_bars))

    hero_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
      ScreenControls.movetowithrandomness(x + offset + (w / 2), y + (h / 2), 1)
      AutoUI.pyautogui.click()
      self.hero_clicks = self.hero_clicks + 1
      hero_clicks_cnt = hero_clicks_cnt + 1
      if hero_clicks_cnt > 20:
        logger('⚠️ Houve muitos cliques em heróis, tente aumentar o go_to_work_btn threshold')
        return
    return len(not_working_green_bars)

  def send_full_bar_heroes_to_work(self):
    offset = 100
    full_bars = self.click_on_full_bar()
    buttons = self.click_on_go_work()

    not_working_full_bars = []
    for bar in full_bars:
      if not self.is_working(bar, buttons):
        not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
      logger('👆 Clicando em %d heróis' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
      ScreenControls.movetowithrandomness(x + offset + (w / 2), y + (h / 2), 1)
      AutoUI.pyautogui.click()
      self.hero_clicks = self.hero_clicks + 1

    return len(not_working_full_bars)

  def send_heroes_to_work(self):
    if Configuration.c['select_heroes_mode'] == 'full':
      return self.send_full_bar_heroes_to_work()
    elif Configuration.c['select_heroes_mode'] == 'green':
      return self.send_green_bar_heroes_to_work()
    else:
      return self.send_all()

  def go_to_heroes(self):
    if self.click_on_go_back():
      self.login_attempts = 0

    time.sleep(3)
    self.click_on_heroes()
    time.sleep(3)

  def search_for_workable_heroes(self, update_last_execute = False):
    if update_last_execute:
      self.telegram.telsendtext('O bot irá colocar os bonecos para trabalhar!')
      for currentWindow in self.windows:
        currentWindow['heroes'] = 0

      return
    
    self.go_to_heroes()

    if Configuration.c['select_heroes_mode'] == 'full':
      logger('⚒️ Enviando heróis com a energia cheia para o trabalho', 'green')
    elif Configuration.c['select_heroes_mode'] == 'green':
      logger('⚒️ Enviando heróis com a energia verde para o trabalho', 'green')
    else:
      logger('⚒️ Enviando todos heróis para o trabalho', 'green')

    empty_scrolls_attempts = Configuration.c['scroll_attempts']

    if Configuration.c['select_heroes_mode'] == 'all':
      time.sleep(4)
      self.send_all()
      logger('💪 ALL heroes sent to work')
      time.sleep(4)
    else:
      while empty_scrolls_attempts > 0:
        self.send_heroes_to_work()
        empty_scrolls_attempts = empty_scrolls_attempts - 1
        self.scroll()
        time.sleep(2)
      logger('💪 {} Heróis enviados para o trabalho'.format(self.hero_clicks))

    self.go_to_treasure_hunt()

  #endregion

  def go_to_treasure_hunt(self):
    self.click_on_x()
    time.sleep(4)
    self.click_on_treasure_hunt()

  def refresh_heroes_positions(self, update_last_execute = False):
    if update_last_execute:
      self.telegram.telsendtext('O bot irá atualizar a posição dos heróis aguarde!')
      for currentWindow in self.windows:
        currentWindow['refresh_heroes'] = 0
    
      return
        
    logger('🔃 Atualizando posição dos heróis')
    self.click_on_go_back()
    time.sleep(2)
    self.click_on_treasure_hunt()

  #login

  def login(self, update_last_execute = False):
    if update_last_execute:
      self.telegram.telsendtext('O bot irá logar, aguarde!')
      for currentWindow in self.windows:
        currentWindow['login'] = 0
      return

    logger('😿 Checando se o jogo se desconectou')

    if self.login_attempts > 4:
      logger('🔃 Muitas tentativas de login, atualizando')
      self.login_attempts = 0
      AutoUI.pyautogui.hotkey('ctrl', 'f5')
      return

    if ScreenControls.clickbtn(self.images['connect-wallet'], timeout=10):
      logger('🎉 Botão de conexão da carteira encontrado, logando!')
      self.login_attempts = self.login_attempts + 1
    time.sleep(5)

    #Login activated
    l = Configuration.c['login_with_pass']
    if l["activated"] == True:
      if ScreenControls.clickbtn(self.images['type-username'], timeout=10):
        ScreenControls.inputtype(l["accounts"][self.activeaccount]["username"])
        logger('⌨ Preenchendo campo de usuário!')

      if ScreenControls.clickbtn(self.images['type-password'], timeout=10):
        ScreenControls.inputtype(l["accounts"][self.activeaccount]["password"])
        logger('⌨ Preenchendo campo de senha!')
      
      if ScreenControls.clickbtn(self.images['connect-login'], timeout=10):
        logger('👌 Clicando no botão login!')
        self.login_attempts = self.login_attempts + 1
        time.sleep(2)
    else:
      if ScreenControls.clickbtn(self.images['connect-metamask'], timeout=10):
        logger('👌 Botão de conexão pela metamask, clicado!')
        self.login_attempts = self.login_attempts + 1
        time.sleep(10)

    if ScreenControls.clickbtn(self.images['select-wallet-2'], timeout=8):
      self.login_attempts = self.login_attempts + 1
      time.sleep(15)

      self.search_for_workable_heroes()
      if self.click_on_treasure_hunt(timeout=15):
        self.login_attempts = 0
      return
    else:
      pass
    
    if ScreenControls.clickbtn(self.images['ok'], timeout=5):
      pass

  def go_balance(self, update_last_execute = False, curwind = ''):
    if update_last_execute:
      self.telegram.telsendtext('O bot irá consultar seu saldo, aguarde!')
      for currentWindow in self.windows:
        currentWindow['balance'] = 0
      
      return

    logger('Consultando seu saldo')
    time.sleep(2)
    self.click_on_balance()
    i = 10
    coins_pos = ScreenControls.positions(self.images['coin-icon'], threshold=Configuration.threshold['default'])
    while len(coins_pos) == 0:
        if i <= 0:
            break
        i = i - 1
        coins_pos = ScreenControls.positions(self.images['coin-icon'], threshold=Configuration.threshold['default'])
        time.sleep(5)

    if len(coins_pos) == 0:
        logger('Saldo não encontrado.')
        self.click_on_x()
        return

    left, top, width, height = coins_pos[0]
    left = left - 44
    top = top + 130
    width = 200
    height = 50

    myscreen = AutoUI.pyautogui.screenshot(region=(left, top, width, height))
    print(f'r = {left}, {top}, {width}, {height}')
    img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\targets\saldo1.png'
    myscreen.save(img_dir)
    time.sleep(4)
    enviar = ('🚨 Seu saldo Bcoins 🚀🚀🚀 em %s' % curwind)
    self.telegram.telsendtext(enviar)
    self.telegram.telsendphoto(img_dir)
    self.click_on_x()
    time.sleep(4)
  
  def send_screenshot(self, update_last_execute = False):
    if update_last_execute:
      self.telegram.telsendtext('O bot irá tirar screenshot das suas telas, aguarde!')
      for currentWindow in self.windows:
        currentWindow['send_screenshot'] = 0
      
      return

    myscreen = AutoUI.pyautogui.screenshot()
    img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\targets\allscreens.png'
    myscreen.save(img_dir)
    time.sleep(4)
    self.telegram.telsendtext('Aqui vai como está sua tela!')
    self.telegram.telsendphoto(img_dir)
    time.sleep(4)

  def refresh_page(self, update_last_execute = False):
    self.telegram.telsendtext('O bot irá atualizar a página e tentará logar novamente, aguarde!')
    for currentWindow in self.windows:
      currentWindow['refresh_page'] = 0
      currentWindow['login'] = 0
      currentWindow['window'].activate()
      AutoUI.pyautogui.hotkey('ctrl', 'f5')
      time.sleep(15)

  def send_executions_infos(self):
    for currentWindow in self.windows:
      title = currentWindow['window'].title
      print(currentWindow['login'])
      login = '' if currentWindow['login'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(int(currentWindow['login'])))
      heroes = '' if currentWindow['heroes'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(int(currentWindow['heroes'])))
      balance = '' if currentWindow['balance'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(int(currentWindow['balance'])))
      new_map ='' if currentWindow['new_map'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(int(currentWindow['new_map'])))
      refresh_heroes ='' if currentWindow['refresh_heroes'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(int(currentWindow['refresh_heroes'])))
      send_screenshot ='' if currentWindow['send_screenshot'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(int(currentWindow['send_screenshot'])))
      refresh_page ='' if currentWindow['refresh_page'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(int(currentWindow['refresh_page'])))
      texto = f'''
        window: {title}
        login: {login}
        heroes: {heroes}
        balance: {balance}
        new_map: {new_map}
        refresh_heroes: {refresh_heroes}
        send_screenshot: {send_screenshot}
        refresh_page: {refresh_page}
      '''

      self.telegram.telsendtext(texto)

  def start(self):
    print(instruction)
    time.sleep(5)
    t = Configuration.c['time_intervals']

    if len(self.windows) >= 1:
      self.accounts = len(self.windows)

      print('\n\n>>---> %d janelas com o nome Bombcrypto encontradas!' % len(self.windows))
      self.telegram.telsendtext('🔌 Bot inicializado em %d Contas. \n\n 💰 É hora de faturar alguns BCoins!!!' % len(self.windows))

      while True:
        for currentWindow in self.windows:
          time.sleep(2)
          now = time.time()
          currentWindow['window'].activate()
          if not currentWindow['window'].isMaximized:
            currentWindow['window'].maximize()

          print('\n\n>>---> Janela atual: %s' % currentWindow['window'].title)

          if self.activeaccount == self.accounts:
            self.activeaccount = 1
          else:
            self.activeaccount = self.activeaccount + 1

          if now - currentWindow['login'] > self.add_randomness(t['check_for_login'] * 60):
            sys.stdout.flush()
            currentWindow['login'] = now
            self.login()

          if now - currentWindow['heroes'] > self.add_randomness(t['send_heroes_for_work'] * 60):
            currentWindow['heroes'] = now
            self.search_for_workable_heroes()

          if now - currentWindow['new_map'] > t['check_for_new_map_button']:
            currentWindow['new_map'] = now
            currentWindow['maps'].append(now)

            if ScreenControls.clickbtn(self.images['new-map']):
              self.telegram.telsendtext(f'Completamos mais um mapa em %s' % currentWindow['window'].title)
              loggerMapClicked()
              time.sleep(3)
              num_jaulas = len(ScreenControls.positions(self.images['jail'], threshold=0.8))
              if num_jaulas > 0:
                self.telegram.telsendtext(
                    f'Parabéns temos {num_jaulas} nova(s) jaula(s) no novo mapa 🎉🎉🎉 em %s' % currentWindow[
                        'window'].title)

          if now - currentWindow['refresh_heroes'] > self.add_randomness(t['refresh_heroes_positions'] * 60):
            currentWindow['refresh_heroes'] = now
            time.sleep(2)
            self.refresh_heroes_positions()

          if now - currentWindow['balance'] > self.add_randomness(t['get_balance'] * 60):
            currentWindow['balance'] = now
            self.go_balance(False, currentWindow['window'].title)

          if now - currentWindow['send_screenshot'] > self.add_randomness(t['send_screenshot'] * 60):
            currentWindow['send_screenshot'] = now
            self.send_screenshot(False)

          logger(None, progress_indicator=True)

          sys.stdout.flush()

    else:
        print('\n\n>>---> Nenhuma janela com o nome Bombcrypto encontrada!')