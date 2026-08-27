# FAST-LIVO2 ROS 2

FAST-LIVO2 is a fast, direct LiDAR-inertial-visual odometry and mapping system. This repository is the ROS 2 port of the original ROS 1 package. Estimation and mapping algorithms are preserved; ROS communication, parameters, build files, and launch files use ROS 2 APIs.

## Requirements

Supported ROS 2 distributions are Foxy, Humble, and Jazzy. The recommended combinations are Ubuntu 20.04 + Foxy, Ubuntu 22.04 + Humble, and Ubuntu 24.04 + Jazzy. The code uses standard `rclcpp`, message, TF2, and `ament_cmake` APIs shared by these distributions.

```bash
sudo apt install ros-humble-desktop ros-humble-cv-bridge \
  ros-humble-image-transport ros-humble-pcl-conversions \
  ros-humble-tf2-ros ros-humble-visualization-msgs
```

Also install Eigen >= 3.3.4, PCL >= 1.8, OpenCV >= 4.2, Sophus (double/non-templated), and `livox_ros_driver2`. The required Vikit headers are included in this source tree. ROS 1 is not required.

## Build

```bash
source /opt/ros/humble/setup.bash
cd ~/FAST-LIVO2_ros2
colcon build --symlink-install
source install/setup.bash
```

For Foxy or Jazzy, source the matching distribution instead:

```bash
source /opt/ros/foxy/setup.bash    # Ubuntu 20.04
# or
source /opt/ros/jazzy/setup.bash   # Ubuntu 24.04
```

The executable is `fastlivo_mapping` in package `fast_livo2`.

## Run

```bash
ros2 launch fast_livo2 mapping_avia.launch.py
ros2 launch fast_livo2 mapping_avia_marslvig.launch.py
ros2 launch fast_livo2 mapping_hesaixt32_hilti22.launch.py
ros2 launch fast_livo2 mapping_ouster_ntu.launch.py
```

Disable RViz with `rviz:=false`. Play a ROS 2 bag in another terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/FAST-LIVO2_ros2/install/setup.bash
ros2 bag play /path/to/your_bag
```

Launch files load the selected mapping and camera YAML files as node parameters. Topic names and algorithm parameters can be overridden with a ROS 2 parameter file.

## ROS 1 to ROS 2 differences

| Area | ROS 1 (`FAST-LIVO2`) | ROS 2 (`FAST-LIVO2_ros2`) |
|---|---|---|
| Build | `catkin_make` | `colcon build` with `ament_cmake` |
| Package | `fast_livo` | `fast_livo2` |
| Node API | `roscpp`, `ros::NodeHandle` | `rclcpp`, `rclcpp::Node` |
| Messages | `sensor_msgs::Imu` | `sensor_msgs::msg::Imu` |
| Time/callbacks | `ros::Time`, `ConstPtr` | `rclcpp::Time`, shared pointers |
| Parameters | rosparam / `nh.param` | `declare_parameter` / `get_parameter` |
| TF | `tf` | `tf2` / `tf2_ros` |
| Livox | `livox_ros_driver` | `livox_ros_driver2` |
| Launch | XML `.launch` | Python `.launch.py` |

Visual-inertial estimation, LiDAR preprocessing, IMU propagation, and voxel mapping remain functionally aligned with ROS 1. Additional ROS 2 lines are middleware adaptation code, not new algorithm modules.

## Known limitations

- ROS 2 launch uses `rviz2`; ROS 1 XML launch files are not supported.
- Livox topics must use the ROS 2 `livox_ros_driver2` `CustomMsg` definition.
- OpenCV minor-version linker warnings may occur with `cv_bridge`; matching versions is recommended.

## References and license

- [FAST-LIVO2 paper](https://arxiv.org/pdf/2408.14035)
- [Original ROS 1 repository](https://github.com/hku-mars/FAST-LIVO2)
- [FAST-LIVO2 dataset](https://github.com/xuankuzcr/Global-LVBA)
- [FAST-Calib](https://github.com/hku-mars/FAST-Calib)

## Acknowledgements

- [NESccee](https://github.com/NESccee)
- [LiDAR_Inertial_Odometry](https://github.com/NESccee/LiDAR_Inertial_Odometry)

GPLv2. Contact the FAST-LIVO2 authors for commercial licensing.

## 中文说明

FAST-LIVO2 ROS 2 是 FAST-LIVO2 的 ROS 2 移植版本。激光雷达、IMU、相机融合算法与 ROS 1 版本保持一致，改动主要集中在节点、消息、参数、TF、构建系统和启动文件。项目不再依赖 ROS 1 或 catkin。

### 支持环境

支持 ROS 2 Foxy、Humble 和 Jazzy，推荐环境如下：

| ROS 2 | Ubuntu | 建议 |
|---|---|---|
| Foxy | 20.04 | 支持 |
| Humble | 22.04 | 推荐 |
| Jazzy | 24.04 | 支持 |

三种发行版均使用相同的 `rclcpp`、`sensor_msgs`、`nav_msgs`、`tf2` 和 `ament_cmake` 接口。请先安装对应发行版的桌面组件、`cv_bridge`、`image_transport`、`pcl_conversions`、`tf2_ros`、`visualization_msgs`，以及 ROS 2 版 `livox_ros_driver2`。

### 编译与运行

```bash
source /opt/ros/<发行版>/setup.bash
cd ~/FAST-LIVO2_ros2
colcon build --symlink-install
source install/setup.bash
ros2 launch fast_livo2 mapping_avia.launch.py
```

将 `<发行版>` 替换为 `foxy`、`humble` 或 `jazzy`。其他数据集启动文件见上文。参数和话题可通过 YAML 参数文件或 `ros2 param` 覆盖。

### 注意事项

- 必须使用 `livox_ros_driver2` 发布的 ROS 2 `CustomMsg`，不能使用 ROS 1 消息头。
- 启动文件为 Python 格式 `.launch.py`，使用 `rviz2`，原 ROS 1 XML 启动文件不适用于 ROS 2。
- 若 `cv_bridge` 与系统 OpenCV 小版本不同，链接阶段可能出现警告；建议统一 OpenCV 版本。
