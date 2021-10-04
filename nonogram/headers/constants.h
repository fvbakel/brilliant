#ifndef _CONSTANTS_H
#define _CONSTANTS_H	1

#include <limits>

enum color {no_color,black,white};
enum direction {x_dir,y_dir};
enum file_type {txt_file,non_file};
enum non_parse_state {searching,parsing_rows,parsing_cols};

const int SIZE_UNKNOWN = -1;

const int POS_UNKNOWN = -1;
const int POS_NA = -2;

constexpr int MAX_VARIATION =  std::numeric_limits<int>::max();

#endif /* <constants.h> included.  */