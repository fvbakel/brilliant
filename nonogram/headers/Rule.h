#ifndef _RULE_H
#define _RULE_H	1

#include <unordered_set>

#include <constants.h>
#include <Constraint.h>
#include <Segment.h>
#include <Location.h>

class Constraint;
class Rule {
    
    protected:
        Constraint         *m_constraint    = nullptr; 
        bool                m_min_max_set   = false;
        
        void set_location_color(const int pos, const enum color new_color);
        void set_location_segment(const int pos, Segment *segment);
        void set_initial_min_max_segments();

        void apply_min_max();
        void apply_start_end_segments();
        void apply_out_of_reach();

        void zero_special_case();
        void search_min_max_updates();

        void min_start_update(Segment *segment);
        void max_end_update(Segment *segment);

        void detect_ready();
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

        void set_segment(Segment *segment,const int start, const int end);
        void mark_segment(Segment *segment);

    public:
        Rule(Constraint *contraint);
        ~Rule();

        
        void calc_locks();

};

#endif