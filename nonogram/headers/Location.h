#ifndef _LOCATION_H
#define _LOCATION_H	1

#include <vector>

#include <Piece.h>

class Location {
    private:
        int     m_x         = 0;
        int     m_y         = 0;
        Piece  *m_piece     = nullptr;

    public:
        Location(const int x,const int y);
        ~Location();

        int get_x();
        void set_x(const int x);

        int get_y();
        void set_y(const int y);

        Piece *get_piece();
        void set_piece(Piece *piece);

        bool isSolved();

};

typedef std::vector<Location*>    locations;

#endif