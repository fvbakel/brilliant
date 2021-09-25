#include <stdio.h>
#include <vector>
#include <assert.h>

#include <Segment.h>
#include <MainConstraint.h>
#include <Nonogram.h>
#include <Location.h>
#include <constants.h>
#include <VarianceCalculator.h>


/*
Helper functions
*/
void create_test_locations(const int nr_to_create,locations &test_locations) {
    test_locations.clear();
    for (int pos = 0;pos < nr_to_create; pos++) {
        test_locations.push_back(new Location(pos,0));
    }
}

void delete_test_locations(locations &test_locations) {
    for (Location *location : test_locations) {
        delete location;
    }
    test_locations.clear();
}

MainConstraint* create_main_constraint(
    enum direction cur_dir,
    std::vector<int> *blacks, 
    const string start_state,
    locations &test_locations
) {
    MainConstraint *constraint = new MainConstraint(x_dir,blacks);
    for (int pos = 0;pos < start_state.size();pos++) {
        char loc_state = start_state.at(pos);
        test_locations[pos]->hard_reset();
        if (loc_state == ' ') {
            test_locations[pos]->set_color(white);
            test_locations[pos]->lock();
        } else if (loc_state == 'X') { 
            test_locations[pos]->set_color(black);
            test_locations[pos]->lock();
        }
        constraint->add_location(test_locations[pos]);
    }
    return constraint;
}


/*
test functions
*/
void test_Location () {
    printf("Start %s\n",__FUNCTION__);
    Location *location = new Location(1,2);
    delete location;

    printf("End %s\n",__FUNCTION__);
}

void test_Nonegram_file_wrong (string &filename) {
    printf("Start %s(%s)\n",__FUNCTION__,filename.c_str());
    Nonogram *nonogram = new Nonogram(filename);

    assert(!nonogram->is_input_valid());
    delete nonogram;
    printf("End %s(%s)\n",__FUNCTION__,filename.c_str());
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

void test_constraint_min_max_rule() {
    printf("Start %s\n",__FUNCTION__);

    std::vector<int> blacks({ 1, 4});
    //                    012345 
    string start_state = "UUUUUU";
    locations locations;
    create_test_locations(start_state.size(),locations);
    MainConstraint *constraint = create_main_constraint(x_dir,&blacks,start_state,locations);

    std::unordered_set<int> affected;
    constraint->calc_locks_rule_min_max(&affected);
    constraint->debug_dump();
    assert(affected.size()==6);

    delete constraint;
    delete_test_locations(locations);

    printf("End %s\n",__FUNCTION__);
}

void test_reduce_constraint() {
    // example:
    // Y: 2 2 7 2 1 7 1 2 6 2 2 
    // |    UUU XX XUXXUUX  UX   UUU U   X XXXXXXXU X U  U U  UU  XXXXXX  XXUXXU|
    // should be reduced to:
    // |    UXU XX XXXXXXX  XX           X XXXXXXX  X         XX  XXXXXX  XX XX |
    printf("Start %s\n",__FUNCTION__);
    std::vector<int> blacks({ 2, 2, 7, 2, 1, 7, 1, 2, 6, 2, 2});
    MainConstraint *constraint = new MainConstraint(x_dir,&blacks); 
    const int size = 100;
    Location *location[size];
    for (int pos = 0;pos < size; pos++) {
        location[pos] = new Location(pos,0);
    }

    // white segments that can vary theory = 12
    // white segments that can vary actual = 2
    // white space unknown actual = 1
    // whitespace variation determined = 4 + 1 + 2 + 2 etc. 
    string start_state = "    UUU XX XUXXUUX  UX   UUU U   X XXXXXXXU X U  U U  UU  XXXXXX  XXUXXU";
    for (int pos = 0;pos < start_state.size();pos++) {
        char loc_state = start_state.at(pos);
        if (loc_state == ' ') {
            location[pos]->set_color(white);
            location[pos]->lock();
        } else if (loc_state == 'X') { 
            location[pos]->set_color(black);
            location[pos]->lock();
        }
        constraint->add_location(location[pos]);
    }

    //
    int var = constraint->get_variation();
    printf("Variation estimate = %d \n",var);
    
    assert(var <= 7726160);
    //assert(var == 2);

    // check
    constraint->calculate_solutions();
    constraint->debug_dump();
    assert(constraint->get_solution_size() == 2);

    std::unordered_set<int> affected;
    constraint->calc_locks(&affected);
    constraint->debug_dump();
    printf("Affected size = %lu \n",affected.size());
    assert(affected.size() ==17);

    delete constraint;

    // delete of locations
    for (int i = 0; i < size; i++) {
        delete location[i];
    }

    printf("End %s\n",__FUNCTION__);
}

void test_constraint () {
    printf("Start %s\n",__FUNCTION__);

    std::vector<int> blacks({ 2, 1});
    MainConstraint *constraint = new MainConstraint(x_dir,&blacks); 
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
    assert(!constraint->is_passed());

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
    constraint = new MainConstraint(x_dir,&blacks_2);

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

    std::vector<int> blacks_3({1,1});
    constraint = new MainConstraint(x_dir,&blacks_3);

    for (int i = 0; i < 5; i++) {
        constraint->add_location(location[i]);
    }
    location[0]->set_color(black);
    location[1]->set_color(white);
    location[2]->set_color(black);
    location[3]->set_color(white);
    location[4]->set_color(white);
    location[5]->set_color(no_color);
    for (int i = 0; i < 4; i++) {
        location[i]->lock();
    }

    constraint->calculate_solutions();
    assert(constraint->get_solution_size() == 1);

    for (int i = 0; i < 4; i++) {
        location[i]->unlock();
    }
    location[0]->set_color(no_color);
    location[1]->set_color(no_color);
    location[2]->set_color(no_color);
    location[3]->set_color(no_color);
    location[4]->set_color(no_color);
    location[5]->set_color(no_color);

    constraint->reset_solution();
    constraint->calculate_solutions();
    printf("solution size = %d\n",constraint->get_solution_size());
    printf("variation size = %d\n",constraint->get_variation());
  //  assert(constraint->get_solution_size() == constraint->get_variation());
    delete constraint;

    std::vector<int> blacks_4({1,1,1});
    constraint = new MainConstraint(x_dir,&blacks_4);

    for (int i = 0; i < 8; i++) {
        constraint->add_location(location[i]);
        location[i]->unlock();
        location[i]->set_color(no_color);
    }
    constraint->reset_solution();
    constraint->calculate_solutions();
    constraint->debug_dump();
    printf("solution size = %d\n",constraint->get_solution_size());
    printf("variation size = %d\n",constraint->get_variation());
    assert(constraint->get_solution_size() == constraint->get_variation());
    delete constraint;

    std::vector<int> blacks_5;
    constraint = new MainConstraint(x_dir,&blacks_5);

    for (int i = 0; i < 8; i++) {
        constraint->add_location(location[i]);
        location[i]->unlock();
        location[i]->set_color(no_color);
    }

    assert(constraint->get_variation() == 1);
    constraint->calculate_solutions();
    assert(constraint->get_solution_size() == 1);

    delete constraint;

    // delete of locations
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

void test_get_variance() {
    
    assert(VarianceCalculator::getCalculator()->get_variance(1,1) == 1);
    assert(VarianceCalculator::getCalculator()->get_variance(3,3) == 10);
    assert(VarianceCalculator::getCalculator()->get_variance(3,3) == 10);
    assert(VarianceCalculator::getCalculator()->get_variance(3,8) == 45);
    assert(VarianceCalculator::getCalculator()->get_variance(5,7) == 330);
    assert(VarianceCalculator::getCalculator()->get_variance(9,16) == 735471);
}

int main() {
    printf("Started\n");

    test_get_variance();
    test_Location();
    test_segment();
    test_constraint();
    test_reduce_constraint();
    test_constraint_min_max_rule();
    
    test_Nonegram();

    string filename = string("./puzzles/QR-code.txt");
    test_Nonegram_file (filename);

    filename = string("./puzzles/alan_turing.txt");
    test_Nonegram_file (filename);

    filename = string("./puzzles/test_wrong.txt");
    test_Nonegram_file_wrong (filename);

    
    filename = string("./puzzles/cat-1_45_32.txt");
    test_Nonegram_file (filename);

    filename = string("./puzzles/42.non");
    test_Nonegram_file (filename);

    filename = string("./puzzles/54.non");
    test_Nonegram_file (filename);

    // a large file with a wide solution space...
    filename = string("./puzzles/tiger.non");
    test_Nonegram_file (filename);

    //filename = string("./puzzles/45_45_large.txt");
    //test_Nonegram_file (filename);
    
    printf("Ready\n");
    return 0;
}
