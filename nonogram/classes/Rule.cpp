#include <Rule.h>

Rule::Rule(locations *locations,segments *segments) {
    m_locations = locations;
    m_segments = segments;
    set_initial_min_max_segments();
}

void Rule::set_location_color(const int pos, const enum color new_color) {
    if (pos <m_locations->size()) {
        m_locations->at(pos)->determine_color(new_color);
    }
}

void Rule::calc_locks() {
    calc_locks_rule_out_of_reach();
    calc_locks_rule_min_max();
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
                set_location_color(pos,new_color);
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
    int nr_not_white = 0;
    int nr_white = 0;
    int nr_no_color = 0;
    enum color previous_color =no_color;
    Segment *next_colored = m_segments->at(1);
    if (next_colored->get_color() != white) {
        for (int pos = 0; pos <= next_colored->get_max_end();pos++) {
            enum color cur_color = m_locations->at(pos)->get_color();
            if (cur_color==no_color) {
                nr_no_color++;
            } else if (cur_color == white){
                nr_white++;
            } else {
                nr_not_white++;
            }
            if ( cur_color != previous_color) {
                if (previous_color == next_colored->get_color()) {
                    int begin_seq = pos - nr_not_white;
                    if (cur_color == white) {
                        
                    }
                    break;
                }
            }
            previous_color = cur_color;
        }
    }
}

Rule::~Rule() {
    return;
}