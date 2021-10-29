#include "cppflow/ops.h"
#include "cppflow/model.h"

#include <opencv2/opencv.hpp>
#include <algorithm>
#include <iterator>
#include <chrono>
#include <ctime> 
#include <iostream>

using namespace cv;
using namespace cppflow;

int main() {
    // Used variables
    const int IMG_SIZE = 25;
    std::vector<float> img_data(IMG_SIZE*IMG_SIZE*3);
    Mat image, preprocessed_image, flat;
   // std::vector<float> predictions;
    std::string text;

    // Initialize neural network
    std::cout<<"Current tensorflow version: "<< TF_Version() << std::endl;
    cppflow::model model("/home/fvbakel/git/brilliant/hello_keras_img/model_1");

    // Input and output Tensors
  //  tensor input(m, "serving_default_input_layer");
  //  tensor prediction(m, "StatefulPartitionedCall");
    
    // Read image and convert to float
    image = cv::imread("/home/fvbakel/Documenten/nonogram/digits-data/Validation/8/F_5_471.png");
    image.convertTo(image, CV_32F, 1.0/255.0);

    // Image dimensions    
    int rows = image.rows;
    int cols = image.cols;
    int channels = image.channels();
    int total = image.total();

    // Assign to vector for 3 channel image
    // Souce: https://stackoverflow.com/a/56600115/2076973
    flat = image.reshape(1, image.total() * channels);
    img_data = image.isContinuous()? flat : flat.clone(); 

    // Feed data to input tensor
    tensor input = tensor(img_data, {1, rows, cols, channels});
        
    // Get tensor with predictions
    auto predictions = model(input);
    std::cout << "It's a " << cppflow::arg_max(predictions, 1) << std::endl;
    return 0;
}