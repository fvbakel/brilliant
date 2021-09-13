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

        void update_size();

    public:
        Constraint(enum direction direction,std::vector<int> *blacks);
        ~Constraint();
       
        int get_size();
        int get_white_var(); 

        void add_location(Location *location);
        bool is_passed();

        void print();

};

typedef std::vector<Constraint*>    constraints;

#endif