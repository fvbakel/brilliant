#ifndef _LOCATION_H
#define _LOCATION_H	1

#include <vector>
#include <string>
#include <constants.h>
#include <Segment.h>


class Location {
    private:
        int         m_x         = 0;
        int         m_y         = 0;
        enum color  m_color     = no_color;
        bool        m_locked    = false;
        bool        m_dirty_x   = false;
        bool        m_dirty_y   = false;
        Segment    *m_segment_x = nullptr;
        Segment    *m_segment_y = nullptr;

        Segment **get_segment_pointer_for_dir(enum direction for_dir);
        void error_check();

    public:
        Location(const int x,const int y);
        ~Location();

        int get_x();
        void set_x(const int x);

        int get_y();
        void set_y(const int y);

        enum color get_color();
        void set_color(enum color);
        void set_solved_color(enum color new_color);
        
        void set_segment(Segment *segment);
        
        Segment *get_segment_for_dir(enum direction for_dir);
        bool has_segment_for_dir(enum direction for_dir);
        bool is_part_of_segment(Segment *segment);

        bool is_locked();
        void lock();
        void unlock();

        void soft_reset();
        void hard_reset();

        void set_dirty_both();
        void clear_dirty_both();
        bool is_dirty_any_dir();
        void set_dirty(enum direction for_dir);
        void clear_dirty(enum direction for_dir);
        bool is_dirty(enum direction for_dir);

        bool is_solved();

        std::string to_string();
        void print();

};

typedef std::vector<Location*>    locations;

#endif