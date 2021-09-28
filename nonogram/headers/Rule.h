#ifndef _RULE_H
#define _RULE_H	1

#include <constants.h>
#include <Segment.h>
#include <Location.h>

enum search_mode {search_first,search_next,search_count_not_white,search_end,search_stop};
enum search_dir  {search_forward,search_back_ward};

class Rule {
    
    protected:
        locations          *m_locations     = nullptr;
        segments           *m_segments      = nullptr;

        bool                m_min_max_set   = false;
        enum search_mode    m_search_mode   = search_first;
        enum search_dir     m_search_dir    = search_forward;
        Segment            *m_cur_searching = nullptr;
        Segment            *m_next_colored  = nullptr;
        int                 m_search_size   = 0;
        int                 m_max_u_size    = 0;
        int                 m_cur_pos       = 0;
        int                 m_u_count       = 0;
        int                 m_w_count       = 0;
        int                 m_c_count       = 0;
        
        void set_location_color(const int pos, const enum color new_color);
        void set_initial_min_max_segments();
        void calc_locks_rule_min_max();
        void apply_start_end_segments();
        void calc_locks_rule_out_of_reach();

        void init_searching();
        void parse_first_white();
        void parse_first_not_white();
        void parse_pos();
        void next_pos();

        void mark_u_white(int start_pos);
        void mark_and_lock(Segment *segment);

    public:
        Rule(locations *locations,segments *segments);
        ~Rule();

        
        void calc_locks();

};

#endif