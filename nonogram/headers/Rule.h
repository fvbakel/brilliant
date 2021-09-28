#ifndef _RULE_H
#define _RULE_H	1

#include <constants.h>
#include <Segment.h>
#include <Location.h>

class Rule {
    
    protected:
        locations  *m_locations     = nullptr;
        segments   *m_segments      = nullptr;

        bool        m_min_max_set   = false;
        
        void set_location_color(const int pos, const enum color new_color);
        void set_initial_min_max_segments();
        void calc_locks_rule_min_max();
        void calc_locks_rule_out_of_reach();

    public:
        Rule(locations *locations,segments *segments);
        ~Rule();

        
        void calc_locks();

};

#endif