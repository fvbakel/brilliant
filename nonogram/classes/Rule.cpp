#include <Rule.h>

Rule::Rule(Constraint *contraint) {
    m_constraint = contraint;
    set_initial_min_max_segments();
}

void Rule::calc_locks() {
    detect_ready();
    search_min_max_updates();
    detect_colered_sequences();
    detect_unkown_sequences();

    // procedures below update the locations based on the new
    // start and end information
    apply_out_of_reach();
    apply_start_end_segments();
    apply_min_max();
}

/*
Given a location position, mark it with the given color. Note that this 
is for cases where we know the color, but not the segment.
*/
void Rule::set_location_color(const int pos, const enum color new_color) {
    if (pos <m_constraint->get_size()) {
        m_constraint->get_location(pos)->set_solved_color(new_color);
    }
}

/*
Given a location position, mark it with the given color and segment
*/
void Rule::set_location_segment(const int pos, Segment *segment) {
    if (pos <m_constraint->get_size()) {
        m_constraint->get_location(pos)->set_segment(segment);
    }
}

void Rule::set_initial_min_max_segments() {
    if (m_min_max_set == false) {
        if (m_constraint->get_segment_size() >= 0) {
            m_constraint->get_segment(0)->set_min_start(POS_NA);
        }
        if (m_constraint->get_segment_size() >= 1 ) {
            m_constraint->get_segment(m_constraint->get_segment_size()-1)->set_max_end(POS_NA);
            m_constraint->get_segment(m_constraint->get_segment_size()-1)->set_limit(m_constraint->get_size()-1);
        }
        if (m_constraint->get_segment_size() > 2 ) {
            m_constraint->get_segment(m_constraint->get_segment_size()-2)->set_max_end(m_constraint->get_size()-1);
            m_constraint->get_segment(1)->set_min_start(0);
        }
        zero_special_case();
        m_min_max_set = true;
    }
}

/*
Examples:
Given               | Result
     012345         | 012345
1 4: UUUUUU         | X XXXX

Given               | Result
     01234567       | 01234567
1 4: UUUUUUUU       | UUUUXXUU
*/
void Rule::apply_min_max() {
    for (int i = 0;i<m_constraint->get_segment_size();i++) {
        if (!m_constraint->get_segment(i)->is_locked()) {
            int min_end = m_constraint->get_segment(i)->get_min_end();
            int max_start = m_constraint->get_segment(i)->get_max_start();
            if (min_end != POS_NA && max_start != POS_NA) {
                enum color new_color = m_constraint->get_segment(i)->get_color();
                for (int pos=max_start; pos <= min_end; pos++) {
                    set_location_segment(pos,m_constraint->get_segment(i));
                }
            }
        }
    }
}

void Rule::apply_start_end_segments() {
    for (int i = 0;i<m_constraint->get_segment_size();i++) {
        if (!m_constraint->get_segment(i)->is_locked()) {
            if (m_constraint->get_segment(i)->is_start_and_end_set()) {
                mark_segment(m_constraint->get_segment(i));
            } else if (m_constraint->get_segment(i)->is_start_set()) {
                int start = m_constraint->get_segment(i)->get_start();
                set_location_segment(start,m_constraint->get_segment(i));
            } else if (m_constraint->get_segment(i)->is_end_set()) {
                int end = m_constraint->get_segment(i)->get_end();
                set_location_segment(end,m_constraint->get_segment(i));
            }
        }
    }
}

void Rule::apply_out_of_reach() {
    for (int i = 0;i<m_constraint->get_segment_size();i++) {
        if (!m_constraint->get_segment(i)->is_locked()) {
            int prev_max_end = -1;
            int next_min_start = m_constraint->get_size();
            if (m_constraint->get_segment(i)->get_before() != nullptr) {
                prev_max_end = m_constraint->get_segment(i)->get_before()->get_max_end();
            } 
            if (m_constraint->get_segment(i)->get_after() != nullptr) {
                next_min_start = m_constraint->get_segment(i)->get_after()->get_min_start();
            }
            for (int pos=prev_max_end+1 ; pos < next_min_start;pos++) {
                set_location_segment(pos,m_constraint->get_segment(i));
            }
        }
    }
}

/*
Mark all white if no colored is found
*/
void Rule::zero_special_case() {
    bool colored_found = false;
    for (int i = 0; i < m_constraint->get_segment_size(); i++) {
        if (m_constraint->get_segment(i)->get_color() != white) {
            colored_found =true;
            break;
        }
    }
    if (!colored_found) {
        // white only
        m_constraint->get_segment(0)->set_start(0);
        m_constraint->get_segment(0)->set_end(m_constraint->get_size()-1);
    }
    
}

/*
Given the min max setting of each segment, check if that min max is still possible
*/
void Rule::search_min_max_updates() {
    for (int i = 0; i<m_constraint->get_segment_size();i++) {
        if (m_constraint->get_segment(i)->get_color() != white) {
            min_start_update(m_constraint->get_segment(i));
            max_end_update(m_constraint->get_segment(i));
        }
    }
}

void Rule::min_start_update(Segment *segment) {
    int pos = segment->get_min_start();
    int stop_pos = segment->get_min_end();
    if (pos < 0) {
        std::__throw_runtime_error("Min start can not be smaller than zero for a non white segment!\n");
    }
    while (pos <= stop_pos ) {
        if (stop_pos >= m_constraint->get_size()) {
            std::__throw_runtime_error("Min end can not be larger than the location size for a non white segment!\n");
        }
        enum color loc_color = m_constraint->get_location(pos)->get_color();
        if (loc_color == white) {
            segment->set_min_start(pos+1);
            stop_pos = segment->get_min_end();
        }
        pos++;
    }
}

void Rule::max_end_update(Segment *segment) {
    int pos = segment->get_max_end();
    int stop_pos = segment->get_max_start();
    while (pos >= stop_pos) {
        enum color loc_color = m_constraint->get_location(pos)->get_color();
        if (loc_color == white) {
            segment->set_max_end(pos  - 1);
            stop_pos = segment->get_max_start();
        }
        pos--;
    }
}

void Rule::detect_ready() {
    int c_count = 0;
    int w_count = 0;
    int u_count = 0;
    int w_expect = m_constraint->get_colored_size(white);
    int c_expect = m_constraint->get_size() - w_expect;
    for (int pos = 0; pos < m_constraint->get_size();pos++) {
        enum color loc_color = m_constraint->get_location(pos)->get_color();
        if (loc_color == white)     w_count++;
        if (loc_color == black)     c_count++;
        if (loc_color == no_color)  u_count++;
    }

    enum color mark_color = no_color;
    if (u_count != 0 && c_count == c_expect) {
        // all u is white  
        mark_color = white;
    } else if (u_count != 0 && w_count == w_expect) {
        // all u is colored
        // assume black for now ....
        mark_color = black;
    } else {
        return;
    }

    if (mark_color != no_color) {
        for (int pos = 0; pos < m_constraint->get_size();pos++) {
            enum color loc_color = m_constraint->get_location(pos)->get_color();
            if (loc_color == no_color) {
                set_location_color(pos,mark_color);
            } 
        }
    }
}

/*
Find each sequence of colored locations. 
*/
void Rule::detect_colered_sequences() {
    int start = POS_NA;
    int last  = POS_NA;
    bool start_must_match = true;
    bool end_must_match   = false;
    for (int pos = 0; pos < m_constraint->get_size();pos++) {
        enum color loc_color = m_constraint->get_location(pos)->get_color();
        if (loc_color != white && loc_color != no_color && start == POS_NA) {
            start = pos;
            last  = pos;
        } else if (loc_color != white && loc_color != no_color && start != POS_NA) {
            last  = pos;
        } else if ( (loc_color == white || loc_color == no_color) && start != POS_NA) {
            if (loc_color == white) {
                end_must_match = true;
            }
            detect_colered_sequence(start,last,start_must_match,end_must_match);
        }
        if (loc_color == white || loc_color == no_color) {
            start = POS_NA;
            last  = POS_NA;
            if (loc_color == no_color) {
                start_must_match = false;
                end_must_match = false;
            } 
            if (loc_color == white) {
                start_must_match = true;
                end_must_match = false;
            }
        }
    }
    if ( start != POS_NA ) {
        end_must_match = true;
        detect_colered_sequence(start,last,start_must_match,end_must_match);
    }
}

/*
Given a start and end pos that are colored:
1. If it must belongs to exactly one segment, apply that segment
If 1 does not apply:
2. Update the max end of segments that must be before
3. Update the min start of segments that must be after
*/
void Rule::detect_colered_sequence(
    const int   start, 
    const int   end,
    bool        start_must_match,
    bool        end_must_match
) {
    Segment *cur_segment   = nullptr;
    Segment *found_segment = nullptr;
    int nr_with_segment = 0;
    enum color loc_color = m_constraint->get_location(start)->get_color();
    int size = (end - start) + 1;
    for (int pos = start;pos <=end;pos++) {
        cur_segment = m_constraint->get_location(pos)->get_segment_for_dir(m_constraint->get_direction());
        if (cur_segment != nullptr) {
            if (cur_segment->is_locked()) {
                return;
            }
            nr_with_segment++;
            found_segment = cur_segment;
        }
    }

    if (nr_with_segment > 0 && nr_with_segment < size) {
        // one or more locations found that are not assigned to the same segment.
        set_segment(found_segment,start,end);
    }
    if (nr_with_segment > 0) {
        return;
    }

    segments possible;
    get_possible_segments(start,end,loc_color,start_must_match,end_must_match,possible);

    if (possible.size() == 0) {
        std::__throw_runtime_error("No segment possible?");
    }

    if (possible.size() == 1) {
        set_segment(possible[0],start,end);
        return;
    } else {
        if (    possible[0]->get_before() != nullptr &&
                possible[0]->get_before()->get_max_end() >= start 
        ) {
                possible[0]->get_before()->set_max_end(start-1);
        }
        int last_i = possible.size() -1;
        if (    possible[last_i]->get_after() != nullptr &&
                possible[last_i]->get_after()->get_min_start() <= end 
        ) {
                possible[last_i]->get_after()->set_min_start(end+1);
        }
    }
    mark_common(start,end,start_must_match,end_must_match,possible);
}

void Rule::detect_unkown_sequences() {
    int start = POS_NA;
    int last  = POS_NA;
    for (int pos = 0; pos < m_constraint->get_size();pos++) {
        enum color loc_color = m_constraint->get_location(pos)->get_color();
        if (loc_color == white && last == POS_NA ) {
            start = pos;
        } else if (loc_color != white && (start != POS_NA || pos == 0) && last == POS_NA) {
            start = pos;
            last  = pos;
        } else if (loc_color != white && start != POS_NA && last != POS_NA) {    
            last  = pos;
        } else if ( loc_color == white && start != POS_NA  && last != POS_NA) {
            detect_unkown_sequence(start,last);
            start = pos;
            last  = POS_NA;
        }
    }
    if ( start != POS_NA  && last !=POS_NA) {
        detect_unkown_sequence(start,last);
    }
}

/*
Given a sequence of unknown and colored, determine if any segment can fit in
this exact space. If not, it must be white
*/
void Rule::detect_unkown_sequence(
    const int   start, 
    const int   end
) {
    bool can_have_one =false;
    int size = (end - start) + 1;
    for (int i = 0;i<m_constraint->get_segment_size();i++) {
        Segment *cur_segment = m_constraint->get_segment(i);
        if (    
                cur_segment->get_color()     != white &&
                cur_segment->get_max_start() >= start && 
                cur_segment->get_min_start() <= end && 
                cur_segment->get_max_end()   >= start   && 
                cur_segment->get_min_end()   <= end   && 
                cur_segment->get_min_size()  <= size
        ) {
            can_have_one = true;
            break;
        }
    }
    if (!can_have_one) {
        for (int pos =start; pos<=end;pos++) {
            set_location_color(pos,white);
        }
    }
}

void Rule::get_possible_segments(
    const int        start, 
    const int        end,
    enum color       allowed_color,
    bool             start_must_match,
    bool             end_must_match,
    segments         &possible
) {
    int size = (end - start) + 1;
    for (int i = 0;i<m_constraint->get_segment_size();i++) {
        Segment *cur_segment = m_constraint->get_segment(i);
        if (    
                allowed_color                == cur_segment->get_color() &&
                cur_segment->get_max_end()   >= end   && 
                cur_segment->get_min_start() <= start && (
                    start_must_match             == false ||
                    cur_segment->get_max_start() >= start
                ) && (
                    end_must_match               == false ||
                    cur_segment->get_min_end()   <= end
                ) &&
                cur_segment->get_min_size()  >= size
        ) {
            if (start_must_match && end_must_match) {
                if (cur_segment->get_min_size()  == size) {
                    possible.push_back(cur_segment);
                }
            } else {
                possible.push_back(cur_segment);
            }
        }
        
    }
}

/*
Given that the segments in possible are possible solutions 
for the given start and end position.

Mark the locations with the color that must be common in all possible solutions

Note that this might be an expensive function to use in some cases.
*/
void Rule::mark_common(
    const int        start, 
    const int        end,
    bool             start_must_match,
    bool             end_must_match,
    segments        &possible
) {
    if (possible.size() < 2) {
        std::__throw_runtime_error("Must have at least two possibilities!");
    }
    int     size                = (end - start) + 1;
    int     common_atleast_size = possible[0]->get_min_size();
    bool    all_same_size       = true;
    for (int i = 1; i < possible.size(); i++) {
        int this_size = possible[i]->get_min_size();
        if (this_size != common_atleast_size) {
            all_same_size = false;
        }
        if (common_atleast_size > this_size) {
            common_atleast_size = this_size;
        }
        if (common_atleast_size == size && all_same_size == false) {
            // no purpose to continue the search....
            break;
        }
    }
    int mark_extra = common_atleast_size - size;
    if (mark_extra > 0) {
        enum color seg_color = possible[0]->get_color();
        if (start_must_match ) {
            for (int pos = end + 1 ;pos <= (end + mark_extra) ;pos++) {
                set_location_color(pos,seg_color);
            }
        }
        if ( end_must_match ) {
            for (int pos = start - 1 ;pos >= (start - mark_extra) ;pos--) {
                set_location_color(pos,seg_color);
            }
        }

        //TODO: we could further improve by checking the number of unknown+colored on both sides
    }
    if (    all_same_size       && 
            mark_extra >= 0     && (
                start_must_match ||
                end_must_match   ||
                (mark_extra == 0)
            ) 
        ) {
        if (start_must_match || mark_extra == 0) {
            set_location_color((end + mark_extra + 1),white);
        }
        if (end_must_match  || mark_extra == 0) {
            set_location_color((start - mark_extra - 1),white);
        }
    }

}

void Rule::set_segment(Segment *segment,const int start, const int end) {
    int size = segment->get_min_size();
    int c_count = (end - start) + 1;
    int move_space = size - c_count;
    segment->set_min_start(start - move_space);
    segment->set_max_end(end + move_space);
    for (int pos = start; pos <= end; pos++) {
        set_location_segment(pos,segment);
    }
}

/*
Given a segment with a valid start and end set,
mark all related locations and lock this segment
*/
void Rule::mark_segment(Segment *segment) {
    for(int pos = segment->get_start();pos <= segment->get_end();pos++) {
        set_location_segment(pos,segment);
        segment->lock();
    }
}

Rule::~Rule() {
    return;
}