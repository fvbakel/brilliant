#include <Location.h>
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <assert.h>

Location::Location(const int x,const int y) {
    m_x      = x;
    m_y      = y;
    m_color  = no_color;
    m_locked = false;
 }

int Location::get_x() {
    return m_x;
}
void Location::set_x(const int x) {
    m_x = x;
}

int Location::get_y() {
    return m_y;
}
void Location::set_y(const int y) {
    m_y = y;
}

enum color Location::get_color() {
    return m_color;
}
void Location::set_color(enum color new_color) {
    assert(m_locked == false);
    m_color = new_color;
}

Segment **Location::get_segment_pointer_for_dir(enum direction for_dir) {
    Segment **p_segment = &m_segment_x;
    if (for_dir == y_dir) {
        p_segment = &m_segment_y;
    } 
    return p_segment;
}

Segment *Location::get_segment_for_dir(enum direction for_dir) {
    Segment **p_segment = get_segment_pointer_for_dir(for_dir);
    return (*p_segment);
}

void Location::set_segment(Segment *segment) {
    Segment **p_segment = get_segment_pointer_for_dir(segment->get_direction());
    if (*p_segment != segment) {
        if (*p_segment != nullptr) {
            printf("ERROR: Setting location to two different segments. Was: ");
            (*p_segment)->print(); 
            printf("Now: ");
            segment->print();
            printf("\n");
            throw std::runtime_error("Setting location to two different segments");
        }
        // now dirty location for this direction, because segment was not known
        set_dirty(segment->get_direction());
        *p_segment = segment;
        set_solved_color(segment->get_color());
    }
}

bool Location::has_segment_for_dir(enum direction for_dir) {
    Segment *segment = get_segment_for_dir(for_dir);
    return segment != nullptr;
}
bool Location::is_part_of_segment(Segment *segment) {
    Segment *my_segment = get_segment_for_dir(segment->get_direction());
    return my_segment == segment;
}

void Location::error_check() {
    bool passed =true;
    std::stringstream error_str;
    if (m_segment_x != nullptr && m_segment_x->get_color() != m_color) {
        error_str << "ERROR: Location color(" << m_color;
        error_str << ") does not match x segment color(" << m_segment_x->get_color() << "\n";
        passed = false;
    }
    if (m_segment_y != nullptr && m_segment_y->get_color() != m_color) {
        error_str << "ERROR: Location color(" << m_color;
        error_str << ") does not match y segment color(" << m_segment_y->get_color() << "\n";
        passed = false;
    }
    if (m_segment_y != nullptr && m_segment_x != nullptr && m_segment_x->get_color() != m_segment_y->get_color()) {
        error_str << "ERROR: Segment x color(" << m_color;
        error_str << ") does not match y segment color(" << m_segment_y->get_color() << "\n";
        passed = false;
    }
    if (!passed) {
        throw std::runtime_error(error_str.str());
    }
}

void Location::set_solved_color(enum color new_color) {
    if (!is_locked()) {
        set_color(new_color);
        set_dirty_both();
        lock();
        error_check();
    }
}

bool Location::is_locked() {
    return m_locked;
}

void Location::lock() {
    assert(m_color != no_color);
    m_locked = true;
}
void Location::unlock() {
    m_locked = false;
}

void Location::soft_reset() {
    if (!m_locked) {
        m_color = no_color;
    }
}
void Location::hard_reset() {
    m_color     = no_color;
    m_locked    = false;
    m_dirty_x   = false;
    m_dirty_y   = false;
}

void Location::set_dirty_both() {
    m_dirty_x   = true;
    m_dirty_y   = true;
}
void Location::clear_dirty_both() {
    m_dirty_x   = false;
    m_dirty_y   = false;
}
bool Location::is_dirty_any_dir() {
    return m_dirty_x || m_dirty_y;
}
void Location::set_dirty(enum direction for_dir) {
    if (for_dir == x_dir) {
        m_dirty_x   = true;
    } else {
        m_dirty_y   = true;
    }
}
void Location::clear_dirty(enum direction for_dir) {
    if (for_dir == x_dir) {
        m_dirty_x   = false;
    } else {
        m_dirty_y   = false;
    }
}
bool Location::is_dirty(enum direction for_dir) {
    if (for_dir == x_dir) {
        return m_dirty_x;
    } else {
        return m_dirty_y;
    }
}

bool Location::is_solved() {
    return (m_color != no_color);
}

std::string Location::to_string() {
        if (m_color == no_color) {
        return "U";
    } else if (m_color == black) {
        return "X";
    } else {
        return " ";
    }
}

void Location::print() {
    std::cout << to_string();
}

Location::~Location() {
    return;
}
