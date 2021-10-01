#include <Rule.h>

Rule::Rule(locations *locations,segments *segments) {
    m_locations = locations;
    m_segments = segments;
    set_initial_min_max_segments();
}

void Rule::calc_locks() {
    search_segments(search_forward);
    search_segments(search_back_ward);

    // procedures below update the locations based on the new
    // start and end information
    apply_out_of_reach();
    apply_start_end_segments();
    apply_min_max();
}

void Rule::set_location_color(const int pos, const enum color new_color) {
    if (pos <m_locations->size()) {
        m_locations->at(pos)->set_solved_color(new_color);
    }
}

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

//TODO: Just move to the next segment to search from here
void Rule::init_searching() {
    m_cur_searching     = nullptr;
    m_next_colored      = nullptr;
    m_search_size       = 0;
    m_max_u_size        = -1;
    int white_size      = 0;
    Segment *segment    = nullptr;
    m_search_mode       = search_stop;
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
                m_next_colored = segment;
                m_max_u_size = m_search_size + white_size + m_next_colored->get_size();
                break;
            }
            if (m_cur_searching == nullptr && !segment->is_locked()) {
                m_cur_searching = segment;
                m_search_size = m_cur_searching->get_min_size();
                m_search_mode = search_first;
            }
        }
        if (m_cur_searching != nullptr && segment->get_color() == white)  {
            white_size++;
        }
        segment = next_segment(segment);
    }
    m_u_count       = 0;
    m_w_count       = 0;
    m_c_count       = 0;
}

void Rule::set_initial_min_max_segments() {
    if (m_min_max_set == false) {
        if (m_segments->size() >= 0) {
            m_segments->at(0)->set_min_start(POS_NA);
        }
        if (m_segments->size() >= 1 ) {
            m_segments->at(m_segments->size()-1)->set_max_end(POS_NA);
        }
        if (m_segments->size() >= 2 ) {
            m_segments->at(m_segments->size()-2)->set_max_end(m_locations->size()-1);
        }
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
                    //set_location_color(pos,new_color);
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
                mark_and_lock(m_segments->at(i));
            } else if (m_segments->at(i)->is_start_set()) {
                int start = m_segments->at(i)->get_start();
                //set_location_color(start,m_segments->at(i)->get_color());
                set_location_segment(start,m_segments->at(i));
            } else if (m_segments->at(i)->is_end_set()) {
                int end = m_segments->at(i)->get_end();
                // set_location_color(end,m_segments->at(i)->get_color());
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
Given that the segment we are searching for must be atleast 
"before" the current position, where before depends on the search direction
*/
// TODO: when ever this function is used, we can move to the next segment to search
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
                //TODO: current segment can be before or after this white space
                m_search_mode = search_count_u;
            } else {
                // segment must be somewhere in the u space
                set_segment_before_current();
                m_search_mode = search_stop;
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
                // TODO can still search for biggest
                m_search_mode = search_stop;
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
        mark_and_lock(m_cur_searching);
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
        mark_and_lock(m_cur_searching);
        // move the search status to the next unlocked segment
        init_searching();
        previous_pos();
    } else {
        // we only found a part of this segment
        mark_segment_reverse(m_cur_pos,m_c_count,m_cur_searching);
        m_search_mode=search_stop;
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
                set_segment_before_current();
                m_search_mode = search_stop;
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
Given that we are at a position and we know there must be atleast one white
before. Where before depends on the search direction.
This fuction will move the current position back to the previous white pos
*/
void Rule::pos_to_previous_white() {
    bool found = false;
    while (!found) {
        previous_pos();
        if (m_locations->at(m_cur_pos)->get_color() == white) {
            found = true;
        }
        if (m_search_mode == search_stop) {
            std::__throw_runtime_error("Can not find previous white (pos_to_previous_white)!");
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

void Rule::mark_segment_reverse(const int start_pos,const int nr, Segment *segment) {
    if (m_search_dir == search_forward) {
        int last_pos = start_pos - (nr -1);
        for (int pos = start_pos;pos >= last_pos;pos--) {
            set_location_segment(pos,segment);
        }
        int size = segment->get_min_size();
        int move_space = size - m_c_count;
        segment->set_min_start(last_pos - move_space);
        segment->set_max_end(start_pos + move_space);
    } else {
        int last_pos = start_pos + (nr - 1);
        for (int pos = start_pos;pos <= last_pos;pos++) {
            set_location_segment(pos,segment);
        }
        int size = segment->get_min_size();
        int move_space = size - m_c_count;
        segment->set_min_start(start_pos - move_space);
        segment->set_max_end(last_pos + move_space);
    }
}

/*
Given a segment with a valid start and end set,
mark all related locations and lock this segment
*/
void Rule::mark_and_lock(Segment *segment) {
    for(int pos = segment->get_start();pos <= segment->get_end();pos++) {
        set_location_segment(pos,segment);
        segment->lock();
    }
}

Rule::~Rule() {
    return;
}