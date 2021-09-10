#ifndef _CONSTRAINT_H
#define _CONSTRAINT_H	1

#include <vector>

#include <constants.h>
#include <Piece.h>
#include <Segment.h>


class Constraint {
    private:
        enum direction      m_direction    = x_dir;
        int                 m_min_size     = SIZE_UNKNOWN;
        segments            m_segments;

    public:
        Constraint(enum direction direction,std::vector<int> *blacks);
        ~Constraint();
};

typedef std::vector<Constraint*>    constraints;

#endif