# Version: 10/01/2022

# -*- coding: utf-8 -*-  
from cv2 import cv2  
from telegram import *
from src.logger import logger, loggerMapClicked
from os import listdir
from random import randint
from random import random
from datetime import datetime

import os
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml
import datetime
import cv2

# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
ch = c['home']
pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

cat = """
>>---> Press ctrl + c to kill the bot.
>>---> Some configs can be found in the config.yaml file."""

account = '💳 - _Account 01_'
#account = '💳 - _Account 02_'
#account = '💳 - _Account 03_'

def addRandomness(n, randomn_factor_size=None):
    """Returns n with randomness
    Parameters:
        n (int): A decimal integer
        randomn_factor_size (int): The maximum value+- of randomness that will be
            added to n
    Returns:
        int: n with randomness
    """

    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)

def remove_suffix(input_string, suffix):
    """Returns the input_string without the suffix"""

    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images(dir_path='./targets/'):
    """ Programatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix
    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

def loadHeroesToSendHome():
    """Loads the images in the path and saves them as a list"""
    file_names = listdir('./targets/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d heroes that should be sent home loaded' % len(heroes))
    return heroes

def show(rectangles, img = None):
    """ Show an popup with rectangles showing the rectangles[(x, y, w, h),...]
        over img or a printSreen if no img provided. Useful for debugging"""

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)

def clickBtn(img, timeout=3, threshold = ct['default']):
    """Search for img in the scree, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)

        if(len(matches)==0):
            has_timed_out = time.time()-start > timeout
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True

    return False

def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
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

    commoms = positions(images['commom-text'], threshold = ct['commom'])
    if (len(commoms) == 0):
        return
    x,y,w,h = commoms[len(commoms)-1]
#
    moveToWithRandomness(x,y,1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')

def clickButtons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    for (x, y, w, h) in buttons:
        moveToWithRandomness(x+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(buttons)

def isHome(hero, buttons):
    y = hero[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            # if send-home button exists, the hero is not home
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
    # ele clicka nos q tao trabaiano mas axo q n importa
    offset = 140

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d buttons detected' % len(buttons))


    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d buttons with green bar detected' % len(not_working_green_bars))
        logger('👆 Clicking in %d heroes' % len(not_working_green_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    hero_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        hero_clicks_cnt = hero_clicks_cnt + 1
        if hero_clicks_cnt > 20:
            logger('⚠️ Too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
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
        logger('👆 Clicking in %d heroes' % len(not_working_full_bars))

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

    #TODO tirar o sleep quando colocar o pulling
    time.sleep(1)
    clickBtn(images['hero-icon'])
    time.sleep(randint(1,3))

def goToGame():
    # in case of server overload popup
    clickBtn(images['x'])
    # time.sleep(3)
    clickBtn(images['x'])

    clickBtn(images['treasure-hunt-icon'])

def refreshHeroesPositions():

    logger('🔃 Refreshing Heroes Positions')
    clickBtn(images['go-back-arrow'])
    clickBtn(images['treasure-hunt-icon'])

    # time.sleep(3)
    clickBtn(images['treasure-hunt-icon'])

def login(account):
    global login_attempts, message
    logger('😿 Checking if game has disconnected')   

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        message = telegram_bot_sendtext("Account " + str(account) + " - CRITICAL\n\n 🛑 - Bomb off? Check the game channel")
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

    if clickBtn(images['connect-wallet'], timeout = 10):
        logger('🎉 Connect wallet button detected, logging in!')
        login_attempts += 1
        #TODO mto ele da erro e poco o botao n abre
        # time.sleep(10)

    if clickBtn(images['select-wallet-2'], timeout=8):
        # sometimes the sign popup appears imediately
        login_attempts += 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        if clickBtn(images['treasure-hunt-icon'], timeout = 15):
            # print('sucessfully login, treasure hunt btn clicked')
            message = telegram_bot_sendtext("Account " + str(account) + "\n\n 🟢 - Sucessfully login")
            login_attempts = 0
        return
        # click ok button

    if not clickBtn(images['select-wallet-1-no-hover'], ):
        if clickBtn(images['select-wallet-1-hover'], threshold = ct['select_wallet_buttons'] ):
            pass
            # o ideal era que ele alternasse entre checar cada um dos 2 por um tempo 
            # print('sleep in case there is no metamask text removed')
            # time.sleep(20)
    else:
        pass
        # print('sleep in case there is no metamask text removed')
        # time.sleep(20)

    if clickBtn(images['select-wallet-2'], timeout = 20):
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        # time.sleep(25)
        if clickBtn(images['treasure-hunt-icon'], timeout=25):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        # time.sleep(15)

    if clickBtn(images['ok'], timeout=5):
        pass
        # time.sleep(15)
        # print('ok button clicked')
    
    # Message to validate the Online
    message = telegram_bot_sendtext("\n\nAccount " + str(account) +" - OKAY")


def sendHeroesHome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len (hero_positions) == 0:
            #TODO maybe pick up match with most wheight instead of first
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('No heroes that should be sent home found.')
        return
    print(' %d heroes that should be sent home found' % n)
    # if send-home button exists, the hero is not home
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])
    # TODO pass it as an argument for both this and the other function that uses it
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not isHome(position,go_home_buttons):
            print(isWorking(position, go_work_buttons))
            if(not isWorking(position, go_work_buttons)):
                print ('hero not working, sending him home')
                moveToWithRandomness(go_home_buttons[0][0]+go_home_buttons[0][2]/2,position[1]+position[3]/2,1)
                pyautogui.click()
            else:
                print ('hero working, not sending him home(no dark work button)')
        else:
            print('hero already home, or home full(no dark home button)')

def refreshHeroes():
    logger('🏢 Search for heroes to work')

    goToHeroes()

    if c['select_heroes_mode'] == "full":
        logger('⚒️ Sending heroes with full stamina bar to work', 'green')
    elif c['select_heroes_mode'] == "green":
        logger('⚒️ Sending heroes with green stamina bar to work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']

    while(empty_scrolls_attempts > 0):
        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
        elif c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons()
        else:
            buttonsClicked = clickButtons()

        sendHeroesHome()

        if buttonsClicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
        scroll()
        time.sleep(2)
    logger('💪 {} heroes sent to work'.format(hero_clicks))
    goToGame()

def balance():
    global saldo_atual, message
    pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\Tesseract.exe"
    clickBtn(images['chest'])

    i = 10
    coins_pos = positions(images['coin-icon'], threshold=ct['default'])
    while(len(coins_pos) == 0):
        if i <= 0:
            break
        i = i - 1
        coins_pos = positions(images['coin-icon'], threshold=ct['default'])
        time.sleep(5)
    
    if(len(coins_pos) == 0):
        logger("Saldo não encontrado.")
        clickBtn(images['x'])
        return

    # a partir da imagem do bcoin calcula a area do quadrado para print
    k,l,m,n = coins_pos[0]
    k -= 44
    l +=  130
    m = 200
    n = 50

    myScreen = pyautogui.screenshot(region=(k, l, m, n))
    img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\targets\saldo1.png'
    myScreen.save(img_dir)
    # Lendo arquivo gerado
    img = cv2.imread(r"D:\Estudos\UDEMY\GIT\bombcrypto-bot\targets\saldo1.png")
    # Print resultado
    print(pytesseract.image_to_string(img))
    time.sleep(2)
        
    clickBtn(images['x'])

def getDifference(then, now=datetime.datetime.now(), interval="horas"):

    duration = now - then
    duration_in_s = duration.total_seconds()

    # Date and Time constants
    yr_ct = 365 * 24 * 60 * 60  # 31536000
    day_ct = 24 * 60 * 60  # 86400
    hour_ct = 60 * 60  # 3600
    minute_ct = 60

    def yrs():
        return divmod(duration_in_s, yr_ct)[0]

    def days():
        return divmod(duration_in_s, day_ct)[0]

    def hrs():
        return divmod(duration_in_s, hour_ct)[0]

    def mins():
        return divmod(duration_in_s, minute_ct)[0]

    def secs():
        return duration_in_s

    return {
        "anos": int(yrs()),
        "dias": int(days()),
        "horas": int(hrs()),
        "minutos": int(mins()),
        "segundos": int(secs()),
    }[interval]

def timeInTheMap():
    try:
        dateStartMap = None
        way = (os.path.dirname(os.path.realpath(__file__)) + r"D:\Estudos\UDEMY\GIT\bombcrypto-bot\tempo_mapa.txt")
        with open(way, "r") as text_file:
            dateStartMap = text_file.readline()
            if dateStartMap == "":
                dateStartMap = datetime.now()

            if not isinstance(dateStartMap, datetime):
                dateStartMap = datetime.strptime(dateStartMap, "%Y-%m-%d %H:%M:%S.%f")
            interval = "horas"
            spentHours = getDifference(
                dateStartMap, now=datetime.now(), interval=interval
            )
            if spentHours == 0:
                interval = "minutos"
                spentHours = getDifference(dateStartMap, now=datetime.now(), interval=interval)
            if spentHours == 0:
                interval = "segundos"
                spentHours = getDifference(dateStartMap, now=datetime.now(), interval=interval)

            telegram_bot_sendtext(f"It took you {spentHours} {interval} to complete the map")
        with open(way, "w") as textFileWrite:
            dateStartMap = datetime.now()
            textFileWrite.write(str(dateStartMap))

    except:
        logger("Failed to get map completion time information.")

def main():
    """Main execution setup and loop"""
    # ==Setup==
    global hero_clicks
    global login_attempts
    global last_log_is_progress
    global message
    global new_maps
    global images
    hero_clicks = 0
    login_attempts = 0
    last_log_is_progress = False

    images = load_images()

    if ch['enable']:
        global home_heroes
        home_heroes = loadHeroesToSendHome()
    else:
        print('\n')
        print('>>---> Home feature not enabled')

    print(cat)
    time.sleep(5)
    t = c['time_intervals']
    
      
    last = {
        "login" : 0,
        "heroes" : 0,
        "new_map" : 0,
        "check_for_captcha" : 0,
        "refresh_heroes" : 0
        }
    # =====================
    last2 = {
        "login" : 0,
        "heroes" : 0,
        "new_map" : 0,
        "check_for_captcha" : 0,
        "refresh_heroes" : 0
        }
    # =====================
    last3 = {
        "login" : 0,
        "heroes" : 0,
        "new_map" : 0,
        "check_for_captcha" : 0,
        "refresh_heroes" : 0
        }
    # =====================

    while True:
        now = time.time()
        now2 = time.time()
        now3 = time.time()
        
        account = 1
    
        while account == 1:
            changeAccount(account)
                                                                    
            if now - last["check_for_captcha"] > addRandomness(t['check_for_captcha'] * 60):
                last["check_for_captcha"] = now
                               
            if now - last["heroes"] > addRandomness(t['send_heroes_for_work'] * 60):
                last["heroes"] = now
                refreshHeroes()

            if now - last["login"] > addRandomness(t['check_for_login'] * 60):
                sys.stdout.flush()
                last["login"] = now
                login(account)

            if now - last["new_map"] > t['check_for_new_map_button']:
                last["new_map"] = now
 
                if clickBtn(images['new-map']):
                    loggerMapClicked()  

            if now - last["refresh_heroes"] > addRandomness( t['refresh_heroes_positions'] * 60):
                last["refresh_heroes"] = now
                refreshHeroesPositions()

                #clickBtn(teasureHunt)
            reduceWindow()
            account = 2
        
        while account == 2:
            changeAccount(account)
                
            if now2 - last2["check_for_captcha"] > addRandomness(t['check_for_captcha'] * 60):
                last2["check_for_captcha"] = now2
                   
            if now2 - last2["heroes"] > addRandomness(t['send_heroes_for_work'] * 60):
                last2["heroes"] = now2
                refreshHeroes()

            if now2 - last2["login"] > addRandomness(t['check_for_login'] * 60):
                sys.stdout.flush()
                last2["login"] = now2
                login(account)

            if now2 - last2["new_map"] > t['check_for_new_map_button']:
                last2["new_map"] = now2
 
                if clickBtn(images['new-map']):
                    loggerMapClicked()

            if now2 - last2["refresh_heroes"] > addRandomness( t['refresh_heroes_positions'] * 60):
                last2["refresh_heroes"] = now2
                refreshHeroesPositions()

                #clickBtn(teasureHunt)
            reduceWindow()
            account = 3
            
        while account == 3:
            changeAccount(account)
            
            if now3 - last3["check_for_captcha"] > addRandomness(t['check_for_captcha'] * 60):
                last3["check_for_captcha"] = now3
                   
            if now3 - last3["heroes"] > addRandomness(t['send_heroes_for_work'] * 60):
                last3["heroes"] = now3
                refreshHeroes()

            if now3 - last3["login"] > addRandomness(t['check_for_login'] * 60):
                sys.stdout.flush()
                last3["login"] = now3
                login(account)

            if now3 - last3["new_map"] > t['check_for_new_map_button']:
                last3["new_map"] = now3
 
                if clickBtn(images['new-map']):
                    loggerMapClicked()                   

            if now3 - last3["refresh_heroes"] > addRandomness( t['refresh_heroes_positions'] * 60):
                last3["refresh_heroes"] = now3
                refreshHeroesPositions()

                #clickBtn(teasureHunt)
            reduceWindow()
            account = 1
            
        logger(None, progress_indicator=True)
        sys.stdout.flush()
        time.sleep(1)

def changeAccount(number):      
    # maximizar a janela
    pyautogui.keyDown('win')
    pyautogui.keyDown(str(number))
    pyautogui.keyUp('win')
    pyautogui.keyUp('str(number)')
    pyautogui.keyDown('alt')
    pyautogui.keyDown('space')
    pyautogui.keyUp('alt')
    pyautogui.keyUp('space')
    pyautogui.keyDown('x') 
    pyautogui.keyUp('x') 

def reduceWindow():
    pyautogui.click(1853,16)
    time.sleep(15)

if __name__ == '__main__':
    main()

#cv2.imshow('img',sct_img)
#cv2.waitKey()

# colocar o botao em pt
# soh resetar posiçoes se n tiver clickado em newmap em x segundo