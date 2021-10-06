#ifndef _NONOGRAM_H
#define _NONOGRAM_H	1

#include <MainConstraint.h>
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
        bool                    m_rule_improve_log  = false;
        bool                    m_solving           = false;

        main_constraints    m_x_contraints;
        main_constraints    m_y_contraints;
        locations           m_locations;

        bool solve_constraint_backtrack(int constraint_index = 0);
        void read_file();

        void create_locations();
        bool has_dirty_locations();

        void line_to_int_array(
            const string &line,
            std::vector<int> *result,
            const char file_delim
        );
        void parse_txt_line(std::string &line,enum direction &cur_dir);
        void parse_non_line(std::string &line,enum direction &cur_dir);

        main_constraints *get_constraints (enum direction for_direction);

        MainConstraint *get_next_to_calculate();
        MainConstraint *get_next_to_calculate_dir(enum direction for_direction);
        void calc_constraint_solutions (enum direction for_direction = y_dir) ;
        void lock_constraint_solutions (
            enum direction for_direction
        );
        int reduce_constraint_solutions (
            enum direction for_direction
        );

        enum direction reduce_and_lock (
            enum direction cur_dir
        );
        void calc_and_lock_constraints (
            enum direction for_direction
        );

        enum direction swap_direction(enum direction cur_dir);

        void apply_rules_only();
        void apply_solutions_and_rules();

        bool is_consistent_dir(enum direction for_direction);
        bool is_input_valid_dir(enum direction for_direction);
        int get_colored_size_sum(enum direction for_direction,enum color for_color);

        void rule_improve_log(Constraint *constraint);
    public:
        Nonogram();
        Nonogram(const string &filename);
        ~Nonogram();

        bool solve();

        Location *get_Location(const int x, const int y);

        bool is_input_valid();
        bool is_solved();
        bool is_consistent();
        bool is_complete();

        void print();

        void reset();

        void enable_rule_improve_log();
};

#endif