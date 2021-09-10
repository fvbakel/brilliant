#ifndef _PIECE_H
#define _PIECE_H	1

#include <constants.h>
#include <vector>

class Piece {
    private:
        enum color m_color = white;

    public:
        Piece(const enum color current_color);
        ~Piece();

    enum color get_color();
};

typedef std::vector<Piece*>    pieces;

#endif