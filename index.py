# -*- coding: utf-8 -*-    
from src.logger import logger, loggerMapClicked
from cv2 import cv2
from os import listdir
from random import randint
from random import random
from pyclick import HumanClicker
from datetime import datetime
from numpy import asarray

import numpy as np
import mss
import pyautogui
import time
import sys
import yaml
import telegram
import os
import pygetwindow

stream = open('config.yaml', 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
ch = c['home']
cn = c['telegram_log']
pyautogui.PAUSE = c['time_intervals']['interval_between_moviments']
pyautogui.FAILSAFE = False
hc = HumanClicker()
pyautogui.MINIMUM_DURATION = 0.1
pyautogui.MINIMUM_SLEEP = 0.1
pyautogui.PAUSE = 2
TELEGRAM_BOT_TOKEN = cn['token']
TELEGRAM_CHAT_ID  = cn['chatid']
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
saldo_atual = 0.0

def telegram_bot_sendtext(bot_message, num_try=0):
    global bot
    try:
        return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=bot_message)
    except:
        if num_try == 1:
            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            return telegram_bot_sendtext(bot_message, 1)
        return 0

def telegram_bot_sendphoto(photo_path, num_try=0):
    global bot
    try:
        return bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=open(photo_path, 'rb'))
    except:
        if num_try == 1:
            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            return telegram_bot_sendphoto(photo_path, 1)
        return 0
       
cat = '''
>>---> BOT - MultiContas para BombCrypto - v 0.3.3 

>>---> https://github.com/rzanca/bombcrypto-multibot/

>>---> Curtiu? Faça sua doação... Wallet BEP20
>>---> 0xc11ed49D4c8cAe4EBdE49091c90543b17079d894

>>---> Pressione ctrl + c ou feche o prompt para parar o BOT.

>>---> As configurações variáveis estão em config.yaml'''

def addRandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    hc.move((int(x), int(y)), t)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images():
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

images = load_images()

def loadHeroesToSendHome():
    file_names = listdir('./targets/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d Herois que devem ser mandados para casa carregados.' % len(heroes))
    return heroes

def show(rectangles, img = None):
    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))
    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)

def clickBtn(img, name=None, timeout=3, threshold=ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
    start = time.time()
    clicked = False
    while not clicked:
        matches = positions(img, threshold=threshold)
        if len(matches) == 0:
            hast_timed_out = time.time() - start > timeout
            if hast_timed_out:
                if not name is None:
                    pass
                return False
            continue

        x, y, w, h = matches[0]
        pos_click_x = x + w / 2
        pos_click_y = y + h / 2
        moveToWithRandomness(pos_click_x, pos_click_y, 1)
        pyautogui.click()
        return True

def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def scroll():
    hero_item_list = positions(images['hero-item'], threshold = ct['commom'])
    if (len(hero_item_list) == 0):
        return
    x,y,w,h = hero_item_list[len(hero_item_list)-1]
    moveToWithRandomness(x,y,1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')
   
def SendAll():
    buttons = positions(images['send-all'], threshold=ct['go_to_work_btn'])
    for (x, y, w, h) in buttons:
        moveToWithRandomness(x+(w/2),y+(h/2),1)
        pyautogui.click()
    return len(buttons)

def isHome(hero, buttons):
    y = hero[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def isWorking(bar, buttons):
    y = bar[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def clickGreenBarButtons():
    offset = 140

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d Barras verdes detectadas' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d Botoes detectados' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d Botoes com barra verde detectados' % len(not_working_green_bars))
        logger('👆 Clicando em %d herois' % len(not_working_green_bars))

    hero_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        hero_clicks_cnt = hero_clicks_cnt + 1
        if hero_clicks_cnt > 20:
            logger('⚠️ Houve muitos cliques em herois, tente aumentar o go_to_work_btn threshold')
            return        
    return len(not_working_green_bars)

def clickFullBarButtons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicando em %d herois' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)

def goToHeroes():
    if clickBtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    time.sleep(1)
    clickBtn(images['hero-icon'])
    time.sleep(randint(1,3))

def goToGame():
    clickBtn(images['x'])

    clickBtn(images['treasure-hunt-icon'])

def refreshHeroesPositions():

    logger('🔃 Atualizando posicao dos herois')
    clickBtn(images['go-back-arrow'])
    clickBtn(images['treasure-hunt-icon'])

def login():
    global login_attempts
    logger('😿 Checando se o jogo se desconectou')

    if login_attempts > 3:
        logger('🔃 Muitas tentativas de login, atualizando')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

    if clickBtn(images['connect-wallet'], timeout = 10):
        logger('🎉 Botao de conexao da carteira encontrado, logando!')
        login_attempts = login_attempts + 1
       
    if clickBtn(images['select-wallet-2'], timeout=8):
        login_attempts = login_attempts + 1
        if clickBtn(images['treasure-hunt-icon'], timeout = 15):
            login_attempts = 0
        return
        
    if not clickBtn(images['select-wallet-1-no-hover'], ):
        if clickBtn(images['select-wallet-1-hover'], threshold = ct['select_wallet_buttons'] ):
            pass
    else:
        pass

    if clickBtn(images['select-wallet-2'], timeout = 20):
        login_attempts = login_attempts + 1
        if clickBtn(images['treasure-hunt-icon'], timeout=25):
            login_attempts = 0

    if clickBtn(images['ok'], timeout=5):
        pass

def sendHeroesHome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len (hero_positions) == 0:
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('Nenhum heroi que deveria ser enviado para casa encontrado.')
        return
    print(' %d Herois que devem ser enviados para casa encontrados.' % n)
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not isHome(position,go_home_buttons):
            print(isWorking(position, go_work_buttons))
            if(not isWorking(position, go_work_buttons)):
                print ('Heroi não está trabalhando, enviando para casa.')
                moveToWithRandomness(go_home_buttons[0][0]+go_home_buttons[0][2]/2,position[1]+position[3]/2,1)
                pyautogui.click()
            else:
                print ('Heroi está trabalhando, não será enviado para casa.')
        else:
            print('Heroi já está na casa, ou a casa está cheia.')

def SendHeroesToWork():
    if c['select_heroes_mode'] == 'full':
        return clickFullBarButtons()
    elif c['select_heroes_mode'] == 'green':
        return clickGreenBarButtons()
    else:
        return SendAll()

def refreshHeroes():
    logger('🏢 Procurando herois para trabalhar')
    
    goToHeroes()

    if c['select_heroes_mode'] == 'full':
        logger('⚒️ Enviando herois com a energia cheia para o trabalho', 'green')
    elif c['select_heroes_mode'] == 'green':
        logger('⚒️ Enviando herois com a energia verde para o trabalho', 'green')
    else:
        logger('⚒️ Enviando todos herois para o trabalho', 'green')

    empty_scrolls_attempts = c['scroll_attemps']
    send_all_work = False
    if not ch['enable'] and c['select_heroes_mode'] == 'all':
        time.sleep(1)
        send_all_work = SendAll()
        if send_all_work:
            logger('💪 ALL heroes sent to work')
        time.sleep(2)

    if not send_all_work:
        buttonsClicked = 0
        while(empty_scrolls_attempts >0):
            SendHeroesToWork()
            sendHeroesHome()
            empty_scrolls_attempts = empty_scrolls_attempts - 1
            scroll()
            time.sleep(2)
        logger('💪 {} Herois enviado para o trabalho'.format(hero_clicks))
    goToGame()
   
def goSaldo():
    logger('Consultando seu saldo')
    time.sleep(2)
    global saldo_atual
    clickBtn(images['consultar-saldo'])
    i = 10
    coins_pos = positions(images['coin-icon'], threshold=ct['default'])
    while(len(coins_pos) == 0):
        if i <= 0:
            break
        i = i - 1
        coins_pos = positions(images['coin-icon'], threshold=ct['default'])
        time.sleep(5)
    
    if(len(coins_pos) == 0):
        logger('Saldo não encontrado.')
        clickBtn(images['x'])
        return

    k,l,m,n = coins_pos[0]
    k = k - 44
    l = l + 130
    m = 200
    n = 50

    myScreen = pyautogui.screenshot(region=(k, l, m, n))
    img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\targets\saldo1.png'
    myScreen.save(img_dir)
    time.sleep(2)
    enviar = ('🚨 Seu saldo Bcoins 🚀🚀🚀 em %s' % curwind)
    test = telegram_bot_sendtext(enviar)
    telegram_bot_sendphoto(img_dir)

    clickBtn(images['x'])
  
def main():
    global hero_clicks
    global login_attempts
    global last_log_is_progress
    hero_clicks = 0
    login_attempts = 0
    last_log_is_progress = False

    global images
    images = load_images()

    if ch['enable']:
        global home_heroes
        home_heroes = loadHeroesToSendHome()
    else:
        print('>>---> Modo Casa não habilitado')
    print('\n')

    print(cat)
    time.sleep(5)
    t = c['time_intervals']
    global windows
    windows = []

    for window in pygetwindow.getWindowsWithTitle('Bombcrypto'):
        if (window.title.count('bombcrypto-multibot') >= 1):
            continue

        windows.append({
            'window': window,
            'login': 0,
            'heroes': 0,
            'ssaldo': 0,
            'new_map': 0,
            'refresh_heroes': 0
        })

    if len(windows) >= 1:
        print('>>---> %d janelas com o nome Bombcrypto encontradas!' % len(windows))
        test = telegram_bot_sendtext('🔌 Bot inicializado em %d Contas. \n\n 💰 É hora de faturar alguns BCoins!!!' % len(windows))

        while True:
            for currentWindow in windows:
                currentWindow['window'].activate()
                if currentWindow['window'].isMaximized == False:
                    currentWindow['window'].maximize()
                
                print('>>---> Janela atual: %s' % currentWindow['window'].title)

                time.sleep(2)
                now = time.time()

                if now - currentWindow['heroes'] > addRandomness(t['send_heroes_for_work'] * 60):
                    currentWindow['heroes'] = now
                    refreshHeroes()

                if now - currentWindow['login'] > addRandomness(t['check_for_login'] * 60):
                    sys.stdout.flush()
                    currentWindow['login'] = now
                    login()

                if now - currentWindow['new_map'] > t['check_for_new_map_button']:
                    currentWindow['new_map'] = now

                if clickBtn(images['new-map']):
                    telegram_bot_sendtext(f'Completamos mais um mapa em %s' % currentWindow['window'].title)
                    loggerMapClicked()
                    time.sleep(3)
                    num_jaulas = len(positions(images['jail'], threshold=0.8))
                    if num_jaulas > 0:
                        telegram_bot_sendtext(
                            f'Parabéns temos {num_jaulas} nova(s) jaula(s) no novo mapa 🎉🎉🎉 em %s' % currentWindow['window'].title)


                if now - currentWindow['refresh_heroes'] > addRandomness( t['refresh_heroes_positions'] * 60):
                    currentWindow['refresh_heroes'] = now
                    refreshHeroesPositions()
                    
                if now - currentWindow['ssaldo'] > addRandomness( t['get_saldo'] * 60):
                    currentWindow['ssaldo'] = now
                    global curwind
                    curwind = currentWindow['window'].title                
                    goSaldo()    
            
                logger(None, progress_indicator=True)

                sys.stdout.flush()

                time.sleep(1)
        
    else:
        print('>>---> Nenhuma janela com o nome Bombcrypto encontrada!')
        
if __name__ == '__main__':
    
    main()
    