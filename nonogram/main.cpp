#include <stdio.h>
#include <vector>
#include <assert.h>

#include <Nonogram.h>



void process_file (string &filename) {
    printf("Start processing: %s\n",filename.c_str());
    Nonogram *nonogram = new Nonogram(filename);

    nonogram->solve_constraint_backtrack();
    nonogram->print();

    if(nonogram->is_solved()) {
        printf("Solved successfully\n");
    } else {
        printf("Unable to solve\n");
    }
    delete nonogram;
    printf("End processing: %s\n",filename.c_str());
}

int main(int argc, char *argv[]) {

    if (argc > 1) {
        printf("Started\n");
        string filename = string(argv[1]);
        process_file (filename);
        printf("Ready\n");
    }
    return 0;
}
