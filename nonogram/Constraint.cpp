#include <stdio.h>
#include <cstdlib>



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
}

int Constraint::get_max_size() {
    return m_max_size;
}
void Constraint::set_max_size(const int size) {
    m_max_size = size;
}

bool Constraint::is_passed() {
    bool passed = true;
    bool foundFirst = false;
    Segment *current_segment = m_segments.at(0);
    Segment *next_segment = current_segment->get_after();
    enum color current_color = no_color;
    int current_count = 0;
    int current_pos = -1;
    for (Location *location : m_locations) {
        current_pos++;
        Piece *piece = location->get_piece();
        if (piece != nullptr) {
            enum color piece_color = piece->get_color();
            if (!foundFirst) {
                if (piece_color == white) {
                    current_color = white;
                }
                foundFirst = true;
            }

            if (piece_color == no_color) {
                passed = false;
                break;
            } else if (piece_color != current_color) {
                // check if count matches
                if ( current_segment->is_size_allowed(current_count)) {
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
                    current_color = piece->get_color();
                    current_count = 0;
                }
            } else {
                // still in the same segment
                current_count++;
                if ( current_segment->is_size_allowed(current_count)) {
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
            
            if (current_pos + required_size >m_max_size) {
                passed = false;
            }
            break;
        }
    }
    return passed;
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