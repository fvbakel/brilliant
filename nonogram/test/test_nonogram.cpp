#include <stdio.h>
#include <iostream>
#include <sstream>
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

    nonogram->enable_rule_improve_log();
    nonogram->solve_constraint_backtrack();
    nonogram->print();

    assert(nonogram->is_solved());
    delete nonogram;
    printf("End %s(%s)\n",__FUNCTION__,filename.c_str());
}


void test_filled(Nonogram *nonogram) {
    printf("Start %s\n",__FUNCTION__);
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
     printf("End %s\n",__FUNCTION__);
}

void test_Nonegram() {
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

    printf("Start location backtrack\n");
    nonogram->solve_location_backtrack();
    nonogram->print();
    assert(nonogram->is_solved());
    printf("End location backtrack\n");

    nonogram->reset();
    assert(!nonogram->is_solved());

    printf("Start constraint backtrack\n");
    nonogram->enable_rule_improve_log();
    nonogram->solve_constraint_backtrack();
    nonogram->print();
    assert(nonogram->is_solved());
    printf("End constraint backtrack\n");

    delete nonogram;
    printf("End %s\n",__FUNCTION__);
}

void test_constraint_rule(
    std::vector<int> &blacks,
    string &start_state,
    string &expected
) {
    std::stringstream clue;
    clue<< "(";
    for (int i = 0; i< blacks.size();i++) {
        clue << blacks[i] << ",";
    }
    clue<< ")";
    printf("Start %s clue %s with [%s] expected [%s]\n",__FUNCTION__,clue.str().c_str(),start_state.c_str(),expected.c_str());

    locations locations;
    create_test_locations(start_state.size(),locations);
    MainConstraint *constraint = create_main_constraint(x_dir,&blacks,start_state,locations);

    constraint->calc_locks_rules();
    //constraint->debug_dump();
    string result = constraint->loc_string();
    printf("   result [%s]\n",result.c_str());
    assert(result.compare(expected) == 0);

    delete constraint;
    delete_test_locations(locations);

    printf("End %s clue %s with [%s] expected [%s]\n",__FUNCTION__,clue.str().c_str(),start_state.c_str(),expected.c_str());
}

void test_constraint_solution(
    std::vector<int> &blacks,
    string &start_state,
    string &expected
) {
    std::stringstream clue;
    clue<< "(";
    for (int i = 0; i< blacks.size();i++) {
        clue << blacks[i] << ",";
    }
    clue<< ")";
    printf("Start %s clue %s with [%s] expected [%s]\n",__FUNCTION__,clue.str().c_str(),start_state.c_str(),expected.c_str());

    locations locations;
    create_test_locations(start_state.size(),locations);
    MainConstraint *constraint = create_main_constraint(x_dir,&blacks,start_state,locations);

    //constraint->calc_locks_rules();
    constraint->calculate_solutions();
    constraint->calc_locks();
    //constraint->debug_dump();
    string result = constraint->loc_string();
    printf("   result [%s]\n",result.c_str());
    assert(result.compare(expected) == 0);

    delete constraint;
    delete_test_locations(locations);

    printf("End %s clue %s with [%s] expected [%s]\n",__FUNCTION__,clue.str().c_str(),start_state.c_str(),expected.c_str());
}

void test_constraint_rules() {
    printf("Begin %s\n",__FUNCTION__);

    std::vector<int> blacks({ 1, 4});
    //                    01234578 
    string start_state = "UUUUUUUU";
    string expected    = "UUUUXXUU";
    test_constraint_rule(blacks,start_state,expected);

    blacks.clear();
    blacks.assign({ 1, 4});
    //             012345 
    start_state = "UUUUUU";
    expected    = "X XXXX";
    test_constraint_rule(blacks,start_state,expected);

    blacks.clear();
    blacks.assign({ 1, 4});
    //             012345 
    start_state = "X XXXX";
    expected    = "X XXXX";
    test_constraint_rule(blacks,start_state,expected);
                                       
    blacks.clear();
    blacks.assign({ 2, 1});
    //             012345 
    start_state = "XX UUU";
    expected    = "XX UUU";
    test_constraint_rule(blacks,start_state,expected);
    //             012345 
    start_state = "XX U U";
    expected    = "XX U U";
    test_constraint_rule(blacks,start_state,expected);
    //             012345 
    start_state = "XXUUUU";
    expected    = "XX UUU";
    test_constraint_rule(blacks,start_state,expected);
    //             012345 
    start_state = "XXUUXU";
    expected    = "XX  X ";
    test_constraint_rule(blacks,start_state,expected);
    //             0123456 
    start_state = "XXUUUXU";
    expected    = "XX   X ";
    test_constraint_rule(blacks,start_state,expected);

    blacks.clear();
    blacks.assign({ 1, 2});
    //             012345 
    start_state = "UXUUUU";
    expected    = " X UXU";
    test_constraint_rule(blacks,start_state,expected);

    blacks.clear();
    blacks.assign({ 2});
    //             012345 
    start_state = "UUXUUU";
    expected    = " UXU  ";
    test_constraint_rule(blacks,start_state,expected);

    blacks.clear();
    blacks.assign({ 3});
    //             01234567 
    start_state = "UUUXU UU";
    expected    = " UXXU   ";
    test_constraint_rule(blacks,start_state,expected);

    blacks.clear();
    blacks.assign({ 2});
    //             012345 
    start_state = "UUUUXX";
    expected    = "    XX";
    test_constraint_rule(blacks,start_state,expected);

    // test backwards search
    blacks.clear();
    blacks.assign({ 1,2});
    //             012345 
    start_state = "UUUUXX";
    expected    = "UUU XX";
    test_constraint_rule(blacks,start_state,expected);

    // the zero clue
    blacks.clear();
    //             012345 
    start_state = "UUUUUU";
    expected    = "      ";
    test_constraint_rule(blacks,start_state,expected);

    blacks.clear();
    blacks.assign({ 5 });
    //             0123456789ABCDE 
    start_state = "  UXXUUU       ";
    expected    = "  UXXXXU       ";
    test_constraint_rule(blacks,start_state,expected);

    // out of reach rule 
    blacks.clear();
    blacks.assign({ 5 });
    //             0123456789ABCDE 
    start_state = "  UXXUUUUUUUU  ";
    expected    = "  UXXXXU       ";
    test_constraint_rule(blacks,start_state,expected);

    // continue search 
    blacks.clear();
    blacks.assign({ 7,2,2,6,7 });
    //             0123456789ABCDE 
    start_state = "UXXXXXXUUX UXUUXXXXXUUXXXXXXU";
    expected    = "XXXXXXX XX UXUUXXXXXUUXXXXXXU";
    test_constraint_rule(blacks,start_state,expected);

    // detect must be other segment
    blacks.clear();
    blacks.assign({ 1,3,1,5,2,3,1,3,1 });
    //             0123456789ABCDE 
    start_state = "X XXX X UXXXXUUXUUXXUUXUXXXUU";
    expected    = "X XXX X UXXXXUUXUUXXU X XXX X";
    test_constraint_rule(blacks,start_state,expected);


/*
    // multipattern complete
    blacks.clear();
    blacks.assign({ 1,1,1});
    //             0123456789A 
    start_state = "UUXUUXUUXUU";
    expected    = "  X  X  X  ";
    test_constraint_rule(blacks,start_state,expected);

    // multipattern incomplete
    blacks.clear();
    blacks.assign({ 2,2,2});
    //             0123456789ABCDEFG 
    start_state = "UUUXUUUUXUUUUXUUU";
    expected    = "  UXU  UXU  UXU  ";
    test_constraint_rule(blacks,start_state,expected);
*/
    printf("End %s\n",__FUNCTION__);
}

void test_constraint_rules_vs_solutions() {
    printf("Begin %s\n",__FUNCTION__);
    std::vector<int> blacks;
    string start_state;
    string expected;

    blacks.clear();
    blacks.assign({ 1, 4});
    //             012345 
    start_state = "UUUUUU";
    expected    = "X XXXX";
    test_constraint_rule(blacks,start_state,expected);
    test_constraint_solution(blacks,start_state,expected);

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

    constraint->calc_locks();
    constraint->debug_dump();
    printf("constraint->get_nr_dirty()= %d \n",constraint->get_nr_dirty());
    assert(constraint->get_nr_dirty() ==17);

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

void test_segment_location() {
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

    locations locations;
    create_test_locations(5,locations);

    locations[0]->set_segment(segment_2);
    locations[1]->set_segment(segment_2);
    assert(locations[0]->has_segment_for_dir(x_dir) == true);
    assert(locations[0]->has_segment_for_dir(y_dir) == false);
    assert(locations[0]->is_part_of_segment(segment_2) == true);
    assert(locations[0]->is_part_of_segment(segment_1) == false);
    assert(locations[0]->get_segment_for_dir(x_dir) == segment_2);
    assert(locations[0]->get_segment_for_dir(y_dir) == nullptr);

    // should report a exception
    bool hasException = false;
    try {
        locations[1]->set_segment(segment_3);
    }
    catch (std::runtime_error &e) {
        cout << e.what() << "\n";
        hasException = true;
    }
    assert(hasException);
    
    delete_test_locations(locations);

    delete segment_1;
    delete segment_2;
    delete segment_3;
    delete segment_4;
    delete segment_5;
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

    assert(segment_1->get_direction() == x_dir);

    delete segment_1;
    delete segment_2;
    delete segment_3;
    delete segment_4;
    delete segment_5;
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

int main(int argc, char *argv[]) {
    printf("Started\n");

    test_get_variance();
    test_Location();
    test_segment();
    test_segment_location();
    if (argc >1) {
        cout << "Any enter to continue";
        char dummy = getchar();
    }
    test_constraint();
    test_reduce_constraint();
    if (argc >1) {
        cout << "Any enter to continue";
        char dummy = getchar();
    }

    test_constraint_rules();
    if (argc >1) {
        cout << "Any enter to continue";
        char dummy = getchar();
    }

    test_constraint_rules_vs_solutions();
    if (argc >1) {
        cout << "Any enter to continue";
        char dummy = getchar();
    }
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
