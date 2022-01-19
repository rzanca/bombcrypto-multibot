import pyautogui
from configuration import Configuration

class AutoUI:
  c = Configuration.c
  pyautogui = pyautogui
  pyautogui.PAUSE = c['time_intervals']['interval_between_movements']
  pyautogui.FAILSAFE = False
  pyautogui.MINIMUM_DURATION = 0.1
  pyautogui.MINIMUM_SLEEP = 0.1
  pyautogui.PAUSE = 2