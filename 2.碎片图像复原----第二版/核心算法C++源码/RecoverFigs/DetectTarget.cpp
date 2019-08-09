#include "header.h"

// 根据原图像返回一个目标区域的矩形
vector<Rect> detectTarget(Mat srcImg) {
	Mat grayImg;
	cvtColor(srcImg, grayImg, COLOR_BGR2GRAY);
	vector<Rect> rect_vec;
	Mat binImg = preSolveImg(grayImg);
	vector<vector<Point>> contours, curves;
	extractContours(binImg, contours);
	approxPoly(curves, contours, 1.0);
	for (auto & contour : curves) {
		int min_x = 0x3f3f3f3f, min_y = 0x3f3f3f3f;
		int max_x = 0, max_y = 0;
		for (auto & pot : contour) {
			min_x = min(min_x, pot.x);
			min_y = min(min_y, pot.y);
			max_x = max(max_x, pot.x);
			max_y = max(max_y, pot.y);
		}
		rect_vec.push_back(Rect(min_x, min_y, max_x - min_x, max_y - min_y));
	}
	return rect_vec;
}

// 通过一个目标边界的矩形来规范化原图像
Mat normalizeImg(Mat srcImg, double rate) {
	if (srcImg.empty()) return Mat();
	vector<Rect> rect_vec = detectTarget(srcImg);
	if (rect_vec.empty()) return Mat();
	Rect rect = rect_vec[0];
	double width = rect.width, height = rect.height;
	int interval_x = (int)ceil((width * rate - width) / 2);
	int interval_y = (int)ceil((height * rate - height) / 2);
	Mat dstImg(rect.height + 2 * interval_y, rect.width + 2 * interval_x, srcImg.type(), Scalar::all(255));
	Mat tgtImg = srcImg(rect);
	tgtImg.copyTo(dstImg(Range(interval_y, interval_y + rect.height), Range(interval_x, interval_x + rect.width)));
	return dstImg;
}

Mat normalizeImg(Mat srcImg, Rect rect, const set<int> & jointedIds, int size) {
	double width = rect.width, height = rect.height;
	double length = sqrt(width * width + height * height);
	int interval_x = (int)ceil((length - width + 32) / 2);
	int interval_y = (int)ceil((length - height + 32) / 2);
	Mat dstImg(rect.height + 2 * interval_y, rect.width + 2 * interval_x, srcImg.type(), Scalar::all(255));
	Mat tgtImg = srcImg(rect);
	tgtImg.copyTo(dstImg(Range(interval_y, interval_y + rect.height), Range(interval_x, interval_x + rect.width)));
	double mv_x = rect.x + (rect.width - dstImg.cols) / 2;
	double mv_y = rect.y + (rect.height - dstImg.cols) / 2;
	for (auto id1 : jointedIds) {
		for (int id2 = 0; id2 < size; id2++) {
			if (id1 == id2) continue;
			movePoint(-mv_x, -mv_y, matchers[id1][id2].first_p);
			movePoint(-mv_x, -mv_y, matchers[id1][id2].last_p);
		}
	}
	return dstImg;
}

