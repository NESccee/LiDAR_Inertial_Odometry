# DJI T100 Livox ROS 2 FAST-LIO

本目录用于在 ROS 2 Jazzy 下使用 DJI T100 360° 激光雷达，并通过 FAST-LIO 输出激光惯性里程计。

项目包含：

- Livox SDK2：雷达底层 SDK
- livox_ros_driver2：ROS 2 驱动和 T100 专用控制命令
- FAST-LIO：点云和 IMU 融合定位

## 目录结构

~~~text
~/T100_ws/bsp/
├── livox-sdk2/
├── livox_ros_driver2/
│   ├── src/livox_ros_driver2/
│   │   ├── build.sh
│   │   ├── config/T100_config.json
│   │   └── launch_ROS2/
│   └── install/
└── fast_lio/
    ├── config/t100.yaml
    ├── launch/mapping.launch.py
    └── .colcon_install/
~~~

T100 网络参数：

~~~text
雷达：192.168.1.10
主机：192.168.1.20/24
控制端口：60000
点云端口：60001
IMU 端口：60003
~~~

## 1. 安装依赖

~~~bash
sudo apt update
sudo apt install -y build-essential cmake git python3-colcon-common-extensions libeigen3-dev libpcl-dev
source /opt/ros/jazzy/setup.bash
~~~

配置连接雷达的网卡，以下以 end0 为例：

~~~bash
sudo ip link set end0 up
sudo ip addr replace 192.168.1.20/24 dev end0
ping -I end0 -c 2 192.168.1.10
~~~

## 2. 编译 Livox SDK2

~~~bash
cd ~/T100_ws/bsp/livox-sdk2
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 1
sudo cmake --install build
sudo ldconfig
~~~

## 3. 编译 livox_ros_driver2

必须从驱动包目录执行原生 build.sh：

~~~bash
cd ~/T100_ws/bsp/livox_ros_driver2/src/livox_ros_driver2
source /opt/ros/jazzy/setup.bash
./build.sh jazzy
~~~

驱动安装目录：

~~~text
~/T100_ws/bsp/livox_ros_driver2/install
~~~

加载驱动环境：

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
~~~

T100 配置文件：

~~~text
~/T100_ws/bsp/livox_ros_driver2/src/livox_ros_driver2/config/T100_config.json
~~~

## 4. 编译 FAST-LIO

FAST-LIO 使用单核编译，构建文件只写入 fast_lio 目录：

~~~bash
cd ~/T100_ws/bsp/fast_lio
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
git submodule update --init --depth 1

taskset -c 0 env MAKEFLAGS=-j1 CMAKE_BUILD_PARALLEL_LEVEL=1 colcon --log-base .colcon_log build --base-paths . --build-base .colcon_build --install-base .colcon_install --executor sequential --parallel-workers 1 --packages-select fast_lio --cmake-args -DCMAKE_BUILD_TYPE=Release
source ~/T100_ws/bsp/fast_lio/.colcon_install/setup.bash
~~~

## 5. 启动 T100 驱动

终端 1：

~~~bash
cd ~/T100_ws/bsp/livox_ros_driver2/src/livox_ros_driver2
source /opt/ros/jazzy/setup.bash
source ../../install/setup.bash
ros2 launch livox_ros_driver2 msg_T100_launch.py
~~~

启动文件会先发送 T100 兼容的 SAMPLING 命令，然后启动驱动。

驱动话题：

~~~text
/livox/lidar
/livox/imu
~~~

## 6. 启动 FAST-LIO

终端 2：

~~~bash
cd ~/T100_ws/bsp/fast_lio
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/bsp/livox_ros_driver2/install/setup.bash
source ~/T100_ws/bsp/fast_lio/.colcon_install/setup.bash

ros2 launch ~/T100_ws/bsp/fast_lio/launch/mapping.launch.py config_path:=~/T100_ws/bsp/fast_lio/config config_file:=t100.yaml rviz:=false
~~~

需要 RViz 时，将 rviz:=false 改为 rviz:=true。

## 7. 查看数据

查看原始点云和 IMU：

~~~bash
ros2 topic hz /livox/lidar
ros2 topic hz /livox/imu
~~~

查看 FAST-LIO 位置：

~~~bash
ros2 topic hz /Odometry
ros2 topic echo /Odometry --field pose.pose.position
~~~

FAST-LIO 点云：

~~~text
/cloud_registered
/cloud_registered_body
~~~

查看位置和姿态 TF：

~~~bash
ros2 run tf2_ros tf2_echo camera_init body
~~~

启动日志出现以下内容表示初始化完成：

~~~text
IMU Initial Done
Initialize the map kdtree
~~~

## 8. 停止程序

优先在启动终端按 Ctrl+C。必要时执行：

~~~bash
pkill -INT -x fastlio_mapping
pkill -INT -x livox_ros_driver2_node
~~~

