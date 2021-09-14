#ifndef _LOCATION_H
#define _LOCATION_H	1

#include <vector>

#include <constants.h>

class Location {
    private:
        int         m_x         = 0;
        int         m_y         = 0;
        enum color  m_color     = no_color;
        bool        m_locked    = false;

    public:
        Location(const int x,const int y);
        ~Location();

        int get_x();
        void set_x(const int x);

        int get_y();
        void set_y(const int y);

        enum color get_color();
        void set_color(enum color);
        
        bool is_locked();
        void lock();
        void unlock();

        void soft_reset();
        void hard_reset();

        bool is_solved();

        void print();

};

typedef std::vector<Location*>    locations;

#endif