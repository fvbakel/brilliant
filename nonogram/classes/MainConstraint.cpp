#include <MainConstraint.h>
#include <stdio.h>

MainConstraint::MainConstraint(enum direction direction,std::vector<int> *blacks)  : Constraint(direction) {
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



MainConstraint::~MainConstraint() {

    for (Segment* segment : m_segments) {
        delete segment;
    }

}