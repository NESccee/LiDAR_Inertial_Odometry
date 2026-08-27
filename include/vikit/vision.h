#pragma once
#include <opencv2/opencv.hpp>
#include <algorithm>
namespace vk {
inline void halfSample(const cv::Mat &src, cv::Mat &dst) { cv::pyrDown(src, dst); }
inline double interpolateMat_8u(const cv::Mat &img, double x, double y) {
  if (img.empty() || x < 0 || y < 0 || x >= img.cols - 1 || y >= img.rows - 1) return 0.0;
  return img.at<unsigned char>(static_cast<int>(y), static_cast<int>(x));
}
inline double shiTomasiScore(const cv::Mat &img, int x, int y) {
  if (x < 1 || y < 1 || x >= img.cols - 1 || y >= img.rows - 1) return 0.0;
  cv::Mat patch = img(cv::Rect(x-1,y-1,3,3)); cv::Mat eig;
  cv::cornerMinEigenVal(patch, eig, 2); return eig.at<float>(1,1);
}
}
