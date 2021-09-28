#include <Segment.h>
#include <stdio.h>

Segment::Segment(
    const enum color      color,
    const enum direction  direction,
    const int             min_size
) {
    m_color     = color;
    m_direction = direction;
    m_min_size  = min_size;
    if (color == black) {
        m_max_size = min_size;
        m_size = min_size;
    } 
}

void Segment::set_min_size(const int min_size) {
    m_min_size = min_size;
    update_other_size();
}
int Segment::get_min_size() {
    return m_min_size;
}

void Segment::set_max_size(const int max_size) {
    m_max_size =max_size;
    update_other_size();
}

void Segment::update_other_size() {
    if (m_color == white) {
        if (m_min_size == m_max_size) {
            m_size = m_min_size;
        }
    }
}

int Segment::get_max_size() {
    return m_max_size;
}
int Segment::get_size() {
    return m_size;
}
enum color Segment::get_color() {
    return m_color;
}

void Segment::set_before(Segment *before) {
    m_before = before;
    if (before != nullptr) {
        if (before->get_after() != this) {
            before->set_after(this);
        }
    }
}

Segment* Segment::get_before() {
    return m_before;
}

void Segment::set_after(Segment *after) {
    m_after = after;
    if (after != nullptr) {
        if (after->get_before() != this) {
            after->set_before(this);
        }
    }
}
Segment* Segment::get_after() {
    return m_after;
}

void Segment::lock() {
    m_locked = true;
}
void Segment::unlock() {
    m_locked = false;
}
bool Segment::is_locked() {
    return m_locked;
}

int Segment::get_max_start() {
    if (m_max_end == POS_NA) {
        return POS_NA;
    }
    return m_max_end - (m_min_size -1) ;
}
int Segment::get_min_end() {
    if (m_min_start == POS_NA) {
        return POS_NA;
    }
    return m_min_start + (m_min_size -1) ;
}

int Segment::get_min_start() {
    return m_min_start;
}
void Segment::set_min_start(const int min_start) {
    if (    m_min_start!=POS_UNKNOWN &&
            min_start!=POS_NA &&
            min_start <=m_min_start
    ) {
        return;
    }
    m_min_start = min_start;
    
    int min_start_next = min_start + m_min_size;
    if (min_start == POS_NA && m_before == nullptr) {
        min_start_next += -(POS_NA) ;
    }
    if(m_after != nullptr) {
        m_after->set_min_start(min_start_next);
    }
}
int Segment::get_start() {
    return m_start;
}
void Segment::set_start(const int start) {
    if (start < 0) {
        return;
    } else {    
        m_start = start;
        if (m_color != white) {
            m_end = m_start + m_size;
            m_after->set_start(m_end + 1);
            m_before->set_end(m_start -1);
        }
    }
}
int Segment::get_max_end() {
    return m_max_end;
}
void Segment::set_max_end(const int max_end) {
    if (    m_max_end!=POS_UNKNOWN &&
            max_end!=POS_NA &&
            max_end >=m_max_end
    ) {
        return;
    }
    m_max_end = max_end;
    int max_end_next = max_end - m_min_size;
    if (max_end != POS_NA && m_after != nullptr && m_before != nullptr) {
        m_before->set_max_end(max_end_next);
    }
}
int Segment::get_end() {
    return m_end;
}
void Segment::set_end(const int end) {
    m_end = end;
    if (m_color != white) {
        m_start = m_end - m_size;
        m_before->set_end(m_start - 1);
        m_after->set_start(m_end + 1);
    }
}
        
void Segment::reset() {
    if (m_color == white) {
        m_size          = SIZE_UNKNOWN;
        m_max_size      = SIZE_UNKNOWN;
        m_min_start     = POS_UNKNOWN;
        m_start         = POS_UNKNOWN;
        m_max_end       = POS_UNKNOWN;
        m_end           = POS_UNKNOWN;
    }
}

bool Segment::is_size_allowed(const int size) {
     return (size >= m_min_size) && (size <= m_max_size);
}

void Segment::print() {
    if (m_before != nullptr) {
        printf("--");
    }
    if (m_color == white) {
        printf("W");
    } else {
        printf("B");
    }
    printf("%d(%d,%d) locked=%d \n",m_min_size,m_start,m_end,m_locked);

    printf("m_min_size=%d\n",m_min_size);
    printf("m_min_start=%d\n",m_min_start);
    printf("max_start=%d\n",get_max_start());
    printf("m_max_end=%d\n",m_max_end);
    printf("min_end=%d\n",get_min_end());
    
    if (m_after != nullptr) {
        printf("--\n");
    }

}

Segment::~Segment() {
    return;
}
