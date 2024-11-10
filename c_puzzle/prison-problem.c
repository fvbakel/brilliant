/*
    Purpose:
    Simulate the prison problem, and check the max prison size that is possible to simulate in a C program

    see original video
    https://www.youtube.com/watch?v=iSNsgj1OCLA

    Simulation video:
    https://www.youtube.com/watch?v=NDIaxmk8Q8c

    Claim in the video is that the max number they could simulate is 1.000.000

    Can we do more? 

    This is the first straight forward, meaning full, happy to read code in C
    It can do:
    Prisoners        Nr simulations   Survived       Duration
     1.000.000       100              37,0000 %      < one minute
    10.000.000       10               50,0000 %      < one minute
    100.000.000      1                 0,0000 %      < one minute
    
    Unable to allocate memory required for 1.000.000.000 prisoners
*/


#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <locale.h>
#include <time.h>

struct box {
    unsigned int    box_number;
    struct box*     points_to_box;
    bool            visited;
};

struct simulation {
    unsigned int nr_of_prisoners;
    unsigned int nr_of_times;
    unsigned int current_sim;
    unsigned int times_escaped;
    unsigned int times_not_escaped;
    unsigned int max_loop_size;
    bool verbose;
    struct box **boxes;
};

struct box **make_boxes(unsigned int nr_of_boxes) {
    struct box **boxes = (struct box**) malloc(nr_of_boxes * sizeof(struct box*));
    if (boxes == NULL) return NULL;  

    struct box *all_boxes = (struct box*) malloc(nr_of_boxes * sizeof(struct box));
    if (all_boxes == NULL) {
        free(boxes);
        return NULL;
    }

    for (unsigned int i = 0; i < nr_of_boxes; i++) {
        boxes[i]                = &all_boxes[i];
        boxes[i]->box_number    = i;
        boxes[i]->visited       = false;
    }

    for (unsigned int i = 0; i < nr_of_boxes-1; i++) {
        boxes[i]->points_to_box = boxes[i+1];
    }
    boxes[nr_of_boxes-1]->points_to_box = boxes[0];

    return boxes;
}

void print_boxes(struct simulation* sim,bool details) {

    for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
        printf("%'d ", sim->boxes[i]->points_to_box->box_number);
    }
    printf("\n");
    if (details) {
        for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
            printf("Box %d prisoner %d visited %d\n", i,sim->boxes[i]->points_to_box->box_number,sim->boxes[i]->visited);
        }
        
        printf("\n");
    }
}

unsigned int random_box_num(struct simulation* sim) {
    return rand() % sim->nr_of_prisoners;
}

struct box* next_not_visited(struct simulation* sim) {
    for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
        if (sim->boxes[i]->visited == false) {
            return sim->boxes[i];
        }
    }
    return NULL;
}

void shuffle_boxes(struct simulation* sim) {
    unsigned int swap_box_index;
    struct box* old;

    for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
        swap_box_index                              = random_box_num(sim);
        old                                         = sim->boxes[i]->points_to_box;
        sim->boxes[i]->points_to_box                = sim->boxes[swap_box_index]->points_to_box;
        sim->boxes[swap_box_index]->points_to_box   = old;
        sim->boxes[i]->visited                      = false;
    }
}

unsigned int find_loop_size(struct box* next_start) {
    unsigned int loop_size = 0;
    while (true) {
        if (next_start->visited) {
            break;
        }
        next_start->visited = true;

        loop_size ++;
        next_start = next_start->points_to_box;
    }
    return loop_size;
}

bool has_longer_than_max(struct simulation* sim) {
    unsigned int total_checked  = 0;
    unsigned int loop_size      = 0;
    
    struct box* next_start;

    while (true) {
        next_start = next_not_visited(sim);
        if (next_start == NULL) {
            printf("This should not never happen, some program error maybe?\n");
            exit(EXIT_FAILURE);
        }

        loop_size = find_loop_size(next_start);
        if (loop_size > sim->max_loop_size) {
            return true;
        }
        total_checked = total_checked + loop_size;
        if (total_checked >= sim->max_loop_size) {
            return false;
        }
    }

}

void run_once(struct simulation* sim) {
    sim->current_sim++;

    shuffle_boxes(sim);
    if (sim->verbose) {
        print_boxes(sim,false);
    }
    if (has_longer_than_max(sim)) {
        sim->times_not_escaped++;
    } else {
        sim->times_escaped++;
    }
    if (sim->verbose) {
        printf("Prisoners escaped %d out of %d times\n",sim->times_escaped,sim->current_sim);
    }
}

void run_sim(struct simulation* sim) {
    sim->current_sim          = 0;
    sim->times_escaped        = 0;
    sim->times_not_escaped    = 0;
    sim->max_loop_size        = sim->nr_of_prisoners / 2;
    sim->boxes = make_boxes(sim->nr_of_prisoners);

    if (sim->boxes == NULL) {
        printf("Unable to allocate memory required for %'d prisoners\n",sim->nr_of_prisoners);
        exit(EXIT_FAILURE);
    }

    for (unsigned int i = 0; i < sim->nr_of_times;i++) {
        run_once(sim);
    }
    double percent = (sim->times_escaped / (double) sim->current_sim) * 100;
    printf("Prisoners escaped %d out of %d times that is %0.4f %%\n",sim->times_escaped,sim->current_sim,percent);
}

struct simulation* make_sim_from_cmd_parameters (int argc, char **argv) {
    struct simulation* sim = (struct simulation*) malloc(sizeof(struct simulation));
    char *endptr, *str;

    if (argc < 2) {
        fprintf(stderr, "Usage: %s nr_of_prisoners [nr_of_times] [-v]\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    str = argv[1];

    sim->nr_of_prisoners   = strtoull(str, &endptr, 10); 
    sim->nr_of_times       = (argc > 2) ? atoi(argv[2]) : 1;
    sim->verbose           = (argc > 3) ? true : false;

    return sim;
}



int main(int argc, char **argv) {
    setlocale(LC_NUMERIC, "");

    struct simulation* sim = make_sim_from_cmd_parameters(argc,argv);
    srand ( time(NULL) );
    run_sim(sim);

    printf("Ready\n");
    exit(EXIT_SUCCESS);
}