#include <stdio.h>
#include <vector>

#include <Piece.h>
#include <Segment.h>
#include <Constraint.h>
#include <Nonogram.h>
#include <constants.h>

void test_Nonegram () {
    printf("Start %s\n",__FUNCTION__);
    string filename = string("./puzzles/small.txt");
    Nonogram *nonogram = new Nonogram(filename);
    delete nonogram;
    printf("End %s\n",__FUNCTION__);
}

void test_constraint () {
    printf("Start %s\n",__FUNCTION__);
    
    std::vector<int> blacks({ 2, 1});
    Constraint *constraint = new Constraint(x_dir,&blacks); 
    delete constraint;
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

void test_piece() {
    printf("Start %s\n",__FUNCTION__);
    Piece *piece = new Piece(1,1,white);
    delete piece;
    printf("End %s\n",__FUNCTION__);
}

int main() {
    printf("Started\n");

    printf("0 \n");
    test_piece();
    printf("1 \n");
    test_segment();
    printf("2 \n");
    test_constraint();
    printf("3 \n");
    test_Nonegram();

    printf("Ready\n");
    return 0;
}
