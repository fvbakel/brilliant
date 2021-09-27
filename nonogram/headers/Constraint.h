#ifndef _CONSTRAINT_H
#define _CONSTRAINT_H	1

#include <vector>

#include <constants.h>
#include <Segment.h>
#include <Location.h>
#include <unordered_set>


class Constraint {
    protected:
        enum direction      m_direction    = x_dir;
        int                 m_size         = SIZE_UNKNOWN;
        int                 m_white_var    = SIZE_UNKNOWN;
        segments            m_segments;
        locations           m_locations;
        bool                m_locked       = false;
        bool                m_min_max_set  = false;

        std::vector<std::vector<enum color> >  m_solutions;

        void update_size();
        void set_initial_min_max_segments();
        void add_variation(
            std::vector<enum color> *solution_base,
            int                     current_pos,
            Segment                 *current_segment,
            int                     variation_remaining
        );
        void print_solution(std::vector<enum color> *solution_base,int max_pos = -1);
        int reduce_sol(int pos, enum color required_color);
        bool set_color(
            std::vector<enum color> *solution_base,
            int current_pos,
            enum color
        );

    public:
        Constraint(enum direction direction);
        ~Constraint();
        
        enum direction get_direction();
        int get_size();
        int get_white_var(); 
        int get_variation(); 

        void add_location(Location *location);

        bool is_valid();
        bool is_passed();
        int get_colored_size(enum color for_color);

        void print();


        void calculate_solutions();
        int get_solution_size();
        void set_solution(int solution_index);
        void reset_solution();

        void set_location_color(const int pos, const enum color new_color,std::unordered_set<int>  *affected);
        void calc_locks_rule_min_max(std::unordered_set<int>  *affected);
        void calc_locks_rules(std::unordered_set<int>  *affected);
        void calc_locks(std::unordered_set<int> *affected);
        int reduce_solutions();

        void debug_dump();
};

typedef std::vector<Constraint*>    constraints;

#endif