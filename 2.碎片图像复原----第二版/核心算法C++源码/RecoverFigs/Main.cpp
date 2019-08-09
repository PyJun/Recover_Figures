#include "header.h"

Matcher matchers[SIZE][SIZE];
vector<vector<vector<Point>>> contours_vec;

// 命令行调用的格式: 
// RecoverFigs.exe inDir outFile
// inDir 为碎片图像的目录， outFile 为输出图像的路径
int main(int argc, const char * argv[]) {
	double t1 = (double)getTickCount();
	const string dir = ((argc > 1) ? argv[1] : DIR) + "/";
	vector<Mat> img_vec = getImgVec(getNums(9), dir);
	Mat recImg;
	if (recoverImg(recImg, img_vec)) { 
		resize(recImg, recImg, Size(600, 600));
		double t2 = (double)getTickCount();
		cout << "耗时: " << (t2 - t1) / (getTickFrequency()) << " 秒" << endl;
		if (argc <= 1) {
			imshow("recoverImg", recImg);
			waitKey(0);
		}
		if (argc > 2) {
			imwrite(string(argv[2]), recImg);
		} else {
			imwrite(dir + string("recoverImg.jpg"), recImg);
		}
		return 0;
	} else {
		//cout << "无法拼接!" << endl;
		return -1;
	}
}


//int main() {
//	vector<Mat> img_vec = getImgVec(getNums(9));
//	int size = (int)img_vec.size();
//	initMatchers(img_vec);
//	vector<pair<int,int>> pair_nums;
//	double tolMatch = imgPrime(pair_nums, size);
//	cout << tolMatch << endl;
//	for (auto pr : pair_nums) {
//		cout << pr.first << " " << pr.second << endl;
//	}
//	cout << endl;
//	system("pause");
//	return 0;
//}



//// 这是二图拼接的主函数
//int main(int argc, const char * argv[]) {
//	vector<Mat> img_vec = getImgVec({ 1, 2, 3, 4, 5, 6, 7, 8, 9 });
//	int size = img_vec.size();
//	initMatchers(img_vec);
//	set<int> jointedIds;
//	Mat dstImg = img_vec[0];
//	dstImg = jointTwo(dstImg, img_vec[1], { 0, 1}, jointedIds, size);
//	dstImg = jointTwo(dstImg, img_vec[2], { 1, 2 }, jointedIds, size);
//	dstImg = jointTwo(dstImg, img_vec[3], { 0, 3 }, jointedIds, size);
//	imshow("Merged Img", dstImg);
//	waitKey(0);
//	return 0;
//}

