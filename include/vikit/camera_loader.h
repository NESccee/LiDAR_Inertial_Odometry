#pragma once
#include "pinhole_camera.h"
#include <rclcpp/rclcpp.hpp>
namespace vk { namespace camera_loader { inline bool loadFromRosNs(const std::string&, AbstractCamera*&cam){ cam=new PinholeCamera(640,480,320,320,320,240); return true; } } }
