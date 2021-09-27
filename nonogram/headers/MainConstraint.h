#ifndef _MAINCONSTRAINT_H
#define _MAINCONSTRAINT_H	1

#include <vector>

#include <constants.h>
#include <Constraint.h>


class MainConstraint : public Constraint {
    
    public:
        MainConstraint(enum direction direction,std::vector<int> *blacks);
        ~MainConstraint();
};

typedef std::vector<MainConstraint*>    main_constraints;

#endif