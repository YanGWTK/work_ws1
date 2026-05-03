import rospy
import threading
import cv2 as cv
from time import sleep, time
from transport_common import ROSNav

class Img_QR_transport:
     def __init__(self):
        self.ros_nav = ROSNav()
        self.model = "Init"
        self.Grip_status = False
        self.QR_name = {}
        self.Img_name = {}
        self.index = 0
     def get_QR(self, img):
     
     def get_Img(self, img):
     
     def process(self, frame, action, text):
     
     def comeback(self):
        self.ros_nav.PubTargetPoint(self.ros_nav.start_point)
        self.model = "come_back"
        
     def Reset(self):
        self.ros_nav.goal_result = 0
        self.model = "Init"
        self.Grip_status = False
        self.ros_nav.Transport_status = False
        self.color_name = {}
        self.index = 0
        
     def Grip_down(self):
        self.model = "Grip_down"
        self.ros_nav.goal_result = 0
        joints = [90, 2.0, 60.0, 40.0, 90, 140]
        self.ros_nav.pubArm(joints, run_time=1000)
        sleep(1)
        self.ros_nav.pubArm([], 6, 30)
        sleep(0.5)
        joints = [90, 145, 0, 45, 90, 30]
        self.ros_nav.pubArm(joints, run_time=1000)
        sleep(1)
        self.comeback()
     
     def Grip_Target(self):
        self.model = "Grip_Target"
        # print "开启夹取流程线程"
        self.Grip_status = True
        self.buzzer_loop()
        joints = [90, 145, 0, 45, 90, 30]
        self.ros_nav.pubArm(joints, run_time=1000)
        sleep(0.5)
        self.buzzer_loop()
        self.ros_nav.pubArm([], 6, 146)
        sleep(1)
        self.model = "Transport"

    def buzzer_loop(self):
        self.ros_nav.pubBuzzer(True)
        sleep(1)
        self.ros_nav.pubBuzzer(False)
        sleep(1)    
        
if __name__ == '__main__':
    rospy.init_node('img_QR_transport',anonymous=False)
    color_transport = ColorTransport()
    capture = cv.VideoCapture(0)
    cv_edition = cv.__version__
    if cv_edition[0] == '3': capture.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'XVID'))
    else: capture.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    text = '0'
    while capture.isOpened():
        start = time()
        ret, frame = capture.read()
        action = cv.waitKey(10) & 0xFF
        if action == ord('q') or action == 113: break
        frame = color_transport.process(frame, action, text)
        text = "FPS : " + str(int(1 / (time() - start)))
        if color_transport.ros_nav.img_show: cv.imshow("frame", frame)
    capture.release()
    cv.destroyAllWindows()
 
 
 
