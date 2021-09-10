#ifndef _PIECE_H
#define _PIECE_H	1

#include <constants.h>
#include <vector>

class Piece {
    private:
        int m_x = 0;
        int m_y = 0;
        enum color m_color = white;

    public:
        Piece(const int x,const int y,const enum color current_color);
        ~Piece();
};

typedef std::vector<Piece*>    pieces;

#endif