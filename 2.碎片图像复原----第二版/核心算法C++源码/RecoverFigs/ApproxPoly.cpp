#include "header.h"

// 对图像进行处理， 包括高斯滤波， canny算子， 形态学闭运算
// 最终得到黑白图像，白色为前景，黑色为背景
Mat preSolveImg(const Mat & srcImg, double c1, double c2, int ksize) {
	Mat tempImg = srcImg.clone(), edges;
	GaussianBlur(tempImg, tempImg, Size(3, 3), 0.1, 0.1);
	Canny(tempImg, edges, c1, c2, 5);
	//imshow("Canny", edges);
	Mat white(tempImg.size(), tempImg.type(), Scalar::all(255));
	tempImg = Mat(tempImg.size(), tempImg.type(), Scalar::all(0));
	white.copyTo(tempImg, edges);
	Mat element1 = getStructuringElement(MORPH_ELLIPSE, Size(ksize, ksize));
	morphologyEx(tempImg, tempImg, MORPH_CLOSE, element1);
	//Mat element2 = getStructuringElement(MORPH_ELLIPSE, Size(17, 17));
	//morphologyEx(tempImg, tempImg, MORPH_OPEN, element2);
	//threshold(tempImg, tempImg, 220, 255, THRESH_BINARY_INV);
	Mat dstImg = tempImg;
	//imshow("dstImg", dstImg);
	return dstImg;
}

// 对黑白的轮廓图提取轮廓坐标
void extractContours(const Mat & srcImg, vector<vector<Point>> & contours) {
	contours.clear();
	vector<Vec4i> hierarchy;
	findContours(srcImg, contours, hierarchy, RETR_CCOMP, CHAIN_APPROX_SIMPLE, Point(0,0));
}

// 从轮廓坐标contours中进行多边形拟合，得到多边形坐标 curves
// minlen 为轮廓的最下长度阈值，epsilon 为多边形拟合的误差
// 可以得到多个多边形轮廓坐标， 所以可用于多碎片的提取
void approxPoly(vector<vector<Point>> & curves, vector<vector<Point>> & contours, double epsilon, int minlen) {
	curves.clear();
	for (auto & vec : contours) {
		if (vec.size() > minlen) {
			vector<Point> tempVec;
			approxPolyDP(vec, tempVec, epsilon, true);
			curves.push_back(tempVec);
		}
	}
}
