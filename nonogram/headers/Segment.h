#ifndef _SEGMENT_H
#define _SEGMENT_H	1

#include <constants.h>
#include <Piece.h>
#include <vector>

class Segment {
    private:
        enum color      m_color        = white;
        enum direction  m_direction    = x_dir;
        int             m_min_size     = SIZE_UNKNOWN;
        int             m_max_size     = SIZE_UNKNOWN;
        int             m_size         = SIZE_UNKNOWN;
        Piece         **m_pieces       = nullptr;
        Segment        *m_before       = nullptr;
        Segment        *m_after        = nullptr;
        
    public:
        Segment();
        Segment(
            const enum color      color,
            const enum direction  direction,
            const int             min_size
        );
        ~Segment();

        void set_min_size(const int min_size);
        int get_min_size();

        int get_max_size();
        int get_size();
        enum color get_color();

        void set_before(Segment *before);
        Segment *get_before();

        void set_after(Segment *after);
        Segment *get_after();
};

typedef std::vector<Segment*>    segments;

#endif /* <Segment.h> included.  */
