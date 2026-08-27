#pragma once
#include <cmath>
namespace vk { inline double huberWeight(double e,double t){return std::abs(e)<=t?1.0:t/std::abs(e);} }
