#ifndef _NONOGRAM_H
#define _NONOGRAM_H	1

#include <Constraint.h>
#include <Location.h>
#include <string>
#include <vector>
#include <unordered_set>

using namespace std;

class Nonogram {
    private:
        enum color      m_colors[2]     = {black,white};
        string          m_filename      = "";
        int             m_x_size        = SIZE_UNKNOWN;
        int             m_y_size        = SIZE_UNKNOWN;

        std::unordered_set<enum direction>  m_sol_calcs;
        constraints     m_x_contraints;
        constraints     m_y_contraints;
        locations       m_locations;

        void read_file();
        //void fill_sizes();
        void create_locations();

        void line_to_int_array(const string &line,std::vector<int> *result);
        void calc_constraint_solutions (enum direction for_direction = y_dir) ;
        void lock_constraint_solutions (
            enum direction for_direction,
            std::vector<int> *affected
        );
        int reduce_constraint_solutions (
            enum direction for_direction,
            std::vector<int> *affected
        );

    public:
        Nonogram();
        Nonogram(const string &filename);
        ~Nonogram();

        bool solve_location_backtrack(int location_index = 0);
        bool solve_constraint_backtrack(int constraint_index = 0);

        Location *get_Location(const int x, const int y);

        bool is_solved();
        bool is_consistent();
        bool is_x_consistent();
        bool is_y_consistent();
        bool is_complete();

        void print();

        void reset();
};

#endif