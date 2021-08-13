/*
    Purpose:
    Solve the clowns puzzle.

    Given are 9 square puzzle pieces. 
    Each piece has 4 pictures in total, one on each side

    The solution must be a 3 by 3 square with the following rules:
    1. the color of adjacent pieces must match
    2. adjacent pieces must have a head - tail combination

*/


#include <stdio.h>
#include <stdlib.h>

int DEBUG = 0;

enum colors{ green, blue, small_stripes,big_stripes };
enum parts{ head,tail };
enum state {used,notused};
enum directions {up,right,down,left};

const char *COLOR_NAMES[] = {"groen", "blauw", "kleine","grote"};
const char *PARTS[] = {"hoofd","broek"};

struct half_man {
    enum colors color;
    enum parts part;
};

struct piece {
    int id;
    struct half_man up;
    struct half_man right;
    struct half_man down;
    struct half_man left;
    enum state current_state; 
};

struct piece **make_pieces() {
    struct piece **pieces =  (struct piece**) malloc(9 * sizeof(struct piece*));
    for (int i =0;i<9;i++) {
        pieces[i] = (struct piece*) malloc(sizeof(struct piece));
    }

    pieces[0]->up.color = green;
    pieces[0]->up.part = head;
    pieces[0]->right.color = green;
    pieces[0]->right.part = tail;
    pieces[0]->down.color = blue;
    pieces[0]->down.part = tail;
    pieces[0]->left.color = big_stripes;
    pieces[0]->left.part = head;
    pieces[0]->current_state = notused;
    pieces[0]->id = 0;

    pieces[1]->up.color = big_stripes;
    pieces[1]->up.part = head;
    pieces[1]->right.color = green;
    pieces[1]->right.part = tail;
    pieces[1]->down.color = blue;
    pieces[1]->down.part = tail;
    pieces[1]->left.color = green;
    pieces[1]->left.part = head;
    pieces[1]->current_state = notused;
    pieces[1]->id = 1;

    pieces[2]->up.color = blue;
    pieces[2]->up.part = head;
    pieces[2]->right.color = green;
    pieces[2]->right.part = head;
    pieces[2]->down.color = small_stripes;
    pieces[2]->down.part = tail;
    pieces[2]->left.color = big_stripes;
    pieces[2]->left.part = tail;
    pieces[2]->current_state = notused;
    pieces[2]->id = 2;

    pieces[3]->up.color = small_stripes;
    pieces[3]->up.part = tail;
    pieces[3]->right.color = green;
    pieces[3]->right.part = tail;
    pieces[3]->down.color = blue;
    pieces[3]->down.part = head;
    pieces[3]->left.color = big_stripes;
    pieces[3]->left.part = head;
    pieces[3]->current_state = notused;
    pieces[3]->id = 3;

    pieces[4]->up.color = blue;
    pieces[4]->up.part = head;
    pieces[4]->right.color = big_stripes;
    pieces[4]->right.part = head;
    pieces[4]->down.color = small_stripes;
    pieces[4]->down.part = tail;
    pieces[4]->left.color = big_stripes;
    pieces[4]->left.part = tail;
    pieces[4]->current_state = notused;
    pieces[4]->id = 4;

    pieces[5]->up.color = small_stripes;
    pieces[5]->up.part = head;
    pieces[5]->right.color = green;
    pieces[5]->right.part = head;
    pieces[5]->down.color = blue;
    pieces[5]->down.part = tail;
    pieces[5]->left.color = green;
    pieces[5]->left.part = tail;
    pieces[5]->current_state = notused;
    pieces[5]->id = 5;

    pieces[6]->up.color = green;
    pieces[6]->up.part = head;
    pieces[6]->right.color = big_stripes;
    pieces[6]->right.part = head;
    pieces[6]->down.color = blue;
    pieces[6]->down.part = tail;
    pieces[6]->left.color = small_stripes;
    pieces[6]->left.part = tail;
    pieces[6]->current_state = notused;
    pieces[6]->id = 6;

    pieces[7]->up.color = blue;
    pieces[7]->up.part = head;
    pieces[7]->right.color = big_stripes;
    pieces[7]->right.part = head;
    pieces[7]->down.color = small_stripes;
    pieces[7]->down.part = tail;
    pieces[7]->left.color = green;
    pieces[7]->left.part = tail;
    pieces[7]->current_state = notused;
    pieces[7]->id = 7;

    pieces[8]->up.color = small_stripes;
    pieces[8]->up.part = head;
    pieces[8]->right.color = green;
    pieces[8]->right.part = head;
    pieces[8]->down.color = blue;
    pieces[8]->down.part = tail;
    pieces[8]->left.color = big_stripes;
    pieces[8]->left.part = tail;
    pieces[8]->current_state = notused;
    pieces[8]->id = 8;

    return pieces;
}

void rotate_piece(struct piece* pc) {
    struct half_man tmp = pc->up;
    pc->up = pc->right;
    pc->right = pc->down;
    pc->down = pc->left;
    pc->left = tmp;
}

int check_two(struct piece *one,struct piece *two,enum directions direction) {
    int result = 1;
    
    if (one==NULL || two==NULL) {
        return 1;
    } else {
        if (direction == right) {
            if (one->right.color != two->left.color) {
                return 0;
            } else if (one->right.part == head && two->left.part != tail) {
                return 0;
            } else if (one->right.part == tail && two->left.part != head) {
                return 0;
            } else {
                // this must be a match!
            }
        } else if (direction == down) {
            if (one->down.color != two->up.color) {
                return 0;
            } else if (one->down.part == head && two->up.part != tail) {
                return 0;
            } else if (one->down.part == tail && two->up.part != head) {
                return 0;
            } else {
                // this must be a match!
            }
        } else {
            printf("Error, direction %d is not implemented\n",direction);
            exit(0);
        }
    }
    return result;
}

int check_row(struct piece **solution, int row) {
    int result = 1;
    int start = row * 3;
    result = check_two(solution[start],solution[start+1],right);
    if (result) {
        result = check_two(solution[start+1],solution[start+2],right);
    }
    return result;
}

int check_col(struct piece **solution, int col) {
    int result = 1;
    result = check_two(solution[col],solution[col+3],down);
    if (result) {
        result = check_two(solution[col+3],solution[col+6],down);
    }
    return result;
}

int check_correct(struct piece **solution) {
    int result = 1;
    for (int i =0;i<3;i++) {
        result = check_row(solution,i);
        if (!result) {
            return result;
        }
    }
    
    for (int i =0;i<3;i++) {
        result = check_col(solution,i);
        if (!result) {
            return result;
        }
    }

    return result;
}

int check_complete(struct piece **solution) {
    for (int i = 0; i < 9; i++) {
        if (solution[i]==NULL) {
            return 0;
        }
    }
    return 1;
}

int solve_next(struct piece **pieces,struct piece **solution,int pos) {
    int result = 0;
    for(int try_piece = 0; try_piece < 9; try_piece++) {
        if (pieces[try_piece]->current_state == notused) {
            pieces[try_piece]->current_state = used;
            for(int direction = up; direction <= left; direction++ ) {
                rotate_piece(pieces[try_piece]);
                solution[pos] = pieces[try_piece];
                result = check_correct(solution);

                if (result) {
                    if (pos < 8) {
                        result = solve_next(pieces,solution,pos + 1);
                    } 
                    if (result) {
                        return result;
                    }
                }
            }
            pieces[try_piece]->current_state = notused;
            solution[pos] = NULL;
        }
    }
    return result;
}


void print_solution(struct piece **solution) {

    for (int row = 0; row < 3; row++) {
        int start = row * 3;
        for (int col = 0; col < 3; col++) {
            struct half_man *h_man = &(solution[start + col]->up);
            printf(";;%s - %s;",PARTS[h_man->part],COLOR_NAMES[h_man->color]);
        }
        printf("\n");
        for (int col = 0; col < 3; col++) {
            struct half_man *h_man = &(solution[start + col]->left);
            printf(";%s - %s;%d",PARTS[h_man->part],COLOR_NAMES[h_man->color],solution[start + col]->id);
            h_man = &(solution[start + col]->right);
            printf(";%s - %s",PARTS[h_man->part],COLOR_NAMES[h_man->color]);
        }
        printf("\n");
        for (int col = 0; col < 3; col++) {
            struct half_man *h_man = &(solution[start + col]->down);
            printf(";;%s - %s;",PARTS[h_man->part],COLOR_NAMES[h_man->color]);
        }
        printf("\n");
    }
}


int main(int argc, char **argv) {
    int result = 0;
    struct piece **pieces = make_pieces();

    struct piece *solution[9] = { NULL };

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

}