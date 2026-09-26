# DJI T100 Livox ROS 2 FAST-LIO

本仓库将 DJI T100 360° 激光雷达接入 ROS 2 Jazzy，并使用 FAST-LIO 进行激光惯性里程计。项目包含 Livox SDK2、livox_ros_driver2 和 FAST-LIO ROS 2。

## 源码结构

~~~text
~/T100_ws/bsp/
  livox-sdk2/                         Livox SDK2
  livox_ros_driver2/                  ROS 2 驱动工作空间
    src/livox_ros_driver2/            驱动 ROS 2 包和原生 build.sh
  fast_lio/                           FAST-LIO ROS 2 包
~~~

livox_ros_driver2 必须保留在 ROS 工作空间的 src 目录下。原生 build.sh 会从该目录回到工作空间根目录执行 colcon。

## 依赖

- Ubuntu 24.04
- ROS 2 Jazzy
- CMake、Git、colcon、PCL、Eigen
- 连接 T100 的网卡：192.168.1.20/24
- T100 地址：192.168.1.10

~~~bash
sudo apt update
sudo apt install -y build-essential cmake git python3-colcon-common-extensions libeigen3-dev libpcl-dev
source /opt/ros/jazzy/setup.bash
~~~

配置网卡（以 end0 为例）：

~~~bash
sudo ip link set end0 up
sudo ip addr replace 192.168.1.20/24 dev end0
ping -I end0 -c 2 192.168.1.10
~~~

## 获取源码

~~~bash
git clone --recursive https://github.com/NESccee/LiDAR_Inertial_Odometry.git ~/T100_ws/bsp
cd ~/T100_ws/bsp
git checkout t100fastlio
git submodule update --init --depth 1
~~~

## 编译 Livox SDK2

~~~bash
cd ~/T100_ws/bsp/livox-sdk2
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 1
sudo cmake --install build
sudo ldconfig
~~~

## 编译 ROS 2 驱动

驱动使用官方原生 build.sh，不能从驱动包目录外调用 colcon 替代：

~~~bash
cd ~/T100_ws/bsp/livox_ros_driver2/src/livox_ros_driver2
source /opt/ros/jazzy/setup.bash
./build.sh jazzy
~~~

原生脚本会在 ~/T100_ws/bsp/livox_ros_driver2/ 下生成 build、install 和 log。加载驱动环境：

~~~bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
~~~

T100 配置文件：

~~~text
~/T100_ws/bsp/livox_ros_driver2/src/livox_ros_driver2/config/T100_config.json
~~~

T100 使用端口：

~~~text
控制：60000    点云：60001    IMU：60003
~~~

## 编译 FAST-LIO

仅使用一个 CPU 核心，并将构建结果放在 FAST-LIO 目录内：

~~~bash
cd ~/T100_ws/bsp/fast_lio
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash

taskset -c 0 env MAKEFLAGS=-j1 CMAKE_BUILD_PARALLEL_LEVEL=1 colcon --log-base .colcon_log build --base-paths . --build-base .colcon_build --install-base .colcon_install --executor sequential --parallel-workers 1 --packages-select fast_lio --cmake-args -DCMAKE_BUILD_TYPE=Release
source .colcon_install/setup.bash
~~~

## 启动 T100 驱动

终端 1：

~~~bash
cd ~/T100_ws/bsp/livox_ros_driver2/src/livox_ros_driver2
source /opt/ros/jazzy/setup.bash
source ../../install/setup.bash
ros2 launch livox_ros_driver2 msg_T100_launch.py
~~~

该启动文件会先向 T100 的 UDP 60000 端口发送兼容的 SAMPLING 命令，然后启动驱动。驱动发布：

~~~text
/livox/lidar
/livox/imu
~~~

## 启动 FAST-LIO

终端 2：

~~~bash
cd ~/T100_ws/bsp/fast_lio
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
source .colcon_install/setup.bash

ros2 launch ~/T100_ws/bsp/fast_lio/launch/mapping.launch.py config_path:=~/T100_ws/bsp/fast_lio/config config_file:=t100.yaml rviz:=true
~~~

如不需要 RViz，将 rviz:=true 改为 rviz:=false。

## 查看数据

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
source ~/T100_ws/bsp/fast_lio/.colcon_install/setup.bash

ros2 topic hz /livox/lidar
ros2 topic hz /livox/imu
ros2 topic hz /Odometry
ros2 topic echo /Odometry --field pose.pose.position
~~~

FAST-LIO 点云话题：

~~~text
/cloud_registered
/cloud_registered_body
~~~

位置和姿态可通过 TF 查看：

~~~bash
ros2 run tf2_ros tf2_echo camera_init body
~~~

## 停止

~~~bash
pkill -INT -x fastlio_mapping
pkill -INT -x livox_ros_driver2_node
~~~

各组件的许可证和上游版权声明保留在对应目录。
