#include <Location.h>

Location::Location(const int x,const int y) {
    m_x = x;
    m_y = y;
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

Piece* Location::get_piece() {
    return m_piece;
}
void Location::set_piece(Piece *piece) {
    m_piece = piece;
}

bool Location::is_solved() {
    return m_piece != nullptr;
}

Location::~Location() {
    return;
}
