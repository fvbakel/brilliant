#ifndef _VARIANCECALCULATOR_H
#define _VARIANCECALCULATOR_H	1

#include <unordered_map>
#include <string>

class VarianceCalculator {
    //protected:
        //static VarianceCalculator       *the_instance;

    private:

        std::unordered_map<std::string,int>   m_cache;

        VarianceCalculator();

        std::string make_key(int nr_of_segments,int nr_of_white_space);
        

    public:
        static VarianceCalculator* getCalculator();

        int get_variance(int nr_of_segments,int nr_of_white_space);

};

#endif
