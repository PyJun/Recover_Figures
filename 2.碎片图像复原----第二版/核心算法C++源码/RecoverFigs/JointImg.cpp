#include "header.h"

// imgId1 大块， imgId2 是小块
Mat jointTwo(Mat srcImg1, Mat srcImg2, pair<int,int> pair_id, set<int> & jointedIds, int size) {
	int imgId1 = pair_id.first, imgId2 = pair_id.second;
	Point first_p1 = matchers[imgId1][imgId2].first_p;
	Point last_p1 = matchers[imgId1][imgId2].last_p;
	Point first_p2 = matchers[imgId2][imgId1].first_p;
	Point last_p2 = matchers[imgId2][imgId1].last_p;
	// 分别得到 p1，p2 直线的倾斜角
	double theta1 = lineDirection(first_p1, last_p1);
	double theta2 = lineDirection(first_p2, last_p2);
	double rot_th1 = (imgId1 > imgId2) ? 90 - theta1 : -90 - theta1;
	double rot_th2 = (imgId1 > imgId2) ? 90 - theta2 : -90 - theta2;
	// 将 srcImg 图像旋转至可以水平拼接
	jointedIds.insert(imgId1);
	Mat dstImg1 = rotateImg(srcImg1, rot_th1, first_p1, last_p1, jointedIds, size);
	Mat dstImg2 = rotateImg(srcImg2, rot_th2, first_p2, last_p2, set<int>{imgId2}, size);
	int com_rows = max(dstImg1.rows, dstImg2.rows), com_cols = dstImg1.cols + dstImg2.cols;
	Mat comImg1(com_rows, com_cols, CV_8UC3, Scalar::all(255)), comImg2(com_rows, com_cols, CV_8UC3, Scalar::all(255));
	// 水平扩展矩阵，得到二个宽度更长的 Mat 对象，以便填充图像不会溢出
	dstImg1.copyTo(comImg1(Range(0, dstImg1.rows), Range(0, dstImg1.cols)));
	dstImg2.copyTo(comImg2(Range(0, dstImg2.rows), Range(0, dstImg2.cols)));
	//imshow("dstImg1", comImg1);
	//imshow("dstImg2", comImg2);

	//hconcat(dstImg1, Mat(dstImg2.size(), dstImg2.type(), Scalar(255, 255, 255)), comImg1);
	//hconcat(Mat(dstImg1.size(), dstImg1.type(), Scalar(255, 255, 255)), dstImg2, comImg2);
	// 计算图片1平移至图片2水平拼接时所需的位移量， 并平移
	double mv_x = ((first_p2.x - first_p1.x) + (last_p2.x - last_p1.x)) / 2;
	double mv_y = ((first_p2.y - first_p1.y) + (last_p2.y - last_p1.y)) / 2;
	comImg2 = moveImg(comImg2, -mv_x, -mv_y, first_p2, last_p2, set<int>{imgId2}, size);
	// 得到掩码矩阵，并将 comImg1 拷贝至 comImg 得到最终拼接后的图像
	Mat mask = preSolveImg(comImg2);
	comImg2.copyTo(comImg1, mask);
	vector<Rect> rect_vec = detectTarget(comImg1);
	if (rect_vec.empty()) {
		//cerr << "Error: rect_vec empty!" << endl;
		return Mat();
	}
	// 一般情况下只有一个轮廓
	//imshow("comImg1", comImg1);
	jointedIds.insert(imgId2);
	Mat comImg = normalizeImg(comImg1, rect_vec[0], jointedIds, size);

	//// 测试代码
	//imshow("comImg1", comImg1);
	//imshow("comImg2", comImg2);
	//imshow("mask", mask);
	//imshow("comImg", comImg);
	//waitKey(0);

	return comImg;
}


Mat jointImg(const vector<Mat> & img_vec, const vector<pair<int,int>> & imgPairs) {
	if (img_vec.empty() || imgPairs.empty()) return Mat();
	int size = (int)img_vec.size();
	set<int> jointedIds;
	int num1 = imgPairs[0].first, num2 = imgPairs[0].second;
	Mat dstImg = jointTwo(img_vec[num1], img_vec[num2], imgPairs[0], jointedIds, size);
	for (int i = 1; !dstImg.empty() && i < (int)imgPairs.size(); i++) {
		int imgNum = imgPairs[i].second;
		dstImg = jointTwo(dstImg, img_vec[imgNum], imgPairs[i], jointedIds, size);
	}
	return dstImg;
}
