#ifndef _CONSTRAINT_H
#define _CONSTRAINT_H	1

#include <vector>

#include <constants.h>
#include <Piece.h>
#include <Segment.h>
#include <Location.h>


class Constraint {
    private:
        enum direction      m_direction    = x_dir;
        int                 m_min_size     = SIZE_UNKNOWN;
        int                 m_max_size     = SIZE_UNKNOWN;
        segments            m_segments;
        locations           m_locations;

    public:
        Constraint(enum direction direction,std::vector<int> *blacks);
        ~Constraint();

        int get_min_size();
        
        int get_max_size();
        void set_max_size(const int size);
        
        void add_location(Location *location);
        bool is_passed();

};

typedef std::vector<Constraint*>    constraints;

#endif