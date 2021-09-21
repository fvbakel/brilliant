#include <VarianceCalculator.h>
#include <sstream>
#include <iostream>

VarianceCalculator::VarianceCalculator() {
    return;
}

VarianceCalculator* VarianceCalculator::getCalculator() {
    static VarianceCalculator       *the_instance;
    if (the_instance == nullptr) {
        the_instance = new VarianceCalculator();
    }
    return the_instance;
}

std::string VarianceCalculator::make_key(int nr_of_segments,int nr_of_white_space) {
    std::ostringstream oss;
    oss << nr_of_segments << "_" << nr_of_white_space;
    return oss.str();
}

int VarianceCalculator::get_variance(int nr_of_segments,int nr_of_white_space) {
    std::string key = make_key(nr_of_segments,nr_of_white_space);
    if (m_cache.find(key) == m_cache.end()) {
        int value = 1;
        if (nr_of_segments == 1 ) {
            value = 1;
        } else if (nr_of_white_space == 0) {
            value= 1;
        } else {
            value =  get_variance(nr_of_segments,nr_of_white_space - 1) +\
                     get_variance(nr_of_segments -1 ,nr_of_white_space);
        }
        m_cache[key] = value;
    }
    return m_cache[key];

}

