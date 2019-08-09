#include "header.h"

// 对一个点坐标 pot 进行旋转
void rotatePoint(const Mat & rot_mat, Point & pot) {
	Mat p(3, 1, CV_64FC1);
	p.at<double>(0, 0) = pot.x;
	p.at<double>(1, 0) = pot.y;
	p.at<double>(2, 0) = 1;
	Mat rot_pot = rot_mat * p;
	pot.x = (int)round(rot_pot.at<double>(0, 0));
	pot.y = (int)round(rot_pot.at<double>(1, 0));
}

Mat rotateImg(const Mat & srcImg, double angle, Point & pot1, Point & pot2, const set<int> & jointedIds, int size) {
	Mat dstImg(srcImg.size(), srcImg.type(), Scalar::all(255));
	Point2f center((float)dstImg.cols / 2, (float)dstImg.rows / 2);
	Mat rot_mat = getRotationMatrix2D(center, angle, 1);
	warpAffine(srcImg, dstImg, rot_mat, Size(dstImg.cols, dstImg.rows), INTER_LINEAR, BORDER_CONSTANT, Scalar::all(255));
	rotatePoint(rot_mat, pot1);
	rotatePoint(rot_mat, pot2);
	for (auto id1 : jointedIds) {
		for (int id2 = 0; id2 < size; id2++) {
			if (id1 == id2) continue;
			rotatePoint(rot_mat, matchers[id1][id2].first_p);
			rotatePoint(rot_mat, matchers[id1][id2].last_p);
		}
	}
	return dstImg;
}

void movePoint(double x, double y, Point & pot) {
	pot.x = pot.x + (int)round(x);
	pot.y = pot.y + (int)round(y);
}


// 对一个图像进行平移
Mat moveImg(const Mat & srcImg, double x, double y, Point & pot1, Point & pot2, const set<int> & jointedIds, int size) {
	Mat dstImg;
	Mat mv_mat = Mat::zeros(2, 3, CV_64FC1);
	mv_mat.at<double>(0, 0) = 1;
	mv_mat.at<double>(0, 2) = x; //水平平移量
	mv_mat.at<double>(1, 1) = 1;
	mv_mat.at<double>(1, 2) = y; //竖直平移量
	warpAffine(srcImg, dstImg, mv_mat, srcImg.size(), INTER_LINEAR, BORDER_CONSTANT, Scalar::all(255));
	movePoint(x, y, pot1);
	movePoint(x, y, pot2);
	for (auto id1 : jointedIds) {
		for (int id2 = 0; id2 < size; id2++) {
			if (id1 == id2) continue;
			movePoint(x, y, matchers[id1][id2].first_p);
			movePoint(x, y, matchers[id1][id2].last_p);
		}
	}
	return dstImg;
}
