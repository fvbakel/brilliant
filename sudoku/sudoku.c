/*
    Purpose:
    Solve sudoku puzzles

*/


#include <stdio.h>
#include <stdlib.h>

int DEBUG = 0;

enum state {used,notused,given};

struct piece {
    int num;
    enum state current_state; 
};

struct piece **make_pieces() {
    struct piece **pieces =  (struct piece**) malloc(81 * sizeof(struct piece*));
    for (int i = 0; i < 81; i++) {
        int num = (i % 9) + 1;
        pieces[i] = (struct piece*) malloc(sizeof(struct piece));
        pieces[i]->num = num;
        pieces[i]->current_state = notused;
    }

    return pieces;
}

int check_row(struct piece **solution, int row) {
    int result = 1;
    int start = row * 9;
    int end = start + 9;

    for (int i = start; i < end; i++) {
        if (solution[i] != NULL && (i+1) != end) {
            for (int j = i+1; j < end; j++) {
                if (solution[j] != NULL) {
                    if (solution[i]->num == solution[j]->num ) {
                        return 0;
                    }
                }
            }
        }

    }
    return result;
}

int check_col(struct piece **solution, int col) {
    int result = 1;
    int start = col;
    int end = 72 + col;

    for (int i = start; i <= end; i+=9) {
        if (solution[i] != NULL && (i+1) != end) {
            for (int j = i+9; j <= end; j+=9) {
                if (solution[j] != NULL) {
                    if (solution[i]->num == solution[j]->num ) {
                        return 0;
                    }
                }
            }
        }
    }
    return result;
}

int square_pos_2_index(int i, int start) {
    int result = (i % 3) + start;
    if (i > 2 && i < 6) {
        result = result + 9;
    } else if (i > 5 && i < 9) {
        result = result + (2*9);
    }
    return result;
}

int check_square(struct piece **solution, int square) {
    int result = 1;
    int start = (square % 3) * 3;
    int end = 9;
    if (square > 2 && square < 6) {
        start = start + (3 * 9);
    } else if (square > 5 && square < 9) {
        start = start + (6 * 9);
    }

    for (int k = 0; k < 9; k++) {
        int i = square_pos_2_index(k,start);
        if (solution[i] != NULL && (k+1) != end) {
            for (int l = k+1 ; l < end; l++) {
                int j = square_pos_2_index(l,start);
                if (solution[j] != NULL) {
                    if (solution[i]->num == solution[j]->num ) {
                        return 0;
                    }
                }
            }
        }
    }
    return result;
}

int check_correct(struct piece **solution) {
    int result = 1;
    for (int i = 0; i < 9; i++) {
        result = check_row(solution,i);
        if (!result) {
            return result;
        }
    }
    
    for (int i =0;i<9;i++) {
        result = check_col(solution,i);
        if (!result) {
            return result;
        }
    }

    for (int i =0;i<9;i++) {
        result = check_square(solution,i);
        if (!result) {
            return result;
        }
    }
    return result;
}

int check_complete(struct piece **solution) {
    for (int i = 0; i < 81; i++) {
        if (solution[i]==NULL) {
            return 0;
        }
    }
    return 1;
}

int solve_next(struct piece **pieces,struct piece **solution,int pos) {
    int result = 0;
    if (solution[pos] != NULL && solution[pos]->current_state == given) {
        if (pos < 80) {
            result = solve_next(pieces,solution,pos + 1);
        } 
    } else {
        int start = (pos / 9 ) * 9;
        int end = ((pos / 9) +1) * 9;
        for(int try_piece = start; try_piece < end; try_piece++) {
            if (pieces[try_piece]->current_state == notused) {
                pieces[try_piece]->current_state = used;
                solution[pos] = pieces[try_piece];
                result = check_correct(solution);

                if (result) {
                    if (pos < 80) {
                        result = solve_next(pieces,solution,pos + 1);
                    } 
                    if (result) {
                        return result;
                    }
                }
                pieces[try_piece]->current_state = notused;
                solution[pos] = NULL;
            }
        }
    }
    return result;
}

void load_puzzle(char* input_file,struct piece **pieces,struct piece **solution) {
    FILE * fp;
    char * line = NULL;
    size_t len = 0;
    ssize_t read;
    int row = 0;
    int row_index = 0;

    fp = fopen(input_file, "r");
    if (fp == NULL) {
        exit(EXIT_FAILURE);
    }

    while ((read = getline(&line, &len, fp)) != -1) {
        printf("%s", line);
        if (len >= 9) {
            for (int i = 0; i  < 9; i++) {
                int value = line[i] - '0';
                if (value) {
                    struct piece *pc = pieces[(row * 9) + value - 1];
                    if (pc->num != value) {
                        printf("Unexpected error in reading file. row=%d,pos=%d,value=%d piece index=%d,num=%d\n",\
                                row,i,value,(row * 9) + value -1,pc->num
                        );
                    }
                    pc->current_state = given;
                    solution[(row*9)+i] = pc;
                }
            }
        row++;
        }
    }

    fclose(fp);
    if (line) {
        free(line);
    }

    printf("Puzzle %s loaded\n",input_file);
}

void print_solution(struct piece **solution) {

    for (int i = 0; i  < 9; i++) { 
        if (i%3 == 0 ) {
            printf("\n");
        }
        for (int j = 0; j  < 9; j++) { 
            int pos = (i * 9) + j;
            if (j%3 == 0 ) {
                printf("  ");
            }
            printf(" %d ",solution[pos]->num);
        }
        printf("\n");

    }

    printf("\n");

}


int main(int argc, char **argv) {
    int result = 0;
    struct piece **pieces = make_pieces();

    struct piece *solution[81] = { NULL };
    char *input_file = "./puzzles/sample.txt";

    load_puzzle(input_file,pieces,solution);

    solve_next(pieces,solution,0);

    result = check_correct(solution);
    if (result == 1) {
        printf("Solution is correct\n");
    } else if (result == 0) {
        printf("Solution is not correct\n");
    }

    result = check_complete(solution);
    if (result == 1) {
        printf("Solution is complete\n");
        print_solution(solution);
    } else if (result == 0) {
        printf("Solution is not complete\n");
    }

    result = check_col(solution,1);

}