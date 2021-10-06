#ifndef _SEGMENT_H
#define _SEGMENT_H	1

#include <constants.h>
#include <vector>

class Segment {
    private:
        enum color      m_color        = white;
        enum direction  m_direction    = x_dir;
        int             m_min_size     = SIZE_UNKNOWN;
        int             m_max_size     = SIZE_UNKNOWN;
        int             m_size         = SIZE_UNKNOWN;
        bool            m_locked       = false;
        int             m_min_start    = POS_UNKNOWN;
        int             m_start        = POS_UNKNOWN;
        int             m_max_end      = POS_UNKNOWN;
        int             m_end          = POS_UNKNOWN;
        int             m_limit        = POS_UNKNOWN;

        Segment        *m_before       = nullptr;
        Segment        *m_after        = nullptr;

        void update_if_one_solution();
        
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

        void set_max_size(const int max_size);
        int get_max_size();
        int get_size();
        enum color get_color();
        enum direction get_direction();
        void set_limit(const int limit);
        int get_limit();

        void update_other_size();

        int get_max_start();
        int get_min_end();

        void lock();
        void unlock();
        bool is_locked();

        int get_min_start();
        void set_min_start(const int min_start);
        int get_start();
        void set_start(const int start);
        int get_max_end();
        void set_max_end(const int max_end);
        int get_end();
        void set_end(const int end);
        
        void reset();

        void set_before(Segment *before);
        Segment *get_before();

        void set_after(Segment *after);
        Segment *get_after();

        bool is_size_allowed(const int size);
        bool is_start_set();
        bool is_end_set();
        bool is_start_and_end_set();

        void print();
        void error_check();
};

typedef std::vector<Segment*>    segments;

#endif /* <Segment.h> included.  */
