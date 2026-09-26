# DJI T100 Livox ROS 2 FAST-LIO

本仓库将 DJI T100 机载 360° 激光雷达接入 ROS 2 Jazzy，并使用 FAST-LIO 进行激光惯性里程计。T100 使用 Livox/Mid-360 兼容的点云和 IMU 数据格式，但控制端口是 DJI 定制协议，因此必须使用仓库内的 T100 配置和启动文件。

## 组件声明

本项目组合使用以下三个开源组件：

- `livox-sdk2/`：Livox SDK2，提供底层雷达通信和数据解析。
- `livox_ros_driver2/`：ROS 2 驱动，发布 T100 点云与 IMU，并发送兼容 T100 的 `SAMPLING` 命令。
- `fast_lio/`：FAST-LIO ROS 2，融合点云和 IMU，发布里程计与地图。

对应数据流为：T100 -> `livox_ros_driver2` -> `/livox/lidar`、`/livox/imu` -> `fast_lio` -> `/Odometry`、`/cloud_registered`。

## 目录结构

```text
livox-sdk2/          Livox SDK2 源码
livox_ros_driver2/   ROS 2 驱动、T100 配置和启动文件
fast_lio/            FAST-LIO ROS 2 源码及 config/t100.yaml
```

## 环境和网络

- Ubuntu 24.04（aarch64 已验证）
- ROS 2 Jazzy
- PCL、Eigen、CMake、Git、Python 3 和 `colcon`
- 雷达地址：`192.168.1.10`
- 主机连接雷达的网卡地址：`192.168.1.20/24`

安装常用依赖：

```bash
sudo apt update
sudo apt install -y build-essential cmake git python3-colcon-common-extensions \
  libeigen3-dev libpcl-dev
```

配置网卡（以下以 `end0` 为例）：

```bash
sudo ip link set end0 up
sudo ip addr replace 192.168.1.20/24 dev end0
ping -I end0 -c 2 192.168.1.10
```

## 编译

以下命令都使用单任务编译，避免设备因并行编译卡死。假设仓库位于 `~/T100_ws`。

### 1. 编译 Livox SDK2

```bash
cd ~/T100_ws/livox-sdk2
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 1
sudo cmake --install build
sudo ldconfig
```

### 2. 编译 ROS 2 驱动

```bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
colcon build --executor sequential --parallel-workers 1 \
  --packages-select livox_ros_driver2 \
  --cmake-args -DROS_EDITION=ROS2 -DDISTRO_ROS=jazzy
source install/setup.bash
```

驱动配置文件为 `livox_ros_driver2/config/T100_config.json`，使用以下 T100 端口：

```text
控制：60000    点云：60001    IMU：60003
```

### 3. 编译 FAST-LIO

首次获取源码时初始化 `ikd-Tree` 子模块：

```bash
cd ~/T100_ws/fast_lio
git submodule update --init --depth 1
```

为避免使用工作空间根目录的构建结果，并将编译限制到 CPU 0，使用 FAST-LIO 目录内的独立目录：

```bash
cd ~/T100_ws/fast_lio
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/livox_ros_driver2/install/setup.bash

taskset -c 0 env MAKEFLAGS=-j1 CMAKE_BUILD_PARALLEL_LEVEL=1 \
colcon --log-base .colcon_log build \
  --base-paths . \
  --build-base .colcon_build \
  --install-base .colcon_install \
  --executor sequential \
  --parallel-workers 1 \
  --packages-select fast_lio \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
source .colcon_install/setup.bash
```

编译输出位于 `fast_lio/.colcon_install`，不会写入其他 ROS 工作空间的 `build`、`install` 或 `log` 目录。若使用其他安装路径，请相应修改后续 `source` 命令。

## 运行

终端 1，启动 T100 驱动。该启动文件会先向 `192.168.1.10:60000` 发送 T100 专用 `SAMPLING` 命令，再启动驱动：

```bash
cd ~/T100_ws
source /opt/ros/jazzy/setup.bash
source livox_ros_driver2/install/setup.bash
ros2 launch livox_ros_driver2 msg_T100_launch.py
```

终端 2，启动 FAST-LIO（不启动 RViz 时将 `rviz` 设为 `false`）：

```bash
cd ~/T100_ws/fast_lio
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/livox_ros_driver2/install/setup.bash
source .colcon_install/setup.bash
ros2 launch ~/T100_ws/fast_lio/launch/mapping.launch.py \
  config_path:=~/T100_ws/fast_lio/config \
  config_file:=t100.yaml \
  rviz:=true
```

## 验证数据

```bash
source /opt/ros/jazzy/setup.bash
source ~/T100_ws/livox_ros_driver2/install/setup.bash
source ~/T100_ws/fast_lio/.colcon_install/setup.bash

ros2 topic hz /livox/lidar
ros2 topic hz /livox/imu
ros2 topic hz /Odometry
ros2 topic echo /Odometry --field pose.pose.position
```

正常运行时，T100 驱动发布 `/livox/lidar` 和 `/livox/imu`，FAST-LIO 发布 `/Odometry`、`/cloud_registered` 与 `/cloud_registered_body`。看到 `IMU Initial Done` 和 `Initialize the map kdtree` 表示 FAST-LIO 已完成初始化。

## 停止程序

优先在两个启动终端按 `Ctrl+C`。必要时可停止当前用户的节点：

```bash
pkill -INT -x fastlio_mapping
pkill -INT -x livox_ros_driver2_node
```

## 许可证和上游

各组件的许可证、版权声明和上游说明保留在对应目录中。Livox SDK2 和 ROS 2 驱动基于 Livox 官方项目，FAST-LIO 基于 FAST-LIO ROS 2 项目并包含 `ikd-Tree` 子模块。

