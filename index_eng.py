# -*- coding: utf-8 -*-    
from src.logger_eng import logger, loggerMapClicked
from cv2 import cv2
from os import listdir
from random import randint
from random import random
from pyclick import HumanClicker

import numpy as np
import mss
import pyautogui
import time
import sys
import yaml
import telegram
import os
import pygetwindow

with open('./config.yaml', 'r', encoding='utf-8') as open_yml:
    c = yaml.safe_load(open_yml)
with open('./telegram.yaml', 'r', encoding='utf-8') as teleg:
    tn = yaml.safe_load(teleg)
ct = c['threshold']
ch = c['home']
pyautogui.PAUSE = c['time_intervals']['interval_between_movements']
pyautogui.FAILSAFE = False
hc = HumanClicker()
pyautogui.MINIMUM_DURATION = 0.1
pyautogui.MINIMUM_SLEEP = 0.1
pyautogui.PAUSE = 2
telegram_notify = tn['active']
saldo_atual = 0.0

if telegram_notify is True:
    if int(len(tn['token'])) > 10 and int(len(tn['chatid']) >=5 ):
        bot = telegram.Bot(token=tn['token'])
        tchat = tn['chatid']
        print('>>---> Telegram notifications enabled.\n')
    else:
        print('>>---> Telegram configuration error, notifications disabled.\n')
        telegram_notify = False
else:
    print('>>---> Telegram notifications disabled.\n')



def telsendtext(bot_message, num_try=0):
    global bot
    try:
        return bot.send_message(chat_id=tchat, text=bot_message)
    except:
        if num_try == 1:
            bot = telegram.Bot(token=tn['token'])
            return telsendtext(bot_message, 1)
        return 0


def telsendphoto(photo_path, num_try=0):
    global bot
    try:
        return bot.send_photo(chat_id=tchat, photo=open(photo_path, 'rb'))
    except:
        if num_try == 1:
            bot = telegram.Bot(token=tn['token'])
            return telsendphoto(photo_path, 1)
        return 0


cat = '''
>>---> BOT - MultiAccounts for BombCrypto - v 0.4.2 

>>---> https://github.com/rzanca/bombcrypto-multibot/

>>---> Did you like it? make your donation... Wallet BEP20
>>---> 0xc11ed49D4c8cAe4EBdE49091c90543b17079d894

>>---> Press ctrl + c or close the prompt to stop the BOT.

>>---> Variable settings are in config.yaml'''


def addrandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)


def movetowithrandomness(x, y, t):
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


def loadheroestosendhome():
    file_names = listdir('./targets/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d Heroes who must be sent home loaded.' % len(heroes))
    return heroes


def show(rectangles, img=None):
    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))
    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


def clickbtn(img, name=None, timeout=3, threshold=ct['default']):
    logger(None, progress_indicator=True)
    if name is not None:
        pass
    start = time.time()
    clicked = False
    while not clicked:
        matches = positions(img, threshold=threshold)
        if len(matches) == 0:
            hast_timed_out = time.time() - start > timeout
            if hast_timed_out:
                if name is not None:
                    pass
                return False
            continue

        x, y, w, h = matches[0]
        pos_click_x = x + w / 2
        pos_click_y = y + h / 2
        movetowithrandomness(pos_click_x, pos_click_y, 1)
        pyautogui.click()
        return True


def printscreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:, :, :3]


def positions(target, threshold=ct['default'], img=None):
    if img is None:
        img = printscreen()
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
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
    hero_item_list = positions(images['hero-item'], threshold=ct['common'])
    if len(hero_item_list) == 0:
        return
    x, y, w, h = hero_item_list[len(hero_item_list) - 1]
    movetowithrandomness(x, y, 1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0, -c['click_and_drag_amount'], duration=1, button='left')


def sendall():
    buttons = positions(images['send-all'], threshold=ct['go_to_work_btn'])
    for (x, y, w, h) in buttons:
        movetowithrandomness(x + (w / 2), y + (h / 2), 1)
        pyautogui.click()
    return len(buttons)

def restall():
    logger('🏢 Laying Heroes to Rest')
    gotoheroes()
    time.sleep(1)
    buttons = positions(images['rest-all'], threshold=ct['go_to_work_btn'])
    for (x, y, w, h) in buttons:
        movetowithrandomness(x + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        time.sleep(2)
    return len(buttons)

def ishome(hero, buttons):
    y = hero[1]

    for (_, button_y, _, button_h) in buttons:
        isbelow = y < (button_y + button_h)
        isabove = y > (button_y - button_h)
        if isbelow and isabove:
            return False
    return True


def isworking(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isbelow = y < (button_y + button_h)
        isabove = y > (button_y - button_h)
        if isbelow and isabove:
            return False
    return True


def clickgreenbarbuttons():
    offset = 140

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d Green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d Buttons detected' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        if not isworking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d Green bar buttons detected' % len(not_working_green_bars))
        logger('👆 Clicking on %d heroes' % len(not_working_green_bars))

    hero_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
        movetowithrandomness(x + offset + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        hero_clicks_cnt = hero_clicks_cnt + 1
        if hero_clicks_cnt > 20:
            logger('⚠️ There were too many clicks on heroes, try to increase the go_to_work_btn threshold')
            return
    return len(not_working_green_bars)


def clickfullbarbuttons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isworking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicking on %d heroes' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        movetowithrandomness(x + offset + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)


def gotoheroes():
    if clickbtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    time.sleep(1)
    clickbtn(images['hero-icon'])
    time.sleep(randint(1, 3))


def gotogame():
    clickbtn(images['x'])

    clickbtn(images['treasure-hunt-icon'])


def refreshheroespositions():
    logger('🔃 Atualizando posição dos heróis')
    clickbtn(images['go-back-arrow'])
    clickbtn(images['treasure-hunt-icon'])


def login():
    global login_attempts
    logger('😿 Checking if the game has disconnected')
    if clickbtn(images['connect-wallet'], timeout=15):
        logger('🎉 Wallet connection button found, logging in!')
        login_attempts = login_attempts + 1
        time.sleep(3)
        if clickbtn(images['select-wallet-2'], timeout=25):
            time.sleep(10)
            refreshheroes()
            login_attempts = 0
            return

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl', 'f5')
        return

    else:
        pass
    if clickbtn(images['ok'], timeout=5):
        time.sleep(10)
        login()
        pass

def sendheroeshome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len(hero_positions) == 0:
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('No hero that should be sent home found.')
        return
    print(' %d Heroes that must be sent home found.' % n)
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not ishome(position, go_home_buttons):
            print(isworking(position, go_work_buttons))
            if not isworking(position, go_work_buttons):
                print('Hero is not working, sending home.')
                movetowithrandomness(go_home_buttons[0][0] + go_home_buttons[0][2] / 2, position[1] + position[3] / 2,
                                     1)
                pyautogui.click()
            else:
                print('Hero is working, will not be sent home.')
        else:
            print('Hero is already in the house, or the house is full.')


def sendheroestowork():
    if c['select_heroes_mode'] == 'full':
        return clickfullbarbuttons()
    elif c['select_heroes_mode'] == 'green':
        return clickgreenbarbuttons()
    else:
        return sendall()


def refreshheroes():
    logger('🏢 Looking for heroes to work')

    gotoheroes()

    if c['select_heroes_mode'] == 'full':
        logger('⚒️ Sending full-energy heroes to work', 'green')
    elif c['select_heroes_mode'] == 'green':
        logger('⚒️ Sending Heroes with Green Energy to Work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    empty_scrolls_attempts = c['scroll_attempts']
    send_all_work = False
    if not ch['enable'] and c['select_heroes_mode'] == 'all':
        time.sleep(1)
        send_all_work = sendall()
        if send_all_work:
            logger('💪 ALL heroes sent to work')
        time.sleep(2)

    if not send_all_work:
        while empty_scrolls_attempts > 0:
            sendheroestowork()
            sendheroeshome()
            empty_scrolls_attempts = empty_scrolls_attempts - 1
            scroll()
            time.sleep(2)
        logger('💪 {} Heroes sent to work'.format(hero_clicks))
    gotogame()


def gobalance():
    logger('Checking your balance')
    time.sleep(5)
    global saldo_atual
    clickbtn(images['consultar-saldo'])
    i = 10
    coins_pos = positions(images['coin-icon'], threshold=ct['default'])
    while len(coins_pos) == 0:
        if i <= 0:
            break
        i = i - 1
        coins_pos = positions(images['coin-icon'], threshold=ct['default'])
        time.sleep(5)

    if len(coins_pos) == 0:
        logger('Balance not found.')
        clickbtn(images['x'])
        return

    left, top, width, height = coins_pos[0]
    left = left - 44
    top = top + 130
    width = 200
    height = 50

    myscreen = pyautogui.screenshot(region=(left, top, width, height))
    img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\targets\saldo1.png'
    myscreen.save(img_dir)
    time.sleep(2)
    enviar = ('🚨 Your balance Bcoins 🚀🚀🚀 in %s' % curwind)
    telsendtext(enviar)
    telsendphoto(img_dir)

    clickbtn(images['x'])


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
        home_heroes = loadheroestosendhome()
    else:
        print('>>---> Home mode not enabled')
    print('\n')

    print(cat)
    time.sleep(5)
    t = c['time_intervals']
    global windows
    windows = []

    for window in pygetwindow.getWindowsWithTitle('Bombcrypto'):
        if window.title.count('bombcrypto-multibot') >= 1:
            continue

        windows.append({
            'window': window,
            'login': 0,
            'heroes': 0,
            'balance': 0,
            'new_map': 0,
            'refresh_heroes': 0,
            'refresh_page': time.time()
        })

    if len(windows) >= 1:
        print('>>---> %d windows named Bombcrypto found!' % len(windows))
        telsendtext(
            '🔌 Bot starting in %d accounts. \n\n 💰 It is time to make some BCoins!!!' % len(windows))

        while True:
            for currentWindow in windows:
                currentWindow['window'].activate()
                if not currentWindow['window'].isMaximized:
                    currentWindow['window'].maximize()

                print('>>---> Current window: %s' % currentWindow['window'].title)

                time.sleep(2)
                now = time.time()

                if now - currentWindow['refresh_page'] > addrandomness(t['check_for_refresh_page'] * 60):
                    logger('🔃 Refreshing the game')
                    currentWindow['refresh_page'] = now
                    restall()
                    pyautogui.hotkey('ctrl', 'f5')

                if now - currentWindow['heroes'] > addrandomness(t['send_heroes_for_work'] * 60):
                    currentWindow['heroes'] = now
                    refreshheroes()

                if now - currentWindow['login'] > addrandomness(t['check_for_login'] * 60):
                    sys.stdout.flush()
                    currentWindow['login'] = now
                    login()

                if now - currentWindow['new_map'] > t['check_for_new_map_button']:
                    currentWindow['new_map'] = now

                if clickbtn(images['new-map']):
                    telsendtext(f'We completed another map in %s' % currentWindow['window'].title)
                    loggerMapClicked()
                    time.sleep(3)
                    num_jaulas = len(positions(images['jail'], threshold=0.8))
                    if num_jaulas > 0:
                        telsendtext(
                            f'Congratulations we have {num_jaulas} new cage(s) on the new map 🎉🎉🎉 in %s' % currentWindow[
                                'window'].title)

                if now - currentWindow['refresh_heroes'] > addrandomness(t['refresh_heroes_positions'] * 60):
                    currentWindow['refresh_heroes'] = now
                    time.sleep(2)
                    refreshheroespositions()

                if now - currentWindow['balance'] > addrandomness(t['get_balance'] * 60):
                    currentWindow['balance'] = now
                    global curwind
                    curwind = currentWindow['window'].title
                    gobalance()

                logger(None, progress_indicator=True)

                sys.stdout.flush()

                time.sleep(1)

    else:
        print('>>---> No windows named Bombcrypto found!')


if __name__ == '__main__':
    main()
