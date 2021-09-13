#include <Location.h>
#include <stdio.h>

Location::Location(const int x,const int y) {
    m_x     = x;
    m_y     = y;
    m_color = no_color;
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
    m_color = new_color;
}

bool Location::is_solved() {
    return (m_color != no_color);
}

void Location::print() {
    if (m_color == no_color) {
        printf("U");
    } else if (m_color == black) {
        printf("X");
    } else {
        printf(" ");
    }
}

Location::~Location() {
    return;
}
