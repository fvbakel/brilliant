#include <Location.h>
#include <stdio.h>
#include <iostream>
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

void Location::determine_color(enum color new_color) {
    if (!is_locked()) {
        set_color(new_color);
        set_dirty_both();
        lock();
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
