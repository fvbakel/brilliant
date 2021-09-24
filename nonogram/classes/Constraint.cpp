#include <stdio.h>
#include <cstdlib>
#include <assert.h>
#include <cmath>

#include <Constraint.h>
#include <VarianceCalculator.h>

Constraint::Constraint(enum direction direction,std::vector<int> *blacks) {
    
    m_direction = direction;
    m_locked = false;
    if (blacks != nullptr) {
        int nr_blacks = blacks->size();
        m_segments.push_back(new Segment(white,m_direction,0));
        Segment* end_segment = new Segment(white,m_direction,0);
        Segment *segment_last = m_segments[0];

        int i = 0;
        while (i < nr_blacks) {
            Segment *segment_black = new Segment(black,m_direction,blacks->at(i));
            m_segments.push_back(segment_black);
            segment_last->set_after(segment_black);
            segment_last = segment_black;
            if ((i + 1) != nr_blacks) {
                Segment *segment_white = new Segment(white,m_direction,1);
                m_segments.push_back(segment_white);
                segment_last->set_after(segment_white);
                segment_last = segment_white;
            }
            i++;
        }
        segment_last->set_after(end_segment);
        m_segments.push_back(end_segment);

    } else {
        printf("ERROR, parameter blacks can not be null\n");
    }
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
        if (segment->get_color() == white) {
            nr_of_white_segments++;
        }
    }
    assert(nr_of_white_segments > 1);

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
    if (white_sequence > 0) {
        estimate_white_var -= white_sequence;
    }

    int value = VarianceCalculator::getCalculator()->get_variance(nr_of_white_segments,estimate_white_var);
    if (value < 1) {
        printf("WARNING: To many or no variation for: \n");
        print();
        value = (int) pow(2,( (8 * sizeof(int) ) -1 ));
        printf("WARNING: falling back to %d \n",value);        
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

void Constraint::calc_locks(std::unordered_set<int>  *affected) {
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
                    if (!m_locations[pos]->is_locked()) {
                        m_locations[pos]->set_color(common[pos]);
                        m_locations[pos]->lock();
                        affected->insert(pos);
                    }
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

void Constraint::print() {
    if (m_direction == x_dir) {
        printf("X: ");
    } else {
        printf("Y: ");
    }

    for(std::vector<Segment*>::iterator it = m_segments.begin(); it != m_segments.end(); ++it) {
        if ((*it)->get_color() == black) {
            printf("%d ",  (*it)->get_size());
        }
    }

    int pos = 0;
    while (pos < m_locations.size()) {
        Location *location = m_locations.at(pos);
        location->print();
        pos++;
    }
    printf("\n");
    
}

Constraint::~Constraint() {

    for (Segment* segment : m_segments) {
        delete segment;
    }
    m_segments.clear();

    // locations are not owned here
    m_locations.clear();
    return;
}
