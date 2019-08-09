#include "header.h"

inline string getImgPath(int i, const string dir) {
	return dir + to_string(i) + string(".png");
}

vector<int> getNums(int n) {
	vector<int> nums;
	for (int i = 1; i <= n; i++) {
		nums.push_back(i);
	}
	return nums;
}

vector<Mat> getImgVec(const vector<int> & nums, const string dir) {
	vector<Mat> img_vec;
	for (auto num : nums) {
		string img_path = getImgPath(num, dir);
		Mat srcImg = imread(img_path, IMREAD_COLOR);
		if (!srcImg.empty()) {
			img_vec.push_back(srcImg);
		}
	}
	return img_vec;
}

vector<Mat> getGrayimgVec(const vector<Mat> & img_vec) {
	vector<Mat> grayImg_vec;
	for (auto img : img_vec) {
		Mat grayImg;
		cvtColor(img, grayImg, COLOR_BGR2GRAY);
		grayImg_vec.push_back(grayImg);
	}
	return grayImg_vec;
}

void initContoursVec(const vector<Mat> & grayImg_vec) {
	contours_vec.clear();
	for (auto grayImg : grayImg_vec) {
		Mat binImg = preSolveImg(grayImg);
		vector<vector<Point>> contours;
		extractContours(binImg, contours);
		contours_vec.push_back(contours);
	}
}

void initMatchers(const vector<Mat> & img_vec) {
	vector<Mat> grayImg_vec = getGrayimgVec(img_vec);
	initContoursVec(grayImg_vec);
	int size = (int)grayImg_vec.size();
	vector<pair<Point, Point>> pot_vec;
	Point first_p1, last_p1, first_p2, last_p2;
	for (int i = 0; i < size; i++) {
		for (int j = 0; j < i && j < size; j++) {
			double match = matchImg(pot_vec, contours_vec[i], contours_vec[j], grayImg_vec[i], grayImg_vec[j]);
			if (match > 0) {
				first_p1 = pot_vec[0].first;
				last_p1 = pot_vec[1].first;
				first_p2 = pot_vec[0].second;
				last_p2 = pot_vec[1].second;
			}
			matchers[i][j] = Matcher(first_p1, last_p1, match);
			matchers[j][i] = Matcher(first_p2, last_p2, match);
		}
	}
}

