#include <Piece.h>
#include <stdio.h>

Piece::Piece(const int x,const int y,const enum color current_color) {
    m_x = x;
    m_y = y;
    m_color = current_color;
}

Piece::~Piece() {
    
}
