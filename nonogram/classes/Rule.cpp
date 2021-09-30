#include <Rule.h>

Rule::Rule(locations *locations,segments *segments) {
    m_locations = locations;
    m_segments = segments;
    set_initial_min_max_segments();
}

void Rule::calc_locks() {
    calc_locks_rule_out_of_reach();
    apply_start_end_segments();
    calc_locks_rule_min_max();
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

//TODO: implement backwards
void Rule::init_searching() {
    m_cur_searching = nullptr;
    m_next_colored = nullptr;
    m_search_size = 0;
    m_max_u_size = -1;
    int white_size = 0;
    m_search_mode = search_stop;
    if (m_search_dir == search_forward) {
        m_cur_pos       = 0;
        for (int i = 0; i < m_segments->size();i++) {
            if (m_cur_searching ==nullptr && m_segments->at(i)->is_locked()) {
                m_cur_pos = m_segments->at(i)->get_end() + 1;
            }
            if (!m_segments->at(i)->is_locked() && m_segments->at(i)->get_color() !=white) {
                if (m_cur_searching == nullptr) {
                    m_cur_searching = m_segments->at(i);
                    m_search_size = m_cur_searching->get_min_size();
                    m_search_mode = search_first;
                } else {
                    m_next_colored = m_segments->at(i);
                    m_max_u_size = m_search_size + white_size + m_next_colored->get_size();
                    break;
                }
            }
            if (m_cur_searching != nullptr && m_segments->at(i)->get_color() == white)  {
                white_size++;
            }
        }
        m_u_count       = 0;
        m_w_count       = 0;
        m_c_count       = 0;
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
void Rule::calc_locks_rule_min_max() {
    for (int i = 0;i<m_segments->size();i++) {
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


/*
Examples:
Given               | Result
     01234567         | 01234567
1 4: UXUUUUUU         |  X UUUUU
*/
void Rule::calc_locks_rule_out_of_reach() {
    m_search_mode = search_first;
    m_search_dir  = search_forward;
    init_searching();
    //if (m_cur_searching != nullptr) {
        //TODO improve search mode end
        while (m_search_mode != search_stop && m_search_mode != search_end) {
            parse_pos();
            next_pos();
        }
    //}
    //TODO: search backwards
}

void Rule::parse_first_white() {
    m_w_count = 1;
    if (m_u_count > 0 ) {
        if (m_next_colored != nullptr) {
            // there is a next segment that is not locked yet
            if (m_u_count >=m_max_u_size) {
                m_search_mode = search_stop;
            }
        }  
        // can the segment we are searching fit in the no_color area?
        if (m_u_count < m_search_size) {
            // the unknowns must be white
            if (m_search_dir == search_forward) {
                mark_u_white(m_cur_pos -1,m_cur_searching->get_before());
            } else {
                mark_u_white(m_cur_pos -1,m_cur_searching->get_after());
            }
            m_search_mode = search_next;
        } else {
            // This could be this segment or the next segment
            // might still be able to determine this segment 
            // based on glue a split, but not here
            m_search_mode = search_stop;
        }
    } else {
        if (m_search_mode == search_first) {
            m_cur_searching->get_before()->set_start(m_cur_pos);
            m_search_mode = search_next;
        }
    }
    m_u_count = 0;
    m_c_count = 0;
}

 void Rule::parse_first_not_white() {
    m_c_count = 1;
    if (m_u_count > 0 ) {
        m_search_mode = search_count_not_white;
        if (m_next_colored !=nullptr) {
            if (m_u_count > m_search_size) {
                // this location belongs to the current segment or the next...
                // TODO can still search for biggest
                m_search_mode = search_end;
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
    } else if (m_search_mode == search_count_not_white) {
        if (cur_color == no_color || cur_color == white) {
            previous_pos();
            parse_last_not_white(cur_color == white);
            return;
        } else {
            m_c_count++;
            return;
        }
    }
}

void Rule::next_pos() {
    if (m_search_dir == search_forward) {
        if (m_cur_pos + 1 >= m_locations->size()) {
            m_search_mode = search_end;
        } else {
            m_cur_pos++;
        }
    } else {
        if (m_cur_pos -1 <= 0) {
            m_search_mode = search_end;
        } else {
            m_cur_pos--;
        }
    }
}

void Rule::previous_pos() {
    if (m_search_dir == search_forward) {
        if (m_cur_pos > 0) {
            m_cur_pos--;
        } else {
            m_search_mode = search_end;
        }
    } else {
        if (m_cur_pos + 1 < m_locations->size()) {
            m_cur_pos++;
        } else {
            m_search_mode = search_end;
        }
    }
}

void Rule::mark_u_white(const int start_pos, Segment *segment) {
    if (m_search_dir == search_forward) {
        for (int pos = start_pos;pos >=0;pos--) {
            if (m_locations->at(pos)->get_color() == no_color) {
                //set_location_color(pos,white);
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
        int last_pos = start_pos + nr;
        for (int pos = start_pos;pos <= last_pos;pos++) {
            set_location_segment(pos,segment);
        }
        int size = segment->get_min_size();
        int move_space = size - m_c_count;
        segment->set_min_start(start_pos - move_space);
        segment->set_max_end(last_pos + move_space);
    }
}

void Rule::mark_and_lock(Segment *segment) {
    for(int pos = segment->get_start();pos <= segment->get_end();pos++) {
        //set_location_color(pos,segment->get_color());
        set_location_segment(pos,segment);
        segment->lock();
    }
}

Rule::~Rule() {
    return;
}