#include <Rule.h>

Rule::Rule(locations *locations,segments *segments) {
    m_locations = locations;
    m_segments  = segments;
    m_direction = segments->at(0)->get_direction();
    set_initial_min_max_segments();
}

void Rule::calc_locks() {
    //TODO: determine the best order of calculations
    search_min_max_updates();
    detect_colered_sequences();
    detect_unkown_sequences();
    search_segments(search_forward);
    search_segments(search_back_ward);

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
    if (pos <m_locations->size()) {
        m_locations->at(pos)->set_solved_color(new_color);
    }
}

/*
Given a location position, mark it with the given color and segment
*/
void Rule::set_location_segment(const int pos, Segment *segment) {
    if (pos <m_locations->size()) {
        m_locations->at(pos)->set_segment(segment);
    }
}

/*
Get the next segment, given the current search direction
*/
Segment* Rule::next_segment(Segment *segment) {
    if (m_search_dir == search_forward) {
        return segment->get_after();
    } else {
        return segment->get_before();
    }
}


/*
The procedure below starts the searching with the first
segment that is not locked. The current pos is set to 
the next pos after the end of the locked segment.
*/
void Rule::init_searching() {
    m_cur_searching     = nullptr;
    m_next_colored      = nullptr;
    m_search_size       = 0;
    m_max_u_size        = -1;
    m_u_count           = 0;
    m_w_count           = 0;
    m_c_count           = 0;
    m_search_mode       = search_stop;

    int white_size      = 0;
    Segment *segment    = nullptr;
    
    if (m_search_dir == search_forward) {
        m_cur_pos       = 0;
        segment = m_segments->at(0);
    } else {
        m_cur_pos       = m_locations->size()-1;
        segment = m_segments->at(m_segments->size()-1);
    }
    while (segment != nullptr) {
        if (m_cur_searching ==nullptr && segment->is_locked()) {
            if (m_search_dir == search_forward) {
                m_cur_pos = segment->get_end() + 1;
            } else {
                m_cur_pos = segment->get_start() - 1;
            }
        }
        if (segment->get_color() !=white) {
            if (m_cur_searching != nullptr) {
                m_next_colored  = segment;
                m_max_u_size    = m_search_size + white_size + m_next_colored->get_size();
                break;
            }
            if (m_cur_searching == nullptr && !segment->is_locked()) {
                m_cur_searching = segment;
                m_search_size   = m_cur_searching->get_min_size();
                m_search_mode   = search_first;
            }
        }
        if (m_cur_searching != nullptr && segment->get_color() == white)  {
            white_size++;
        }
        segment = next_segment(segment);
    }
}

/*
Given a search that is in process and we know that the next colored segment 
must start after the current position,
- reset the current search state.
- move to the next position

*/
void Rule::next_to_search() {
    m_max_u_size    = -1;
    m_u_count       = 0;
    m_w_count       = 0;
    m_c_count       = 0;
    m_search_mode   = search_stop;

    int white_size      = 0;
    Segment *segment    = nullptr;

    if (m_next_colored == nullptr) {
        return;
    }
    if (m_cur_searching == nullptr) {
        std::__throw_runtime_error("next_to_search preconditions is not met.");
    }

    m_cur_searching     = m_next_colored;
    m_search_size       = m_cur_searching->get_min_size();
    m_search_mode       = search_count_u;
    m_next_colored      = nullptr;
    segment = next_segment(m_cur_searching);
    while (segment != nullptr) {
        if (segment->get_color() !=white) {
            if (m_cur_searching != nullptr) {
                m_next_colored = segment;
                m_max_u_size = m_search_size + white_size + m_next_colored->get_size();
                break;
            }
            if (m_cur_searching == nullptr && !segment->is_locked()) {
                m_cur_searching = segment;
                m_search_size   = m_cur_searching->get_min_size();
            }
        }
        if (m_cur_searching != nullptr && segment->get_color() == white)  {
            white_size++;
        }
        segment = next_segment(segment);
    }
}

void Rule::set_initial_min_max_segments() {
    if (m_min_max_set == false) {
        if (m_segments->size() >= 0) {
            m_segments->at(0)->set_min_start(POS_NA);
        }
        if (m_segments->size() >= 1 ) {
            m_segments->at(m_segments->size()-1)->set_max_end(POS_NA);
        }
        if (m_segments->size() > 2 ) {
            m_segments->at(m_segments->size()-2)->set_max_end(m_locations->size()-1);
            m_segments->at(1)->set_min_start(0);
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
    for (int i = 0;i<m_segments->size();i++) {
        if (!m_segments->at(i)->is_locked()) {
            int min_end = m_segments->at(i)->get_min_end();
            int max_start = m_segments->at(i)->get_max_start();
            if (min_end != POS_NA && max_start != POS_NA) {
                enum color new_color = m_segments->at(i)->get_color();
                for (int pos=max_start; pos <= min_end; pos++) {
                    set_location_segment(pos,m_segments->at(i));
                }
            }
        }
    }
}

void Rule::apply_start_end_segments() {
    for (int i = 0;i<m_segments->size();i++) {
        if (!m_segments->at(i)->is_locked()) {
            if (m_segments->at(i)->is_start_and_end_set()) {
                mark_segment(m_segments->at(i));
            } else if (m_segments->at(i)->is_start_set()) {
                int start = m_segments->at(i)->get_start();
                set_location_segment(start,m_segments->at(i));
            } else if (m_segments->at(i)->is_end_set()) {
                int end = m_segments->at(i)->get_end();
                set_location_segment(end,m_segments->at(i));
            }
        }
    }
}

void Rule::apply_out_of_reach() {
    for (int i = 0;i<m_segments->size();i++) {
        if (!m_segments->at(i)->is_locked()) {
            int prev_max_end = -1;
            int next_min_start = m_locations->size();
            if (m_segments->at(i)->get_before() != nullptr) {
                prev_max_end = m_segments->at(i)->get_before()->get_max_end();
            } 
            if (m_segments->at(i)->get_after() != nullptr) {
                next_min_start = m_segments->at(i)->get_after()->get_min_start();
            }
            for (int pos=prev_max_end+1 ; pos < next_min_start;pos++) {
                set_location_segment(pos,m_segments->at(i));
            }
        }
    }
}

/*
Mark all white if no colored is found
*/
void Rule::zero_special_case() {
    bool colored_found = false;
    for (int i = 0; i < m_segments->size(); i++) {
        if (m_segments->at(i)->get_color() != white) {
            colored_found =true;
            break;
        }
    }
    if (!colored_found) {
        // white only
        m_segments->at(0)->set_start(0);
        m_segments->at(0)->set_end(m_locations->size()-1);
    }
    
}

/*
Locate segments and update the start, end, min_start and max_end
information.
*/
void Rule::search_segments(const enum search_dir in_dir) {
    m_search_mode = search_first;
    m_search_dir  = in_dir;
    init_searching();
    while (m_search_mode != search_stop) {
        parse_pos();
        next_pos();
    }

}

/*
Given the min max setting of each segment, check if that min max is still possible
*/
void Rule::search_min_max_updates() {
    for (int i = 0; i<m_segments->size();i++) {
        if (m_segments->at(i)->get_color() != white) {
            min_start_update(m_segments->at(i));
            max_end_update(m_segments->at(i));
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
        if (stop_pos >= m_locations->size()) {
            std::__throw_runtime_error("Min end can not be larger than the location size for a non white segment!\n");
        }
        enum color loc_color = m_locations->at(pos)->get_color();
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
        enum color loc_color = m_locations->at(pos)->get_color();
        if (loc_color == white) {
            segment->set_max_end(pos  - 1);
            stop_pos = segment->get_max_start();
        }
        pos--;
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
    for (int pos = 0; pos < m_locations->size();pos++) {
        enum color loc_color = m_locations->at(pos)->get_color();
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
    enum color loc_color = m_locations->at(start)->get_color();
    int size = (end - start) + 1;
    for (int pos = start;pos <=end;pos++) {
        cur_segment = m_locations->at(pos)->get_segment_for_dir(m_direction);
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
    for (int pos = 0; pos < m_locations->size();pos++) {
        enum color loc_color = m_locations->at(pos)->get_color();
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
    for (int i = 0;i<m_segments->size();i++) {
        Segment *cur_segment = m_segments->at(i);
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
    for (int i = 0;i<m_segments->size();i++) {
        Segment *cur_segment = m_segments->at(i);
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
            possible.push_back(cur_segment);
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
Given that the current location is white.
This function checks if the next segment can be "before" the current
position, where before depends on the search direction
Does not consider the values of other locations
*/
bool Rule::in_reach_of_next() {
    if (m_next_colored == nullptr) {
        return false;
    }
    if (m_search_dir == search_forward) {
        return (m_cur_pos > m_next_colored->get_min_end());
    } else {
        return (m_cur_pos < m_next_colored->get_max_start());
    }
}

/*
Given that the current location is white.
This function checks if the current segment we are
searching for can be "after" this. Where after depends on the
search direction
*/
bool Rule::in_reach_of_current() {
    if (m_search_dir == search_forward) {
        return (m_cur_pos < m_cur_searching->get_max_start());
    } else {
        return (m_cur_pos > m_cur_searching->get_min_end());
    }
}

/*
Given that the segment we are searching for must be at least 
"before" the current position, where before depends on the search direction
*/
void Rule::set_segment_before_current() {
    if (m_search_dir == search_forward) {
        m_cur_searching->set_max_end(m_cur_pos - 1);
    } else {
        m_cur_searching->set_min_start(m_cur_pos + 1);
    }
}

/*
Given that the segment we are searching for must be atleast 
"after" the current position, where after depends on the search direction
*/
void Rule::set_segment_after_current() {
    if (m_search_dir==search_forward) {
        m_next_colored->set_min_start(m_cur_pos + 1);
    } else {
        m_next_colored->set_max_end(m_cur_pos - 1);
    }
}

void Rule::parse_first_white() {
    m_w_count = 1;
    // TODO: we are a bit to strict with u count in all the code
    // we should add additional logic to check if the U space needs a leading white or not
    if (m_u_count > 0 ) {
        // Here we need to know if the next segment 
        // and the current segment can fir in the unkown
        // space that we found
        if (m_next_colored != nullptr) {
            if (in_reach_of_next()) {
                if (m_u_count >=m_max_u_size) {
                    // yes both segments could be in the unknown space we found
                    m_search_mode = search_stop;
                } else {
                    // no, both segments can not be in the unknown space we found
                    set_segment_after_current();
                }
            } else {
                // next segment can not be in the unknown space we found
                // and the next segment already has this information
            }
        }  
        // can the segment we are searching fit in the unknown space?
        if (m_u_count < m_search_size) {
            // the unknowns must be white, because this can not fit there
            if (m_search_dir == search_forward) {
                mark_u_white(m_cur_pos - 1,m_cur_searching->get_before());
            } else {
                mark_u_white(m_cur_pos + 1,m_cur_searching->get_after());
            }
            m_search_mode = search_next;
        } else {
            // This segment could be in the unknown space
            // can it fit after this white space?
            if (in_reach_of_current()) {
                m_search_mode = search_count_u;
            } else {
                // segment must be somewhere in the u space
                set_segment_before_current();
                next_to_search();
            }
        }
    } else {
        if (m_search_mode == search_first) {
            if (m_search_dir == search_forward) {
                m_cur_searching->get_before()->set_start(m_cur_pos);
            } else {
                m_cur_searching->get_after()->set_end(m_cur_pos);
            }
            m_search_mode = search_next;
        }
    }
    m_u_count = 0;
    m_c_count = 0;
}

 void Rule::parse_first_not_white() {
    m_c_count = 1;
    if (m_u_count > 0 ) {
        m_search_mode = search_count_c;
        if (m_next_colored != nullptr) {
            if (m_u_count > m_search_size) {
                // this location belongs to the current segment or the next...
                m_search_mode = search_count_u;
            } else {
                // Location is part of this segment
            }
        } else {
            // Location is part of this segment

        }
    } else {
        //found the location of this non white segment!
        if (m_search_dir == search_forward) {
            m_cur_searching->set_start(m_cur_pos);
        } else {
            m_cur_searching->set_end(m_cur_pos);
        }
        mark_segment(m_cur_searching);
        // move the search status to the next unlocked segment
        init_searching();
        previous_pos();
    }
    m_w_count = 0;
 }

/* We found a sequence of colored that we know must be part of
   the segment we are searching.
   - m_cur_pos is at the last pos of the color of this segment

*/
void Rule::parse_last_not_white(const bool end_found) {
    if (end_found || m_c_count == m_cur_searching->get_min_size()) {
        //found the location of this non white segment!
        if (m_search_dir == search_forward) {
            m_cur_searching->set_end(m_cur_pos);
        } else {
            m_cur_searching->set_start(m_cur_pos);
        }
        mark_segment(m_cur_searching);
        // move the search status to the next unlocked segment
        init_searching();
        previous_pos();
    } else {
        // we only found a part of this segment
        mark_segment_reverse();

        //TODO: we can improve here by continue of the search to improve the max end
        // based on the number of unknowns we count
        //m_search_mode=search_stop;
        m_search_mode = search_count_u;
    }
}

/*
Given:
- the segment we are searching for could fit in one or more u space blocks before.
- the current position is on the white

can it fit in the u space we just found? If not, could it fit after?

*/
void Rule::parse_count_u_white() {
    if (m_u_count == 0) {
        if (in_reach_of_current()) {
            // continue the search
            return;
        } else {
            set_segment_before_current();
            m_search_mode = search_stop;
        }
    } else {
        if ((m_u_count + m_c_count) < m_cur_searching->get_min_size()) {
            // can not fit, u space + c space could be the next segment
            if (in_reach_of_current()) {
                // continue the search
                return;
            } else {
                pos_to_previous_white();
                if (m_search_mode != search_stop) {
                    set_segment_before_current();
                    m_search_mode = search_stop;
                }
            }
        } else {
            // can fit, do we need to look further?
            if (in_reach_of_current()) {
                // continue the search
                return;
            } else {
                set_segment_before_current();
                m_search_mode = search_stop;
            }

        }
    }
}

/*
Based on the search mode, decide what function should process the current
position
*/
void Rule::parse_pos() {
    enum color cur_color = m_locations->at(m_cur_pos)->get_color();
    if (m_search_mode == search_first || m_search_mode == search_next) {
        if (cur_color == no_color) {
            m_u_count++;
            return;
        } else if (cur_color == white) {
            parse_first_white();
            return;
        } else {
            parse_first_not_white();
            return;
        }
    } else if (m_search_mode == search_count_c) {
        if (cur_color == no_color || cur_color == white) {
            previous_pos();
            parse_last_not_white(cur_color == white);
            return;
        } else {
            m_c_count++;
            return;
        }
    } else if (m_search_mode == search_count_c_ready) {
        parse_last_not_white(true);
        return;
    } else if (m_search_mode == search_count_u) {
        if (cur_color == no_color) {
            m_u_count++;
            return;
        } else if (cur_color == white) {
            parse_count_u_white();
            return;
        } else {
            m_c_count++;
            // no action needed in this case, just keep searching
            return;
        }
    }
    // TODO: implement search_count_u ready
}

void Rule::next_pos() {
    bool last=false;
    if (m_search_dir == search_forward) {
        if (m_cur_pos + 1 >= m_locations->size()) {
            last = true;
        } else {
            m_cur_pos++;
        }
    } else {
        if (m_cur_pos -1 < 0) {
            last = true;
        } else {
            m_cur_pos--;
        }
    }

    if (last) {
        if ( m_search_mode == search_count_c) {
            m_search_mode = search_count_c_ready;
        } else {
            m_search_mode = search_stop;
        }
    }
}

void Rule::previous_pos() {
    if (m_search_dir == search_forward) {
        if (m_cur_pos > 0) {
            m_cur_pos--;
        } else {
            m_search_mode = search_stop;
        }
    } else {
        if (m_cur_pos + 1 < m_locations->size()) {
            m_cur_pos++;
        } else {
            m_search_mode = search_stop;
        }
    }
}

/*
Given that we are at a position and we move to the previous until we find white.
This fuction will move the current position back to the previous white pos, 
or set the search mode to stop if that is not found
*/
void Rule::pos_to_previous_white() {
    bool found = false;
    while (!found) {
        previous_pos();
        if (m_search_mode == search_stop) {
            break;
        }
        if (m_locations->at(m_cur_pos)->get_color() == white) {
            found = true;
        }
    }
};

void Rule::mark_u_white(const int start_pos, Segment *segment) {
    if (m_search_dir == search_forward) {
        for (int pos = start_pos;pos >=0;pos--) {
            if (m_locations->at(pos)->get_color() == no_color) {
                set_location_segment(pos,segment);
            } else {
                break;
            }
        }
    } else {
        for (int pos = start_pos;pos < m_locations->size();pos++) {
            if (m_locations->at(pos)->get_color() == no_color) {
                set_location_segment(pos,segment);
            } else {
                break;
            }
        }
    }
}

void Rule::mark_segment_reverse() {
    int size = m_cur_searching->get_min_size();
    int move_space = size - m_c_count;
    int begin_move_space = move_space;
    if (begin_move_space > m_u_count) {
        begin_move_space = m_u_count;
    }
    if (m_search_dir == search_forward) {
        int start_pos = m_cur_pos - (m_c_count -1);
        for (int pos = m_cur_pos;pos >= start_pos;pos--) {
            set_location_segment(pos,m_cur_searching);
        }

        m_cur_searching->set_min_start(start_pos - begin_move_space);
        m_cur_searching->set_max_end(m_cur_pos + move_space);
    } else {
        int last_pos = m_cur_pos + (m_c_count - 1);
        for (int pos = m_cur_pos;pos <= last_pos;pos++) {
            set_location_segment(pos,m_cur_searching);
        }
        m_cur_searching->set_min_start(m_cur_pos - move_space);
        m_cur_searching->set_max_end(last_pos + begin_move_space);
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