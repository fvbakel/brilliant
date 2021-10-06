#include <stdio.h>
#include <cstdlib>
#include <assert.h>
#include <cmath>
#include <sstream>
#include <iostream>


#include <Constraint.h>
#include <VarianceCalculator.h>

Constraint::Constraint(enum direction direction) {
    m_direction = direction;
    m_locked = false;
}

void Constraint::add_location(Location *location) {
    m_locations.push_back(location);
    update_size();
}

enum direction Constraint::get_direction() {
    return m_direction;
}

int Constraint::get_size() {
    return m_size;
}

int Constraint::get_white_var() {
    return m_white_var;
}

int Constraint::get_segment_size() {
    return m_segments.size();
}
Segment* Constraint::get_segment(int index) {
    return m_segments.at(index);
}
Location* Constraint::get_location(int index) {
    return m_locations.at(index);
}

int Constraint::get_nr_dirty() {
    int count = 0;
    for (Location* location : m_locations ) {
        if (location->is_dirty(m_direction)) {
            count++;
        }
    }
    return count;
}

void Constraint::clear_dirty() {
    for (Location* location : m_locations ) {
        location->clear_dirty(m_direction);
    }
}

int Constraint::get_variation() {
    int nr_of_white_segments = 0;
    int estimate_white_var = m_white_var;
    
    if (m_segments.size() ==0) {
        return 0;
    } else if (m_segments.size() < 3) {
        // only sement at begin and end
        return 1;
    }

    for (Segment *segment : m_segments) {
        if (segment->get_color() == white && !segment->is_locked()) {
            nr_of_white_segments++;
        }
    }

    if (nr_of_white_segments < 2) {
        return 1;
    }

    int white_sequence = 0;
    bool first_segment = true;
    for (int pos = 0; pos < m_locations.size();pos++) {
        if (m_locations[pos]->get_color() ==white) {
            white_sequence++;
        } else {
            
            if (first_segment && white_sequence > 0) {
                estimate_white_var -= white_sequence;
            } else if (white_sequence > 1) {
                estimate_white_var -= (white_sequence - 1);
            }
            first_segment =false;
            white_sequence = 0;
        }
    }
    if (white_sequence > 0 ) {
        estimate_white_var -= white_sequence;
    }

    if (estimate_white_var<0) {
        printf("ERROR: To many white space detected!: \n");
        print();
        estimate_white_var = 0;
    }

    int value = VarianceCalculator::getCalculator()->get_variance(nr_of_white_segments,estimate_white_var);
    if (value < 1) {
        value = MAX_VARIATION;
    }
    return value;
}

void Constraint::update_size() {
    int min_size = 0;
    m_size = m_locations.size();
    
    for (Segment *segment : m_segments) {
        min_size += segment->get_min_size();
    }

    m_white_var = m_size - min_size;
    for (Segment *segment : m_segments) {
        if (segment->get_color() == white) {
            segment->set_max_size(m_white_var + segment->get_min_size());
        }
    }
}

/*
Given a color, get the total number of locations that are expected to
have this color in the correct solution.
*/
int Constraint::get_colored_size(enum color for_color) {
    int count = 0;
    for (Segment *segment : m_segments) {
        if (for_color != white && segment->get_color() == for_color) {
            count +=segment->get_size();
        } else if (for_color == white && segment->get_color() != for_color) {
            count +=segment->get_size();
        } else {
            // no count needed, continue with next
        }
    }
    if (for_color == white) {
        return m_size - count;
    } 
    return count;
}

bool Constraint::is_valid() {
    if (m_white_var < 0) {
        return false;
    }
    return true;
}

bool Constraint::is_passed() {
    bool passed = true;
    bool foundFirst = false;
    bool all_filled = false;
    Segment *current_segment = m_segments.at(0);
    assert(current_segment != nullptr);
    Segment *next_segment = current_segment->get_after();
    assert(next_segment != nullptr);
    enum color current_color = no_color;
    int current_count = 0;

    for (int current_pos = 0; current_pos < m_locations.size(); current_pos++) {
        Location *location = m_locations.at(current_pos);
        enum color loc_color = location->get_color();
        if (loc_color != no_color) {
            if (current_pos == (m_locations.size() -1)) {
                all_filled = true;
            }
            if (!foundFirst) {
                if (loc_color == white) {
                    current_color = white;
                }
                foundFirst = true;
            }

            if (loc_color != current_color) {
                // check if count matches
                if ( !current_segment->is_size_allowed(current_count)) {
                    passed = false;
                    break;
                }

                //segment switch to next
                current_segment = next_segment;
                if (current_segment == nullptr) {
                    passed = false;
                    break;
                } else {
                    next_segment = current_segment->get_after();
                    current_color = loc_color;         
                    current_count = 1;
                }
            } else {
                // still in the same segment
                current_count++;
                if (
                    (current_color==white && !current_segment->is_size_allowed(current_count)) ||
                    (current_color!=white && current_count > current_segment->get_max_size())

                ) {   
                    passed = false;
                    break;
                }
            }

        } else {
            // check if remaining size is ok.
            int required_size = 0;
            if ( current_segment->get_min_size() < current_count) {
                required_size = (current_segment->get_min_size() - current_count);
            }
             
            while (next_segment != nullptr) {
                current_segment = next_segment;
                next_segment = current_segment->get_after();
                required_size += current_segment->get_min_size();
            }
            if (current_pos + required_size > m_size) {
                passed = false;
            }
            break;
        }
    }

    if (all_filled) {
        //must still check if we got to the last segment
        if ( current_segment != nullptr && !current_segment->is_size_allowed(current_count)) {
            passed = false;
        } else {
            if (
                current_segment != m_segments.back() && 
                current_segment != m_segments.back()->get_before()
            ) {
                passed = false;
            }
        }
    }
    return passed;
}

void Constraint::calculate_solutions() {
    std::vector<enum color> solution_base(m_size);
    Segment *current_segment = m_segments[0];
    m_solutions.clear();

    // special case if there are only two segments
    if (m_segments.size() == 2) {
        current_segment = m_segments[1];
    }

    if (m_white_var == SIZE_UNKNOWN) {
        update_size();
    }
    
    if (get_variation() > MAX_SOLUTIONS) {
        printf("ERROR: Contraint has more than the maximum variance (%d)",MAX_SOLUTIONS);
        print();
        std::__throw_domain_error("ERROR: Contraint has more than the maximum variance");
    }

    add_variation(
        &solution_base,
        0,
        current_segment,
        m_white_var
    );
}

void Constraint::add_variation(
    std::vector<enum color> *solution_base,
    int current_pos,
    Segment *current_segment,
    int variation_remaining
) {
   
    // add this segment to the solution
    int count = 0;
    while (count < current_segment->get_min_size()) {
        if (set_color(solution_base,current_pos,current_segment->get_color())) {
            current_pos++;
            count++;
        } else {
            return;
        }
    }

    Segment *next_segment = current_segment->get_after();
    if (next_segment!=nullptr) {
        add_variation(solution_base,current_pos,next_segment,variation_remaining); 
    } 

    if (current_segment->get_color() == white) {
        int var_count = 0;
        while (var_count < variation_remaining) {
            if (set_color(solution_base,current_pos,white)) {
                current_pos++;
                var_count++;
            } else {
                return;
            }
            if (next_segment!=nullptr) {
                add_variation(solution_base,current_pos,next_segment,(variation_remaining-var_count)); 
            } 
        }
        if (next_segment==nullptr) {
            assert(current_pos == m_size);
            m_solutions.push_back(std::vector<enum color>(*solution_base));
        } 
    }
}

bool Constraint::set_color(
    std::vector<enum color> *solution_base,
    int current_pos,
    enum color to_color
) {
    bool is_locked = m_locations[current_pos]->is_locked();
    if ( 
         !is_locked ||    
        ( is_locked && m_locations[current_pos]->get_color() == to_color)
    ) {
        solution_base->at(current_pos) = to_color;
        return true;
    } else {
        return false;
    }
}

int Constraint::get_solution_size() {
    return m_solutions.size();
}

void Constraint::set_solution(int solution_index) {
    assert(solution_index < m_solutions.size());
    int pos = 0;
    while (pos < m_locations.size()) {
        Location *location = m_locations.at(pos);
        if (!location->is_locked()) {
            location->set_color(m_solutions.at(solution_index).at(pos));
        } else {
            assert(m_solutions.at(solution_index).at(pos) == location->get_color());
        }
        pos++;
    }
}
void Constraint::reset_solution() {
    for (Location *location : m_locations) {
        location->soft_reset();
    }
}

void Constraint::set_location_color(const int pos, const enum color new_color) {
    if (pos <m_locations.size()) {
        m_locations[pos]->set_solved_color(new_color);
    }
}

void Constraint::calc_locks() {
    if (m_solutions.size()>0 && !m_locked) {
        std::vector<enum color>  common = m_solutions[0];
        int nr_in_common = m_size;
        int sol_idx = 1;
        while (sol_idx < m_solutions.size()) {
            nr_in_common = m_size;
            for (int pos = 0; pos < m_size;pos++) {
                if (common[pos] != no_color) {
                    if (common[pos] != m_solutions[sol_idx][pos]) {
                        nr_in_common--;
                        common[pos] = no_color;
                    }
                } else {
                    nr_in_common--;
                }
            }
            if (nr_in_common == 0) {
                break;
            }
            sol_idx++;
        }

        if (nr_in_common > 0) {
            int nr_locked = 0;
            for (int pos = 0; pos < m_size;pos++) {
                if (common[pos] != no_color) {
                    set_location_color(pos,common[pos]);
                }
                if (m_locations[pos]->is_locked()) {
                    nr_locked++;
                }
            }
            if (nr_locked == m_size) {
                m_locked = true;
            }
        }
    }
}

void Constraint::calc_locks_rules() {
    if (m_Rule == nullptr) {
        m_Rule = new Rule(this);
    }
    bool first = true;
    while (get_nr_dirty() > 0  || first) {
        clear_dirty();
        m_Rule->calc_locks();
        first = false;
    }
}

int Constraint::reduce_solutions() {
    int nr_reduced = 0;

    if (m_solutions.size() > 1) {
        for (int pos = 0; pos < m_size;pos++) {
            
            if (m_locations[pos]->is_locked()) {
                nr_reduced += reduce_sol(pos,m_locations[pos]->get_color());
            }
            if (m_solutions.size() == 1) {
                break;
            }
        }
    }

    return nr_reduced;
}

int Constraint::reduce_sol(int pos, enum color required_color) {
    int nr_reduced = 0;
    if (m_solutions.size() > 1) {
        for (int i = 0; i < m_solutions.size();i++) {
            if(m_solutions.at(i).size() > 0 && m_solutions.at(i).at(pos) != required_color) { 
                nr_reduced++;
                // to slow :-(
                //it = m_solutions.erase(it);
                m_solutions.at(i).clear();
            }
        }
    }

    if (nr_reduced > 0) {
        std::vector<std::vector<enum color>> result;
        for (int i = 0; i < m_solutions.size();i++) {
            if( m_solutions.at(i).size() != 0) {
                result.push_back(m_solutions.at(i));
            }
        }
        m_solutions.clear();
        m_solutions = result;
    }

    return nr_reduced;
}

void Constraint::print_solution(std::vector<enum color> *solution_base,int max_pos) {

    if (max_pos < 0) {
        max_pos = solution_base->size();
    }
    printf("\"");
    for (int i =0; i < max_pos;i++) {
        enum color cur_color = solution_base->at(i);
        if (cur_color == no_color) {
            printf("U");
        } else if (cur_color == black) {
            printf("X");
        } else if (cur_color == white){
            printf(" ");
        } else {
            printf("O");
        }
    }
    printf("\"\n");
}

static char to_letter(int i) {
    char seg_char = '.';
    if (i>=0 && i<26) {
        seg_char = (char) (i + 65);
    } else if (i>=26 && i<52) {
        seg_char = (char) (i + 97);
    } else {
        seg_char = '.';
    }
    return seg_char;
}

void Constraint::debug_dump() {
    printf("Start dump of: ");
    print();
    printf("Solutions are:\n");
    for (int i = 0; i < m_solutions.size();i++) {
        print_solution(&(m_solutions[i]));
    }

    printf("End of dump of ");
    print();
}

std::string Constraint::clue_string(){
    std::stringstream str_str;
    bool first = true;
    for(std::vector<Segment*>::iterator it = m_segments.begin(); it != m_segments.end(); ++it) {
        if ((*it)->get_color() == black) {
            if (!first) {
                str_str << ",";
            }
            first =false;
            str_str << (*it)->get_size() ;
        }
    }
    return str_str.str();
}

std::string Constraint::loc_string(){
    std::stringstream str_str;
    int pos = 0;
    while (pos < m_locations.size()) {
        Location *location = m_locations.at(pos);
        str_str << location->to_string();
        pos++;
    }
    return str_str.str();
}

std::string Constraint::loc_dirty_string(){
    std::stringstream str_str;
    int pos = 0;
    while (pos < m_locations.size()) {
        Location *location = m_locations.at(pos);
        if (location->is_dirty(m_direction)) {
            str_str << "D";
        } else {
            str_str << "C";
        }
        pos++;
    }
    return str_str.str();
}

std::string Constraint::loc_seg_string(){
    std::stringstream str_str;
    int pos = 0;
    while (pos < m_locations.size()) {
        Location *location = m_locations.at(pos);
        str_str << location->has_segment_for_dir(m_direction);
        pos++;
    }
    return str_str.str();
}

std::string Constraint::loc_seg_locked_string(){
    std::stringstream str_str;
    int pos = 0;
    pos = 0;
    while (pos < m_locations.size()) {
        Location *location = m_locations.at(pos);
        bool seg_locked = false;
        if (location->has_segment_for_dir(m_direction)) {
            Segment *cur_segment = location->get_segment_for_dir(m_direction);
            seg_locked = cur_segment->is_locked();
        }
        if (seg_locked) {
            str_str << "L";
        } else {
            str_str << "F";
        }
        pos++;
    }
    return str_str.str();
}

std::string Constraint::seg_string(){
    std::stringstream str_str;
    std::string head_tail = "   ";
    str_str << "\n***\n";
    for(int i = 0; i< m_segments.size();i++) {
        str_str << to_letter(i);
        if (m_segments[i]->get_color() != white) {
            str_str << m_segments[i]->get_min_size();
        }
        if (i!=m_segments.size()-1) {
            str_str << "-";
        }
    }
    str_str << "\n";
    str_str << "<UN0123";
    for (int pos = 7; pos <m_size + 3;pos++) {
        str_str << "." ;
    }
    str_str << "NU>\n" ;
    str_str << head_tail << loc_string()            << head_tail << "\n";
    str_str << head_tail << loc_seg_string()        << head_tail << "\n";
    str_str << head_tail << loc_seg_locked_string() << head_tail << "\n";
    str_str << head_tail << loc_dirty_string()      << head_tail << "\n";
 
    for(int i = 0; i< m_segments.size();i++) {
        int start = m_segments[i]->get_min_start();
        int end = m_segments[i]->get_max_end();
        char seg_char = to_letter(i);

        if (start < -2) {
            start = -3;
        }
        if (end < 0) {
            if (end == POS_NA || end == POS_UNKNOWN) {
                if (i==0 && m_segments[1]->get_color()!=white && m_segments[1]->get_start() == 0) {
                    end = start;
                } else {
                    end = (m_size - 1) + (-end);
                }
            } else {
                end = (m_size - 1) + 3;
            }
        }
        for (int pos = -3; pos <start;pos++) {
            str_str << " " ;
        }
        for (int pos = start; pos <=end;pos++) {
            str_str << seg_char ;
        }
        for (int pos = end +1; pos < m_size + 3;pos++) {
            str_str << " " ;
        }
        str_str << "\n";
    }
    str_str << "***\n";
    return str_str.str();
}

std::string Constraint::to_string() {
    std::stringstream str_str;
    if (m_direction == x_dir) {
        str_str << "X: ";
    } else {
        str_str << "Y: ";
    }

    str_str << clue_string();
    str_str << " ";
    str_str << loc_string();

    return str_str.str();
}

void Constraint::print() {
    std::cout << to_string();
    printf("\n");
}

void Constraint::print_seg() {
    std::cout << seg_string();
}

Constraint::~Constraint() {

    m_segments.clear();

    if (m_Rule != nullptr) {
        delete m_Rule;
    }
    
    // locations are not owned here
    m_locations.clear();
    return;
}
