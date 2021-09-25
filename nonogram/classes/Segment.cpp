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

int Segment::get_min_start() {
    return m_min_start;
}
void Segment::set_min_start(const int min_start) {
    m_min_start = min_start;
}
int Segment::get_start() {
    return m_start;
}
void Segment::set_start(const int start) {
    m_start = start;
}
int Segment::get_max_end() {
    return m_max_end;
}
void Segment::set_max_end(const int max_end) {
    m_max_end = max_end;
}
int Segment::get_end() {
    return m_end;
}
void Segment::set_end(const int end) {
    m_end = end;
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

Segment::~Segment() {
    return;
}
