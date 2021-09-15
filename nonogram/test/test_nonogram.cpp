#include <stdio.h>
#include <vector>
#include <assert.h>

#include <Segment.h>
#include <Constraint.h>
#include <Nonogram.h>
#include <Location.h>
#include <constants.h>


void test_Location () {
    printf("Start %s\n",__FUNCTION__);
    Location *location = new Location(1,2);
    delete location;

    printf("End %s\n",__FUNCTION__);
}

void test_Nonegram_file (string &filename) {
    printf("Start %s(%s)\n",__FUNCTION__,filename.c_str());
    Nonogram *nonogram = new Nonogram(filename);

    nonogram->solve_constraint_backtrack();
    nonogram->print();

    assert(nonogram->is_solved());
    delete nonogram;
    printf("End %s(%s)\n",__FUNCTION__,filename.c_str());
}


void test_filled(Nonogram *nonogram) {
    
    nonogram->get_Location(0,0)->set_color(black);
    nonogram->get_Location(1,0)->set_color(black);
    nonogram->get_Location(2,0)->set_color(white);
    nonogram->get_Location(3,0)->set_color(white);
    nonogram->get_Location(4,0)->set_color(white);
    nonogram->get_Location(5,0)->set_color(black);

    nonogram->get_Location(0,1)->set_color(white);
    nonogram->get_Location(1,1)->set_color(black);
    nonogram->get_Location(2,1)->set_color(white);
    nonogram->get_Location(3,1)->set_color(black);
    nonogram->get_Location(4,1)->set_color(black);
    nonogram->get_Location(5,1)->set_color(black);

    nonogram->get_Location(0,2)->set_color(white);
    nonogram->get_Location(1,2)->set_color(black);
    nonogram->get_Location(2,2)->set_color(white);
    nonogram->get_Location(3,2)->set_color(black);
    nonogram->get_Location(4,2)->set_color(black);
    nonogram->get_Location(5,2)->set_color(white);

    nonogram->get_Location(0,3)->set_color(white);
    nonogram->get_Location(1,3)->set_color(black);
    nonogram->get_Location(2,3)->set_color(black);
    nonogram->get_Location(3,3)->set_color(black);
    nonogram->get_Location(4,3)->set_color(white);
    nonogram->get_Location(5,3)->set_color(white);

    nonogram->get_Location(0,4)->set_color(white);
    nonogram->get_Location(1,4)->set_color(black);
    nonogram->get_Location(2,4)->set_color(black);
    nonogram->get_Location(3,4)->set_color(black);
    nonogram->get_Location(4,4)->set_color(black);
    nonogram->get_Location(5,4)->set_color(white);

    nonogram->get_Location(0,5)->set_color(white);
    nonogram->get_Location(1,5)->set_color(white);
    nonogram->get_Location(2,5)->set_color(white);
    nonogram->get_Location(3,5)->set_color(black);
    nonogram->get_Location(4,5)->set_color(white);
    nonogram->get_Location(5,5)->set_color(white);

}

void test_Nonegram () {
    printf("Start %s\n",__FUNCTION__);
    string filename = string("./puzzles/small.txt");
    Nonogram *nonogram = new Nonogram(filename);

    assert(nonogram->get_Location(0,0) != nullptr);
    
    assert(nonogram->is_consistent());
    assert(!nonogram->is_complete());
    assert(!nonogram->is_solved());

    test_filled(nonogram);
    nonogram->print();
    assert(nonogram->is_consistent());
    assert(nonogram->is_complete());
    assert(nonogram->is_solved());

    nonogram->reset();
    assert(!nonogram->is_solved());

    nonogram->solve_location_backtrack();
    nonogram->print();
    assert(nonogram->is_solved());

    nonogram->reset();
    assert(!nonogram->is_solved());

    nonogram->solve_constraint_backtrack();
    nonogram->print();
    assert(nonogram->is_solved());


    delete nonogram;
    printf("End %s\n",__FUNCTION__);
}

void test_constraint () {
    printf("Start %s\n",__FUNCTION__);

    std::vector<int> blacks({ 2, 1});
    Constraint *constraint = new Constraint(x_dir,&blacks); 
    Location *location[8] = {   new Location(0,0),\
                                new Location(1,0),\
                                new Location(2,0),\
                                new Location(3,0),\
                                new Location(4,0),\
                                new Location(5,0),\
                                new Location(6,0),\
                                new Location(7,0)
    };

    for (int i = 0; i < 4; i++) {
        constraint->add_location(location[i]);
    }

    assert(constraint->get_size() == 4);
    assert(constraint->get_white_var() == 0);

    assert(constraint->is_passed());
    location[0]->set_color(white);
    assert(constraint->is_passed());

    location[0]->set_color(black);
    assert(constraint->is_passed());

    location[0]->set_color(black);
    location[1]->set_color(black);
    location[2]->set_color(white);
    location[3]->set_color(black);

    assert(location[0]->get_color() == black);
    assert(constraint->is_passed());

    location[0]->set_color(black);
    location[1]->set_color(black);
    location[2]->set_color(black);
    location[3]->set_color(black);

    assert(!constraint->is_passed());

    location[0]->set_color(black);
    location[1]->set_color(black);
    location[2]->set_color(white);
    location[3]->set_color(white);

    assert(!constraint->is_passed());

    location[0]->set_color(white);
    location[1]->set_color(black);
    location[2]->set_color(black);
    location[3]->set_color(white);

    assert(!constraint->is_passed());

    location[0]->set_color(black);
    location[1]->set_color(white);
    location[2]->set_color(black);
    location[3]->set_color(white);

    assert(!constraint->is_passed());

    // 5 locations
    constraint->add_location(location[4]);

    location[0]->set_color(black);
    location[1]->set_color(black);
    location[2]->set_color(white);
    location[3]->set_color(black);
    location[4]->set_color(white);

    assert(constraint->is_passed());

    location[0]->set_color(white);
    location[1]->set_color(black);
    location[2]->set_color(black);
    location[3]->set_color(white);
    location[4]->set_color(black);

    assert(constraint->is_passed());

    location[0]->set_color(white);
    location[1]->set_color(black);
    location[2]->set_color(black);
    location[3]->set_color(white);
    location[4]->set_color(no_color);

    assert(constraint->is_passed());


    delete constraint;
    std::vector<int> blacks_2({5});
    constraint = new Constraint(x_dir,&blacks_2);

    for (int i = 0; i < 6; i++) {
        constraint->add_location(location[i]);
    }

    location[0]->set_color(black);
    location[1]->set_color(black);
    location[2]->set_color(black);
    location[3]->set_color(black);
    location[4]->set_color(black);
    location[5]->set_color(white);
    
    assert(constraint->is_passed());

    delete constraint;
    for (int i = 0; i < 8; i++) {
        delete location[i];
    }


    printf("End %s\n",__FUNCTION__);
}

void test_segment() {
    printf("Start %s\n",__FUNCTION__);
    Segment *segment_1 = new Segment(white,x_dir,0);
    Segment *segment_2 = new Segment(black,x_dir,2);
    Segment *segment_3 = new Segment(white,x_dir,1);
    Segment *segment_4 = new Segment(black,x_dir,1);
    Segment *segment_5 = new Segment(white,x_dir,0);

    segment_1->set_after(segment_2);
    segment_2->set_after(segment_3);
    segment_3->set_after(segment_4);
    segment_4->set_after(segment_5);
    printf("End %s\n",__FUNCTION__);
}

int main() {
    printf("Started\n");

    
    test_Location();
    test_segment();
    test_constraint();
    
    test_Nonegram();

    string filename = string("./puzzles/QR-code.txt");
    test_Nonegram_file (filename);

    filename = string("./puzzles/alan_turing.txt");
    test_Nonegram_file (filename);
    
    printf("Ready\n");
    return 0;
}
