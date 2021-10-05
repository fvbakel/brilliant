#ifndef _RULE_H
#define _RULE_H	1

#include <unordered_set>

#include <constants.h>
#include <Segment.h>
#include <Location.h>



enum search_mode {  search_first,   search_next,
                    search_count_c, search_count_c_ready,
                    search_count_u, search_count_u_ready,
                    search_stop
                };
enum search_dir  {search_forward,search_back_ward};

// todo: replace with two boolean
enum detect_rule {  detect_include,     // actual size can be bigger on both sizes
                    detect_start,       // must start exactly and have atleast the size
                    detect_end,         // must end exactly
                    detect_start_end    // start and end must match exactly
                };

class Rule {
    
    protected:
        locations          *m_locations     = nullptr;
        segments           *m_segments      = nullptr;
        enum direction      m_direction     = x_dir;

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
        void set_location_segment(const int pos, Segment *segment);
        void set_initial_min_max_segments();

        void init_searching();
        void next_to_search(); 
        Segment *next_segment(Segment *segment);

        void apply_min_max();
        void apply_start_end_segments();
        void apply_out_of_reach();

        void zero_special_case();
        void search_segments(const enum search_dir in_dir);
        void search_min_max_updates();

        void min_start_update(Segment *segment);
        void max_end_update(Segment *segment);

        void detect_colered_sequences();
        void detect_colered_sequence(
            const int   start, 
            const int   end,
            bool        start_must_match,
            bool        end_must_match
        );
        void detect_unkown_sequences();
        void detect_unkown_sequence(
            const int   start, 
            const int   end
        );
        void get_possible_segments(
            const int        start, 
            const int        end,
            enum color       allowed_color,
            bool             start_must_match,
            bool             end_must_match,
            segments         &possible
        );
        void mark_common(
            const int        start, 
            const int        end,
            bool             start_must_match,
            bool             end_must_match,
            segments        &possible
        );

        bool in_reach_of_next();
        bool in_reach_of_current();

        void set_segment_before_current();
        void set_segment_after_current();
        void set_segment(Segment *segment,const int start, const int end);

        void parse_first_white();
        void parse_first_not_white();
        void parse_last_not_white(const bool end_found);
        void parse_count_u_white();

        void parse_pos();
        void next_pos();
        void previous_pos();
        void pos_to_previous_white();

        void mark_u_white(const int start_pos, Segment *segment);
        void mark_segment_reverse();
        void mark_segment(Segment *segment);

    public:
        Rule(locations *locations,segments *segments);
        ~Rule();

        
        void calc_locks();

};

#endif