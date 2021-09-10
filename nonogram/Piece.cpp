#include <Piece.h>
#include <stdio.h>

Piece::Piece(const enum color current_color) {
    m_color = current_color;
}

enum color Piece::get_color() {
    return m_color;
}

Piece::~Piece() {
    
}
