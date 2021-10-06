#include <Segment.h>
#include <stdio.h>
#include <sstream>

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

enum direction Segment::get_direction() {
    return m_direction;
}

void Segment::set_limit(const int limit) {
    if (m_after == nullptr) {
        m_limit = limit;
    }
}
int Segment::get_limit() {
    return m_limit;
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
    if ( !  ((m_min_start == POS_UNKNOWN && min_start == POS_NA) ||
            (m_min_start < 0 && min_start >=0)                   ||
            (min_start > m_min_start))
    ) {    
        return;
    }

    m_min_start = min_start;
    update_if_one_solution();
    int min_start_next = min_start + m_min_size;
    if (min_start == POS_NA && m_before == nullptr) {
        min_start_next += -(POS_NA) ;
    }
    if(m_after != nullptr) {
        m_after->set_min_start(min_start_next);
    }
    error_check();
}
int Segment::get_start() {
    return m_start;
}
void Segment::set_start(const int start) {
    if (start < 0) {
        return;
    } else {    
        m_start = start;
        set_min_start(start);
        if (m_color != white) {
            m_end = m_start + (m_size -1) ;
            set_max_end(m_end);
            m_after->set_start(m_end + 1);
            m_before->set_end(m_start -1);
        }
    }
    if (m_after == nullptr && m_color == white && m_start >=0 ) {
        if (m_start >m_limit) {
            // This segment does not exists
            set_end(m_limit +1);
            lock();
        } else {
            set_end(m_limit);
        }
    }
    error_check();
}
int Segment::get_max_end() {
    return m_max_end;
}
void Segment::set_max_end(const int max_end) {
    if ( !( 
           ( m_max_end == POS_UNKNOWN && max_end == POS_NA ) ||
           ( (m_max_end == POS_UNKNOWN || m_max_end == POS_NA)  && max_end >= 0) ||
           ( m_max_end > max_end && m_max_end >= 0)
        )
    ) {
        return;
    }
    m_max_end = max_end;
    update_if_one_solution();
    int max_end_next = max_end - m_min_size;
    if (max_end != POS_NA && m_after != nullptr && m_before != nullptr) {
        m_before->set_max_end(max_end_next);
    }
    error_check();
}
int Segment::get_end() {
    return m_end;
}
void Segment::set_end(const int end) {
    m_end = end;
    set_max_end(end);
    if (m_color != white) {
        m_start = m_end - (m_size - 1);
        set_min_start(m_start);
        m_before->set_end(m_start - 1);
        m_after->set_start(m_end + 1);
    }
    if (m_before == nullptr && m_color == white && m_end >=0) {
        set_start(0);
    }

    error_check();
}

void Segment::update_if_one_solution() {
    if (m_locked) {
        return;
    } else if (is_start_and_end_set()) {
        return;
    } else {
        int possible_size = m_max_end - m_min_start + 1;
        if (    m_min_start   != POS_NA       &&
                m_min_start   != POS_UNKNOWN  &&
                m_max_end     != POS_NA       &&
                m_max_end     != POS_UNKNOWN  &&
                possible_size == m_min_size
        ) {
            if (!is_start_set()) {
                set_start(m_min_start);
            }
            if (!is_end_set()) {
                set_end(m_max_end);
            }
        }
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

bool Segment::is_start_set() {
    return (m_start != POS_UNKNOWN) && (m_start   != POS_NA);
}
bool Segment::is_end_set() {
    return (m_end != POS_UNKNOWN) && (m_end   != POS_NA);
}
bool Segment::is_start_and_end_set() {
    return is_start_set() && is_end_set();
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

void Segment::error_check() {
    bool passed =true;
    std::stringstream error_str;

    if ( m_start != POS_NA &&
         m_start != POS_UNKNOWN &&
         m_end   != POS_NA &&
         m_end   != POS_UNKNOWN &&
         m_start > m_end
    ) {
        error_str << "m_start=" << m_start <<" larger than m_end=" << m_end << "\n";
        passed =false;
    }
    if ( m_min_start != POS_NA &&
         m_min_start != POS_UNKNOWN &&
         m_max_end   != POS_NA &&
         m_max_end   != POS_UNKNOWN &&
         m_min_start > get_max_start()
    ) {
        error_str << "m_min_start=" << m_min_start <<" larger than max_start=" << get_max_start() << "\n";
        passed =false;
    }
    if ( m_min_start != POS_NA &&
         m_min_start != POS_UNKNOWN &&
         m_start     != POS_NA &&
         m_start     != POS_UNKNOWN &&
         m_min_start > m_start
    ) {
        error_str << "m_min_start=" << m_min_start <<" larger than m_start=" << m_start << "\n";
        passed =false;
    }
    if ( m_max_end != POS_NA &&
         m_max_end != POS_UNKNOWN &&
         m_end     != POS_NA &&
         m_end     != POS_UNKNOWN &&
         m_max_end >  m_end
    ) {
        error_str << "m_max_end=" << m_max_end <<" larger than m_end=" << m_end << "\n";
        passed =false;
    }

    if (!passed) {
        std::__throw_runtime_error(error_str.str().c_str());
    }
}

Segment::~Segment() {
    return;
}
