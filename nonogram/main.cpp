#include <stdio.h>
#include <vector>
#include <assert.h>

#include <Nonogram.h>



void process_file (string &filename, bool rule_improve_log = false) {
    printf("Start processing: %s\n",filename.c_str());
    Nonogram *nonogram = new Nonogram(filename);
    if (rule_improve_log) {
        nonogram->enable_rule_improve_log();
    }
    nonogram->solve();
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
        bool rule_improve_log = false;
        if (argc > 2) {
            rule_improve_log = true;
        }
        process_file (filename,rule_improve_log);
        printf("Ready\n");
    }
    return 0;
}
