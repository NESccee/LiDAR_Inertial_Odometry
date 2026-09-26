# T100 Livox ROS 2 FAST-LIO

本目录包含 DJI T100 雷达的 Livox SDK2、ROS 2 驱动和 FAST-LIO。

## 目录结构

~~~text
bsp/
  livox-sdk2/                              Livox SDK2
  livox_ros_driver2/src/livox_ros_driver2/ ROS 2 驱动包源码
  fast_lio/                                FAST-LIO ROS 2
~~~

GitHub 组合仓库中的结构不同，驱动包直接位于：

~~~text
livox_ros_driver2/
  package.xml
  CMakeLists.txt
  launch_ROS2/
  config/T100_config.json
~~~

## 本地 bsp 工作空间编译

本机实际使用的是 ROS 2 工作空间：

~~~text
~/T100_ws/bsp/livox_ros_driver2/
  src/livox_ros_driver2/    ROS 2 驱动包源码
  install/                  驱动安装结果
~~~

编译驱动：

~~~bash
cd ~/T100_ws/bsp/livox_ros_driver2/src/livox_ros_driver2
./build.sh jazzy
~~~

加载本机已安装的驱动：

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
~~~

## 编译 GitHub 组合仓库

假设组合仓库位于 ~/T100_ws/LiDAR_Inertial_Odometry：

~~~bash
cd ~/T100_ws/LiDAR_Inertial_Odometry
source /opt/ros/jazzy/setup.bash

colcon build --base-paths livox_ros_driver2 --build-base build_driver --install-base install_driver --executor sequential --parallel-workers 1 --packages-select livox_ros_driver2 --cmake-args -DROS_EDITION=ROS2 -DDISTRO_ROS=jazzy
source install_driver/setup.bash
~~~

FAST-LIO 使用独立构建目录，并固定使用 CPU 0：

~~~bash
cd ~/T100_ws/LiDAR_Inertial_Odometry/fast_lio
source /opt/ros/jazzy/setup.bash
source ../install_driver/setup.bash
git submodule update --init --depth 1

taskset -c 0 env MAKEFLAGS=-j1 CMAKE_BUILD_PARALLEL_LEVEL=1 colcon --log-base .colcon_log build --base-paths . --build-base .colcon_build --install-base .colcon_install --executor sequential --parallel-workers 1 --packages-select fast_lio --cmake-args -DCMAKE_BUILD_TYPE=Release
source .colcon_install/setup.bash
~~~

## 配置网络

T100 地址为 192.168.1.10，主机连接雷达的网卡需要配置为 192.168.1.20/24：

~~~bash
sudo ip link set end0 up
sudo ip addr replace 192.168.1.20/24 dev end0
ping -I end0 -c 2 192.168.1.10
~~~

## 本机启动

终端 1，启动 T100 驱动。启动文件会自动发送 SAMPLING 控制命令：

~~~bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
ros2 launch livox_ros_driver2 msg_T100_launch.py
~~~

终端 2，启动 FAST-LIO。本机 FAST-LIO 安装环境是 bsp/fast_lio/.colcon_install：

~~~bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
source ~/T100_ws/bsp/fast_lio/.colcon_install/setup.bash
ros2 launch /home/lckfb/T100_ws/bsp/fast_lio/launch/mapping.launch.py config_path:=/home/lckfb/T100_ws/bsp/fast_lio/config config_file:=t100.yaml rviz:=false
~~~

## 验证

~~~bash
ros2 topic hz /livox/lidar
ros2 topic hz /livox/imu
ros2 topic hz /Odometry
ros2 topic echo /Odometry --field pose.pose.position
~~~

正常运行时，驱动发布 /livox/lidar 和 /livox/imu，FAST-LIO 发布 /Odometry、/cloud_registered 和 /cloud_registered_body。

## 端口

~~~text
控制：60000
点云：60001
IMU：60003
~~~
