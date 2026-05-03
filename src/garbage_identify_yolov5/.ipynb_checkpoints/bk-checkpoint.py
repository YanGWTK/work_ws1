#!/usr/bin/env python3
# coding: utf-8
#import Arm_Lib.
import rospy
import cv2 as cv
import threading
from time import sleep
#from dofbot_config import *
import ipywidgets as widgets
from IPython.display import display
from garbage_identify import garbage_identify
from Speech_Lib import Speech
from garbage_library import GarbageTransport
spe = Speech()
target = garbage_identify()
num=0
dp = []
msg = {}

recyclable_waste=['Newspaper','Zip_top_can','Book','Old_school_bag']
toxic_waste=['Syringe','Expired_cosmetics','Used_batteries','Expired_tablets']
wet_waste=['Fish_bone','Egg_shell','Apple_core','Watermelon_rind']
dry_waste=['Toliet_paper','Peach_pit','Cigarette_butts','Disposable_chopsticks']

class Spech_Garbage_Identify:
    def __init__(self):
        self.img = None
        self.garbage_index=0
        self.name = None
        self.target = garbage_identify()
        self.garbage_result = 999
        self.garbage_transbot = GarbageTransport()	
    def process(self,img,action):
        sleep(0.05)
        img,self.name = self.target.garbage_run(img)
        name = self.name
        print(self.name)
        if spe.speech_read() == 94:
            print("kkk")
            if  self.name!=None:
                self.garbage_transbot.model = "Grip"
                #self.garbage_transbot.buzzer_loop()
                #self.garbage_result = self.garbage_type.garbage_result(name)            
                if self.name == 'Newspaper':
                    spe.void_write(96)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(1)
                if self.name == 'Zip_top_can':
                    spe.void_write(94)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(1)
                        
                if self.name == 'Book':
                    spe.void_write(97)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(1)
                        
                if self.name == 'Old_school_bag':
                    spe.void_write(95)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(1)
                        
                if self.name == 'Syringe':
                    spe.void_write(98)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(2)
                        
                if self.name == 'Expired_cosmetics':
                    spe.void_write(100)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(2)
                        
                if self.name == 'Used_batteries':
                    spe.void_write(99)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(2)
                        
                if self.name == 'Expired_tablets':
                    spe.void_write(101)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(2)
                        
                if self.name == 'Fish_bone':
                    spe.void_write(102)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(3)
                        
                if self.name == 'Egg_shell':
                    spe.void_write(105)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(3)
                        
                if self.name == 'Watermelon_rind':
                    spe.void_write(103)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(3)
                        
                if self.name == 'Apple_core':
                    spe.void_write(104)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(3)  
                        
                if self.name == 'Toilet_paper':
                    spe.void_write(109)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(4)
                        
                if self.name == 'Cigarette_butts':
                    spe.void_write(107)
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(4)
                        
                if self.name == 'Peach_pit':
                    spe.void_write(108)
                    #self.garbage_transbot.buzzer_loop()
                    while self.garbage_transbot.model !="init_point":
                        self.garbage_transbot.process(4)
                    
                if self.name == 'Disposable_chopsticks':
                    spe.void_write(106)
                    self.garbage_transbot.process(4)
            self.name=None
            self.garbage_transbot.Reset()
                    
                    
        return img

              



if __name__ == '__main__':
    rospy.init_node('garbage_transport',anonymous=False)
    spech_garbage_identify = Spech_Garbage_Identify()
    # 打开摄像头 Open camera
    capture = cv.VideoCapture(0)
    garbage_identify
    # Be executed in loop when the camera is opened normally 
    # 当摄像头正常打开的情况下循环执行
    while capture.isOpened():
            ret,img = capture.read()
            action = cv.waitKey(10)&0xff
            if action==113:break
            #cv.rectangle(img, (185, 128), (442, 353), (0, 255, 0), 2)
            img = spech_garbage_identify.process(img,action)
            cv.imshow("img",img)

    capture.release()
    cv.destoryALLWindows()
        


