#include <stdio.h>
#include <cstdlib>
#include <assert.h>


#include <Constraint.h>

Constraint::Constraint(enum direction direction,std::vector<int> *blacks) {
    
    m_direction = direction;
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
        printf("ERROR, one or more black fields are required!\n");
    }
}

void Constraint::add_location(Location *location) {
    m_locations.push_back(location);
    update_size();
}

int Constraint::get_size() {
    return m_size;
}

int Constraint::get_white_var() {
    return m_white_var;
}

void Constraint::update_size() {
    int min_size = 0;
    int max_white_size = 0;
    m_size = m_locations.size();
    
    for (Segment *segment : m_segments) {
        min_size += segment->get_min_size();
    }

    m_white_var = m_size - min_size;
    max_white_size = 1 + m_white_var;

    for (Segment *segment : m_segments) {
        if (segment->get_color() == white) {
            segment->set_max_size(max_white_size);
        }
    }
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
        //printf("Getting location %d\n",current_pos);
        Location *location = m_locations.at(current_pos);
        enum color loc_color = location->get_color();
        if (loc_color != no_color) {
    /*        if (loc_color==black) {
                printf("loc_color= black\n");
            } else {
                printf("loc_color!= black\n");
            }
    */
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
        /*        printf("Segment switch\n");
                if (current_color==black) {
                    printf("current_color= black\n");
                } else {
                    printf("current_color!= black\n");
                }
        */
                // check if count matches
                if ( !current_segment->is_size_allowed(current_count)) {
            //        printf("Not Ok because exceed segment size in switch. current_count=%d, min_size=%d, max_size=%d\n",current_count,current_segment->get_min_size(),current_segment->get_max_size());
                    passed = false;
                    break;
                }

                //segment switch to next
                current_segment = next_segment;
                if (current_segment == nullptr) {
                    passed = false;
                    break;
                } else {
    //                printf("getting new next segment\n");
                    next_segment = current_segment->get_after();
                    current_color = loc_color;
    /*                if (current_color==black) {
                        printf("current segment current_color= black\n");
                    } else {
                        printf("current segment current_color!= black\n");
                    }
    */            
                    current_count = 1;
                }
            } else {
                // still in the same segment
                current_count++;
            /*    if (current_segment->get_color()==black) {
                    printf("current segment color= black\n");
                } else {
                    printf("current segment color!= black\n");
                }
            */
                if (
                    (current_color==white && !current_segment->is_size_allowed(current_count)) ||
                    (current_color!=white && current_count > current_segment->get_max_size())

                ) {
                /*    if (current_color==black) {
                        printf("current_color= black\n");
                    } else {
                        printf("current_color!= black\n");
                    }
                    
                    printf("current_count=%d\n",current_count);
                    printf("current_segment->get_min_size=%d\n",current_segment->get_min_size());
                    printf("current_segment->get_max_size=%d\n",current_segment->get_max_size());
                    printf("Not Ok because exceed segment size in same segment\n");
                */    
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
    //            printf("Not Ok because can not meet size\n");
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
    m_solutions.clear();

    if (m_white_var == SIZE_UNKNOWN) {
        update_size();
    }

    print();
    std::vector<enum color> solution_base(m_size);
    add_variation(
        &solution_base,
        0,
        m_segments[0],
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
        solution_base->at(current_pos) = current_segment->get_color();
        current_pos++;
        count++;
    }

    Segment *next_segment = current_segment->get_after();
    if (next_segment!=nullptr) {
        add_variation(solution_base,current_pos,next_segment,variation_remaining); 
    } 

    if (current_segment->get_color() == white) {
        int var_count = 0;
        while (var_count < variation_remaining) {
            solution_base->at(current_pos) = white;
            current_pos++;
            var_count++;
            if (next_segment!=nullptr) {
                add_variation(solution_base,current_pos,next_segment,(variation_remaining-var_count)); 
            } 
        }
        if (next_segment==nullptr) {
       //     printf("Adding solution: ");
       //     print_solution(solution_base);
            assert(current_pos == m_size);
            m_solutions.push_back(std::vector<enum color>(*solution_base));
        } 
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
        location->set_color(m_solutions.at(solution_index).at(pos));
        pos++;
    }

}
void Constraint::reset_solution() {
    for (Location *location : m_locations) {
        location->set_color(no_color);
    }
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