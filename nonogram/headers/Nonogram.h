#ifndef _NONOGRAM_H
#define _NONOGRAM_H	1

#include <Constraint.h>
#include <string>
#include <vector>

using namespace std;

class Nonogram {
    private:
        string          m_filename      = "";
        int             m_x_size        = SIZE_UNKNOWN;
        int             m_y_size        = SIZE_UNKNOWN;
        constraints     m_x_contraints;
        constraints     m_y_contraints;
        //Solution     *m_Solution = nullptr;

        void read_file();
        void line_to_int_array(const string &line,std::vector<int> *result);

    public:
        Nonogram();
        Nonogram(const string &filename);
        ~Nonogram();
};

#endif