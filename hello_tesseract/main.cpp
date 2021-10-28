#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <string>
#include <vector>

using namespace std;
using namespace cv;

static const char* FILENAME = "/home/fvbakel/Documenten/nonogram/pictures/puzzle-30-nonogram.png";
//static const char* FILENAME = "/home/fvbakel/Documenten/nonogram/pictures/one-vert.png";

class Grid {
    public:
        int m_x_size = 0;
        int m_y_size = 0;
        int m_x_line_thickness = 0;
        int m_y_line_thickness = 0;
};

void detect_grid_1() {
    string outText;
    string imPath = FILENAME;
    Mat im = cv::imread(imPath, IMREAD_GRAYSCALE);

    Mat blured;
    cv::blur(im,blured,im.size());
    cv::imshow("blur", blured);
    waitKey(0);
}

void detect() {
 /*           //m_ocr->SetPageSegMode(tesseract::PSM_SINGLE_LINE);
            std::vector<std::vector<cv::Point> > contours;
            //Blur the image with Gaussian kernel
            cv::Mat image_blurred;
            cv::Mat thresh;
            cv::GaussianBlur(subset, image_blurred, cv::Size(9, 9), 0);
            cv::adaptiveThreshold(image_blurred,thresh,255,cv::ADAPTIVE_THRESH_GAUSSIAN_C,cv::THRESH_BINARY_INV,11,30);
            cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT,cv::Size(17, 17));
            cv::Mat diltated;
            cv::dilate(thresh,diltated,kernel,cv::Point(-1,-1),4);
            cv::imshow("Test", diltated);
            cv::waitKey(0);
            cv::findContours(diltated,contours,cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
            std::cout << "Found contours: " << contours.size() << "\n";
            for (size_t idx = 0; idx < contours.size(); idx++) {
                cv::drawContours(image_blurred, contours, idx, cv::Scalar(0, 0, 0));
            }
            */
}

void hello_opencv_1() {
    string outText;
    string imPath = FILENAME;
    Mat im = cv::imread(imPath, IMREAD_GRAYSCALE);

    tesseract::TessBaseAPI *ocr = new tesseract::TessBaseAPI();
    // Initialize tesseract-ocr with English, without specifying tessdata path
   // if (ocr->Init(NULL, "eng",tesseract::OEM_LSTM_ONLY)) {
    if (ocr->Init(NULL, "eng")) {
        cerr << "Could not initialize tesseract.\n";
        exit(1);
    }

    cout << "Size: " << im.cols << "," << im.rows << "\n";
    //ocr->SetVariable("user_defined_dpi", "70"); 
    //ocr->SetPageSegMode(tesseract::PSM_AUTO);
    ocr->SetVariable("tessedit_char_blacklist", ".,!?@#$%&*()<>_-+=/:;'\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz");
    ocr->SetVariable("tessedit_char_whitelist", "0123456789");
    ocr->SetVariable("classify_bln_numeric_mode", "1");

    cv::Rect rect(202, 0, 25, 167);
    //cv::Rect rect(202, 140, 26, 26);
    //cv::rectangle(im, rect, cv::Scalar(0, 255, 0));
    cv::Mat subset = im(rect);
   /* cv::imshow("Test", subset);
    waitKey(0);
*/
    ocr->SetImage(subset.data, subset.cols, subset.rows, subset.channels() , subset.step);
    // Get OCR result
    outText = string(ocr->GetUTF8Text());
    cout << outText << "\n";

    // Destroy used object and release memory
    ocr->End();
    delete ocr;
}

void hello_2()
{
    char *outText;

    tesseract::TessBaseAPI *api = new tesseract::TessBaseAPI();
    // Initialize tesseract-ocr with English, without specifying tessdata path
    if (api->Init(NULL, "eng")) {
        fprintf(stderr, "Could not initialize tesseract.\n");
        exit(1);
    }

    // Open input image with leptonica library
    Pix *image = pixRead(FILENAME);
    api->SetImage(image);
    // Restrict recognition to a sub-rectangle of the image
    // SetRectangle(left, top, width, height)
    api->SetRectangle(30, 86, 590, 100);
    // Get OCR result
    outText = api->GetUTF8Text();
    printf("OCR output:\n%s", outText);

    // Destroy used object and release memory
    api->End();
    delete api;
    delete [] outText;
    pixDestroy(&image);

}

void hello_3()
{
    char *outText;

    tesseract::TessBaseAPI *api = new tesseract::TessBaseAPI();
    // Initialize tesseract-ocr with English, without specifying tessdata path
    if (api->Init(NULL, "eng")) {
        fprintf(stderr, "Could not initialize tesseract.\n");
        exit(1);
    }

    // Open input image with leptonica library
    Pix *image = pixRead(FILENAME);
    api->SetImage(image);

    l_uint32  value     =0;
    int width = pixGetWidth(image);
    int height = pixGetHeight(image);
    int offset = 20;
    l_int32 x = offset;
    l_int32 y = offset;
    std::vector<l_int32> x_lines;
    std::vector<l_int32> y_lines;
    for (x = offset;x<width;x++) {
        pixGetPixel( image, x,y,&value );
        if (value == 0) {
            x_lines.push_back(x);
        }
    }

    x = offset;
    y = offset;
    for (y = offset;y<height;y++) {
        pixGetPixel( image, x,y,&value );
        if (value == 0) {
            y_lines.push_back(x);
        }
    }
    
    // Restrict recognition to a sub-rectangle of the image
    // SetRectangle(left, top, width, height)
   // api->SetRectangle(x_lines[0], y_lines[0], (x_lines[1] - x_lines[0]) , (y_lines[1] - y_lines[0]));
    api->SetRectangle(202, 0, 28, 170);
    // Get OCR result
    outText = api->GetUTF8Text();
    printf("OCR output:\n%s", outText);

    // Destroy used object and release memory
    api->End();
    delete api;
    delete [] outText;
    pixDestroy(&image);

}

void hello_boxes() {
    char *outText;
    tesseract::TessBaseAPI *api = new tesseract::TessBaseAPI();
    // Initialize tesseract-ocr with English, without specifying tessdata path
    if (api->Init(NULL, "eng")) {
        fprintf(stderr, "Could not initialize tesseract.\n");
        exit(1);
    }
    Pix *image = pixRead(FILENAME);
    api->SetImage(image);
    Boxa* boxes = api->GetComponentImages(tesseract::RIL_TEXTLINE, true, NULL, NULL);
    printf("Found %d textline image components.\n", boxes->n);
    for (int i = 0; i < boxes->n; i++) {
    BOX* box = boxaGetBox(boxes, i, L_CLONE);
    api->SetRectangle(box->x, box->y, box->w, box->h);
    char* ocrResult = api->GetUTF8Text();
    int conf = api->MeanTextConf();
    fprintf(stdout, "Box[%d]: x=%d, y=%d, w=%d, h=%d, confidence: %d, text: %s",
                    i, box->x, box->y, box->w, box->h, conf, ocrResult);
    boxDestroy(&box);
    }
    // Destroy used object and release memory
    api->End();
    delete api;
    delete [] outText;
    pixDestroy(&image);
}

int main()
{
    // hello_1();
    // hello_2();
    // hello_boxes();
    // hello_3();
    hello_opencv_1();
    detect_grid_1();
}