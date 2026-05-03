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

from Speech_Lib import Speech
from garbage_library import GarbageTransport
from yahboomcar_msgs.msg import *
spe = Speech()

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
        self.garbage_result = 999
        self.garbage_transbot = GarbageTransport()
        self.sub_msg = rospy.Subscriber('DetectMsg',TargetArray,self.sub_msg_callback)
        print("init done")
    def process(self):
        sleep(0.05)
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
                    

              
    def sub_msg_callback(self,msg):
        #print("------------------")
        if(len(msg.data)!=0):
        	print(msg.data[0].frame_id)
        	self.name = msg.data[0].frame_id
        	self.process()
        


if __name__ == '__main__':
    rospy.init_node('garbage_transport',anonymous=False)
    transport_garbage = Spech_Garbage_Identify()
    rospy.spin()

        


