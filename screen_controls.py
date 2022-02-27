import time
import numpy as np
import mss
import pygetwindow
import pyautogui
from cv2 import cv2
from src.logger import logger, loggerMapClicked
from configuration import Configuration
from autoui import AutoUI
from pyclick import HumanClicker

class ScreenControls:

  @staticmethod
  def getWindowsWithTitle():
    return pygetwindow.getWindowsWithTitle('Bombcrypto')

  @staticmethod
  def printscreen():
    with mss.mss() as sct:
      monitor = sct.monitors[0]
      sct_img = np.array(sct.grab(monitor))
      return sct_img[:, :, :3]
  
  @staticmethod
  def positions(target, threshold=Configuration.threshold['default'], img=None):
    if img is None:
      img = ScreenControls.printscreen()
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

  @staticmethod
  def movetowithrandomness(x, y, t):
    HumanClicker().move((int(x), int(y)), t)

  @staticmethod  
  def clickbtn(img, name=None, timeout=3, threshold=Configuration.threshold['default']):
    logger(None, progress_indicator=True)
    
    start = time.time()
    clicked = False
    
    while not clicked:
      matches = ScreenControls.positions(img, threshold=threshold)
      if len(matches) == 0:
        hast_timed_out = time.time() - start > timeout
        if hast_timed_out:
          return False
        continue

      x, y, w, h = matches[0]
      pos_click_x = x + w / 2
      pos_click_y = y + h / 2
      ScreenControls.movetowithrandomness(pos_click_x, pos_click_y, 1)
      AutoUI.pyautogui.click()
      return True

  @staticmethod
  def inputtype(text):
    time.sleep(2)
    pyautogui.write(text, interval=0.3)
    time.sleep(2)