#ifndef _CONSTRAINT_H
#define _CONSTRAINT_H	1

#include <vector>

#include <constants.h>
#include <Segment.h>
#include <Location.h>


class Constraint {
    private:
        enum direction      m_direction    = x_dir;
        int                 m_size         = SIZE_UNKNOWN;
        int                 m_white_var    = SIZE_UNKNOWN;
        segments            m_segments;
        locations           m_locations;

        std::vector<std::vector<enum color> >  m_solutions;

        void update_size();
        void add_variation(
            std::vector<enum color> *solution_base,
            int                     current_pos,
            Segment                 *current_segment,
            int                     variation_remaining
        );
        void print_solution(std::vector<enum color> *solution_base,int max_pos = -1);
        

    public:
        Constraint(enum direction direction,std::vector<int> *blacks);
        ~Constraint();
       
        int get_size();
        int get_white_var(); 

        void add_location(Location *location);
        bool is_passed();

        void print();

        void calculate_solutions();
        int get_solution_size();
        void set_solution(int solution_index);
        void reset_solution();

};

typedef std::vector<Constraint*>    constraints;

#endif