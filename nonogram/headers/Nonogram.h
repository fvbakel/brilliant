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
        enum color              m_colors[2]         = {black,white};
        string                  m_filename          = "";
        int                     m_x_size            = SIZE_UNKNOWN;
        int                     m_y_size            = SIZE_UNKNOWN;
        bool                    m_valid             = false;
        bool                    m_valid_checked     = false;
        enum non_parse_state    m_non_parse_state   = searching;

        std::unordered_set<enum direction>  m_sol_calcs;
        constraints     m_x_contraints;
        constraints     m_y_contraints;
        locations       m_locations;

        void read_file();

        void create_locations();

        void line_to_int_array(
            const string &line,
            std::vector<int> *result,
            const char file_delim
        );
        void parse_txt_line(std::string &line,enum direction &cur_dir);
        void parse_non_line(std::string &line,enum direction &cur_dir);

        constraints *get_constraints (enum direction for_direction);

        Constraint *get_next_to_calculate();
        Constraint *get_next_to_calculate_dir(enum direction for_direction);
        void calc_constraint_solutions (enum direction for_direction = y_dir) ;
        void lock_constraint_solutions (
            enum direction for_direction,
            std::unordered_set<int> *affected
        );
        int reduce_constraint_solutions (
            enum direction for_direction,
            std::unordered_set<int> *affected
        );

        enum direction reduce_and_lock (
            enum direction cur_dir,
            std::unordered_set<int> *affected
        );

        enum direction swap_direction(enum direction cur_dir);

        void init_constraint_solutions_1();
        void init_constraint_solutions_2();

        bool is_consistent_dir(enum direction for_direction);
        bool is_input_valid_dir(enum direction for_direction);
        int get_colored_size_sum(enum direction for_direction,enum color for_color);

    public:
        Nonogram();
        Nonogram(const string &filename);
        ~Nonogram();

        bool solve_location_backtrack(int location_index = 0);
        bool solve_constraint_backtrack(int constraint_index = 0);

        Location *get_Location(const int x, const int y);

        bool is_input_valid();
        bool is_solved();
        bool is_consistent();
        bool is_complete();

        void print();

        void reset();
};

#endif