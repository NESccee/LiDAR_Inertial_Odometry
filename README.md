# T100 Livox ROS 2 FAST-LIO

本仓库包含 DJI T100 定制激光雷达所需的 Livox SDK2、ROS 2 驱动和 FAST-LIO ROS 2。
默认环境为 Ubuntu 24.04、ROS 2 Jazzy，主机网卡连接 T100 后使用 `192.168.1.20/24`，雷达地址为 `192.168.1.10`。

## 项目组成声明

本项目明确使用以下三个开源组件：

- **Livox SDK2**：负责 Livox/T100 雷达底层设备通信和数据协议处理，目录为 `livox-sdk2/`。
- **livox_ros_driver2**：负责将 T100 点云和 IMU 数据接入 ROS 2，并发送 T100 专用 `SAMPLING` 控制命令，目录为 `livox_ros_driver2/`。
- **FAST-LIO ROS 2**：负责融合点云与 IMU，输出实时里程计和地图，目录为 `fast_lio/`。

三个组件在本项目中组合使用：T100 通过 `livox_ros_driver2` 发布 `/livox/lidar` 和 `/livox/imu`，FAST-LIO 订阅这两个话题进行激光惯性里程计计算。各组件的许可证和上游版权声明保留在对应目录及文件中。

## 目录

```text
livox-sdk2/       Livox SDK2
livox_ros_driver2/ ROS 2 驱动及 T100 配置
fast_lio/         FAST-LIO ROS 2 及 t100.yaml
```

## 依赖

```bash
sudo apt update
sudo apt install -y build-essential cmake git python3 python3-colcon-common-extensions \
  libeigen3-dev libpcl-dev
```

安装 ROS 2 Jazzy 后加载环境：

```bash
source /opt/ros/jazzy/setup.bash
cd ~/T100_ws
```

## 编译 SDK2

```bash
cd ~/T100_ws/livox-sdk2
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 1
sudo cmake --install build
sudo ldconfig
```

## 编译 ROS 2 驱动

```bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
colcon build --executor sequential --parallel-workers 1 \
  --packages-select livox_ros_driver2 \
  --cmake-args -DROS_EDITION=ROS2 -DDISTRO_ROS=jazzy
source install/setup.bash
```

驱动配置为 `livox_ros_driver2/config/T100_config.json`，并使用 T100 专用 UDP 端口：

```text
控制 60000，点云 60001，IMU 60003
```

## 编译 FAST-LIO

首次获取源码时还需要初始化 `ikd-Tree` 子模块：

```bash
cd ~/T100_ws/fast_lio
git submodule update --init --depth 1
```

ROS 2 Jazzy 需要 C++17。为避免设备卡死，编译固定使用一个 CPU 核心：

```bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
taskset -c 0 env MAKEFLAGS=-j1 CMAKE_BUILD_PARALLEL_LEVEL=1 \
  colcon build --executor sequential --parallel-workers 1 \
  --packages-select fast_lio \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

## 配置网卡

将连接雷达的网卡配置为 `192.168.1.20/24`。例如网卡名为 `end0`：

```bash
sudo ip link set end0 up
sudo ip addr replace 192.168.1.20/24 dev end0
ping -I end0 -c 2 192.168.1.10
```

## 启动 T100 驱动

终端 1：

```bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch livox_ros_driver2 msg_T100_launch.py
```

该 launch 会自动向 `192.168.1.10:60000` 发送 T100 兼容的 `SAMPLING` 命令，然后启动驱动。驱动发布：

```text
/livox/lidar   livox_ros_driver2/msg/CustomMsg
/livox/imu     sensor_msgs/msg/Imu
```

## 启动 FAST-LIO

终端 2：

```bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch fast_lio mapping.launch.py config_file:=t100.yaml rviz:=true
```

T100 配置文件为 `fast_lio/config/t100.yaml`，使用四线 Livox 点云、10 Hz 扫描和 `/livox/lidar`、`/livox/imu` 话题。

## 查看坐标和状态

终端 3 只查看位姿坐标：

```bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /Odometry --field pose.pose.position
```

查看频率：

```bash
ros2 topic hz /livox/lidar
ros2 topic hz /livox/imu
ros2 topic hz /Odometry
```

`/cloud_registered` 是世界坐标系点云；`/cloud_registered_body` 是雷达机体坐标系点云。

## 停止程序

优先在各自 launch 终端按 `Ctrl+C`。也可以执行：

```bash
pkill -INT -x fastlio_mapping
pkill -INT -x livox_ros_driver2_node
```

确认没有重复启动的节点：

```bash
pgrep -a -f 'fastlio_mapping|livox_ros_driver2_node|ros2 launch'
```
