# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO 
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus


# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
UP = False
DOWN = True
ON = True
OFF = False
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (.1, .1,.1, 1) # (WHITE)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()
arm = stepper(port = 0, speed = 10)

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////
	
class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    armPosition = 0
    lastClick = time.clock()
    highArm = False
    magnet = False

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.clock()
        if ((currentTime - self.lastClick) > DEBOUNCE):
            processInput = True
        self.lastClick = currentTime
        return processInput

    def toggleArm(self):
        self.highArm = not self.highArm
        if self.highArm:
            cyprus.set_pwm_values(1, period_value=100000,
                                  compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)

        else:
            cyprus.set_pwm_values(1, period_value=100000,
                                  compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)

        print("Process arm movement here")

    def toggleMagnet(self):
        self.magnet = not self.magnet
        if self.magnet:
            cyprus.set_servo_position(2, 1)

        else:
            cyprus.set_servo_position(2, .5)

        print("Process magnet here")
        
    def auto(self):
        x = -21.12
        y = -12.7
        if self.isBallOnTallTower():
            x = -12.75
            y = -21.12

        arm.home(1)

        arm.go_to_position(x)
        self.toggleMagnet
        sleep(0.5)
        self.toggleArm()
        sleep(1)
        self.toggleArm()
        sleep(0.5)
        arm.go_to_position(y)
        sleep(0.5)
        self.toggleArm()
        sleep(0.7)
        self.toggleMagnet()
        sleep(0.5)
        self.toggleArm()
        sleep(0.5)
        arm.home(1)

        print("Run the arm automatically here")


    def setArmPosition(self, position):
        if arm.get_position_in_units() == 0:
            self.ids.moveArm.value = 0
        self.ids.armControlLabel.text = str(position)
        arm.go_to_position(position)

        print(arm.get_position_in_units())
        print("Move arm here")

    def homeArm(self):
        arm.home(self.homeDirection)
        
    def isBallOnTallTower(self):
        print("Determine if ball is on the top tower")
        if cyprus.read_gpio() & 0b0001:
            sleep(0.5)
            if cyprus.read_gpio() & 0b0001:
                print("Proximity sensor is off")
                return False

        return True

    def isBallOnShortTower(self):
        print("Determine if ball is on the bottom tower")
        if cyprus.read_gpio() & 0b0010:
            print("NO")
            return False
        print("yes")
        return True

    def initialize(self):
        cyprus.initialize()
        cyprus.setup_servo(1)
        cyprus.setup_servo(2)
        cyprus.set_servo_position(2, .5)
        self.homeArm()
        print("Home arm and turn off magnet")

    def resetColors(self):
        self.ids.armControl.color = YELLOW
        self.ids.magnetControl.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()
    
sm.add_widget(MainScreen(name = 'main'))


# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()
