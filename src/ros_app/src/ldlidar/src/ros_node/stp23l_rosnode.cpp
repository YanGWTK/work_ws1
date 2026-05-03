/**
 * @file main.cpp
 * @author LDRobot (support@ldrobot.com)
 * @brief  main process App
 *         This code is only applicable to LDROBOT LiDAR LD06 products 
 * sold by Shenzhen LDROBOT Co., LTD    
 * @version 0.1
 * @date 2021-10-28
 *
 * @copyright Copyright (c) 2021  SHENZHEN LDROBOT CO., LTD. All rights
 * reserved.
 * Licensed under the MIT License (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License in the file LICENSE
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "ros_api.h"
#include "lipkg.h"

void  ToMessagePublish(uint16_t distance,
    LaserSingleMeasureSetting& setting, ros::Publisher& lidarpub);

int main(int argc, char **argv) {
  ros::init(argc, argv, "ldldiar_publisher");
  ros::NodeHandle nh;  // create a ROS Node
  ros::NodeHandle nh_private("~");
  std::string product_name;
	std::string port_name;
  int serial_port_baudrate;
  LaserSingleMeasureSetting setting;
	
  nh_private.getParam("product_name", product_name);
	nh_private.getParam("topic_name", setting.topic_name);
	nh_private.getParam("port_name", port_name);
  nh_private.param("port_baudrate", serial_port_baudrate, int(230400));
	nh_private.param("frame_id", setting.frame_id, std::string("base_laser"));

  ldlidar::LiPkg *lidar_commh = new ldlidar::LiPkg();
  ldlidar::CmdSerialInterfaceLinux *cmd_port = new ldlidar::CmdSerialInterfaceLinux();

  ROS_INFO_STREAM("[ldrobot] SDK Pack Version is: " << lidar_commh->GetSdkVersionNumber());
  ROS_INFO("[ldrobot] <product_name>: %s", product_name.c_str());
  ROS_INFO("[ldrobot] <topic_name>: %s", setting.topic_name.c_str());
  ROS_INFO("[ldrobot] <port_name>: %s", port_name.c_str());
  ROS_INFO("[ldrobot] <port_baudrate>: %d", serial_port_baudrate);
  ROS_INFO("[ldrobot] <frame_id>: %s", setting.frame_id.c_str());

  if (port_name.empty()) {
    ROS_ERROR("[ldrobot] input <port_name> param is null");
    exit(EXIT_FAILURE);
  }
  
  lidar_commh->SetProductType(ldlidar::LDType::STP_23L);
  
  cmd_port->SetReadCallback(std::bind(&ldlidar::LiPkg::CommReadCallback, lidar_commh, std::placeholders::_1, std::placeholders::_2));
  
  if (!cmd_port->Open(port_name, serial_port_baudrate)) {
    ROS_ERROR("open lidar serial device:%s is fail.", port_name.c_str());
    exit(EXIT_FAILURE);
  } else {
    ROS_INFO("open lidar serial device:%s is success.", port_name.c_str());
  }

  // stop measure
  {
    if (!lidar_commh->SendCmd(cmd_port, 0x00, ldlidar::PACK_STOP)) {
      ROS_ERROR("Send cmd PACK_STOP is fail.");
      exit(EXIT_FAILURE);
    } 
    auto st_time = std::chrono::steady_clock::now();
    bool wait_ack = false;
    while ((!wait_ack) && (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-st_time).count() < 1000)) {
      if (lidar_commh->IsWorkStopReady()) {
        lidar_commh->ResetWorkStopReady();
        wait_ack = true;
       }
       usleep(100);
    }

    // if (!wait_ack) {
    //   ROS_ERROR("stop cmd is not ack");
    //   exit(EXIT_FAILURE);
    // } else {
    //   ROS_INFO("lidar device stop measure.");
    // }
  }

  // get lidar version inf
  ROS_INFO("Get lidar version information.");
  if (!lidar_commh->SendCmd(cmd_port, 0x00, ldlidar::PACK_VERSION)) {
    ROS_ERROR("Send cmd PACK_VERSION is fail.");
    exit(EXIT_FAILURE);
  }
  auto start_time = std::chrono::steady_clock::now();
  ldlidar::LidarDeviceVerInfoTypeDef lidar_device_inf;
  bool wait_result = false;
  ROS_INFO("Wait recv lidar version information.");
  while ((!wait_result) && \
    (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-start_time).count() < 1000)) {
    if (lidar_commh->IsDeviceInfoReady()) {
      lidar_commh->ResetDeviceInfoReay();
      lidar_device_inf = lidar_commh->GetLidarDeviceVersionInfo();
      wait_result = true;
    }
    usleep(100);
  }

  if (wait_result) {
    ROS_INFO("Get lidar version information is success.");
    ROS_INFO("lidar firmware version:%s", lidar_device_inf.firmware_ver.c_str());
    ROS_INFO("lidar hardware version:%s", lidar_device_inf.hardware_ver.c_str());
    ROS_INFO("lidar manufacture times:%s",lidar_device_inf.manufacture_times.c_str());
    ROS_INFO("lidar mcu id number:%s", lidar_device_inf.mcu_id.c_str());
    ROS_INFO("lidar sn code:%s", lidar_device_inf.sn.c_str());
    ROS_INFO("lidar pitch angle:%d,%d,%d,%d",lidar_device_inf.pitch_angle[0],
      lidar_device_inf.pitch_angle[1],
      lidar_device_inf.pitch_angle[2],
      lidar_device_inf.pitch_angle[3]);
    ROS_INFO("lidar blind area, near:%d,far:%d", lidar_device_inf.blind_area_most_near, lidar_device_inf.blind_area_most_far);
    ROS_INFO("lidar frequence val:%d", lidar_device_inf.frequence); 
  } 
  // else {
  //   ROS_ERROR("Get lidar version information is fail.");
  //   exit(EXIT_FAILURE);
  // }
  
  // start measure
  ROS_INFO("Start measure.");
  if (!lidar_commh->SendCmd(cmd_port, 0x00, ldlidar::PACK_GET_DISTANCE)) {
    ROS_ERROR("Send cmd PACK_GET_DISTANCE is fail.");
    exit(EXIT_FAILURE);
  }
  
  // create a ROS topic
  ros::Publisher lidar_pub = nh.advertise<sensor_msgs::Range>(setting.topic_name, 10);  
  
  ros::Rate r(10); //10hz
  auto last_time = std::chrono::steady_clock::now();
  while (ros::ok()) {
    if (lidar_commh->IsFrameReady()) {
      lidar_commh->ResetFrameReady();
      last_time = std::chrono::steady_clock::now();
      ldlidar::LaserFrameDataType laser_frame_data;
      if (lidar_commh->GetLaserMeasureData(laser_frame_data)) {
        ///// 遍历测量帧数据
        ROS_INFO("get lidar frame Data, timestamp:%d", laser_frame_data.timestamp);
        for (int i = 0; i < laser_frame_data.numbers; i++) {
          ToMessagePublish(laser_frame_data.points[i].distance, setting, lidar_pub);
          ROS_INFO("Measure data: ");
          ROS_INFO("distance:%d,noise:%d,peak:%d,confidence:%d,intg:%d,reftof:%d",
           laser_frame_data.points[i].distance,
           laser_frame_data.points[i].noise,
           laser_frame_data.points[i].peak,
           laser_frame_data.points[i].confidence,
           laser_frame_data.points[i].intg,
           laser_frame_data.points[i].reftof);
          ROS_INFO("-------------------------------");
        }
      } else {
        ROS_ERROR("get lidar frame data error");
        exit(EXIT_FAILURE);
      }
    }

    if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-last_time).count() > 1000) { 
			ROS_ERROR("[ldrobot] publish data is time out, please check lidar device");
			exit(EXIT_FAILURE);
		}

    r.sleep();
  }

  // stop measure
  {
    if (!lidar_commh->SendCmd(cmd_port, 0x00, ldlidar::PACK_STOP)) {
      ROS_ERROR("Send cmd PACK_STOP is fail.");
      exit(EXIT_FAILURE);
    } 
    auto st_time = std::chrono::steady_clock::now();
    bool wait_ack = false;
    while ((!wait_ack) && (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-st_time).count() < 1000)) {
      if (lidar_commh->IsWorkStopReady()) {
        lidar_commh->ResetWorkStopReady();
        wait_ack = true;
       }
       usleep(100);
    }

    if (!wait_ack) {
      ROS_ERROR("stop cmd is not ack");
      exit(EXIT_FAILURE);
    } else {
      ROS_INFO("lidar device stop measure.");
    }
  }

  cmd_port->Close();
  
  delete lidar_commh;
  lidar_commh = nullptr;
  delete cmd_port;
  cmd_port = nullptr;
  
  return 0;
}

void  ToMessagePublish(uint16_t distance, 
    LaserSingleMeasureSetting& setting, ros::Publisher& lidarpub) {

  sensor_msgs::Range output;

  output.header.stamp = ros::Time::now();
  output.header.frame_id = setting.frame_id;
  output.radiation_type = sensor_msgs::Range::INFRARED;
  output.field_of_view = 0.1;
  output.min_range = 0;
  output.max_range = 12;
  output.range = distance / 1000.f; // unit is meter.
  
  lidarpub.publish(output);
}


/********************* (C) COPYRIGHT SHENZHEN LDROBOT CO., LTD *******END OF
 * FILE ********/
