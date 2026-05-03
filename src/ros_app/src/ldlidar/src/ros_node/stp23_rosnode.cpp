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

  lidar_commh->SetProductType(ldlidar::LDType::STP_23);
 
  cmd_port->SetReadCallback(std::bind(&ldlidar::LiPkg::CommReadCallback, lidar_commh, std::placeholders::_1, std::placeholders::_2));
  
  if (cmd_port->Open(port_name, (uint32_t)serial_port_baudrate)) {
    ROS_INFO("[ldrobot] open %s device %s is success", product_name.c_str(), port_name.c_str());
  }else {
    ROS_ERROR("[ldrobot] open %s device %s is fail", product_name.c_str(), port_name.c_str());
    exit(EXIT_FAILURE);
  }
  
  ros::Publisher lidar_pub = nh.advertise<sensor_msgs::Range>(setting.topic_name, 10);  // create a ROS topic
  
  ros::Rate r(10); //10hz
  auto last_time = std::chrono::steady_clock::now();
  while (ros::ok()) {
    if (lidar_commh->IsFrameReady()) {
      lidar_commh->ResetFrameReady();
      last_time = std::chrono::steady_clock::now();
      ldlidar::LaserPointDataType laserdata;
      if (lidar_commh->GetLaserMeasureData(laserdata)) {
        for (int i = 0; i < laserdata.numbers; i++) {
          ToMessagePublish(laserdata.distance[i], setting, lidar_pub);
          ROS_INFO("[ldrobot] Measure data: ");
          ROS_INFO("distance(mm): %d, intensity: %d", laserdata.distance[i], laserdata.intensity[i]);
          ROS_INFO("-------------------------------");
        }
      }
    }

    if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-last_time).count() > 1000) { 
			ROS_ERROR("[ldrobot] publish data is time out, please check lidar device");
			exit(EXIT_FAILURE);
		}

    r.sleep();
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
