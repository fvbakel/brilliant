/*
    Purpose:
    Simulate the prison problem, and check the max prison size that is possible to simulate in a C program

    see original video
    https://www.youtube.com/watch?v=iSNsgj1OCLA

    Simulation video:
    https://www.youtube.com/watch?v=NDIaxmk8Q8c

    Claim in the video is that the max number they could simulate is 1.000.000

    Can we do more? 

    This is the solution based on and array of unsigned ints and a bit array.

    It can do:
    Prisoners        Nr simulations   Survived       Duration
    100.000.000      1                0,0000 %      < one minute

    500.000.000      1                              ~ one minute

    1.000.000.000    1                Killed, why? requires 8 Gb of Mem and I only have 6...
    
*/


#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <locale.h>
#include <time.h>
#include <stdint.h>

#define MASK 31U // this are all one's in 32 bit
#define SHIFT 5U // 2^5 = 32 bits

#define OFF 0U // Bit is Off
#define ON  1U // Bit is On

// the const below is to reduce the multiplications
const unsigned int BITS_IN_WORD=8*sizeof(uint32_t);

// the constant below is a cache of all the possible bit masks
const uint32_t offset_mask[] = {1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072,262144,524288,1048576,2097152,4194304,8388608,16777216,33554432,67108864,134217728,268435456,536870912,1073741824,2147483648};

struct bits_state {
  uint32_t *bit_array;
  unsigned int limit;
  unsigned int nr_of_words;
};

static inline struct bits_state *create_bits(int limit) {
  struct bits_state *bits_state=malloc(sizeof *bits_state);

  bits_state->nr_of_words=(limit >> SHIFT) + 1;
  bits_state->bit_array=calloc(bits_state->nr_of_words,sizeof(uint32_t));
  bits_state->limit=limit;
  return bits_state;
}

static inline void delete_bits(struct bits_state *bits_state) {
  free(bits_state->bit_array);
  free(bits_state);
}

static inline void setBit(struct bits_state *bits_state,unsigned int index) {
    unsigned int word_offset = index >> SHIFT;                // 1 word = 2ˆ5 = 32 bit, so shift 5, much faster than /32
    unsigned int offset  = index & MASK;                      // use & (and) for remainder, faster than modulus of /32
    bits_state->bit_array[word_offset] |=  offset_mask[offset];
}

static inline uint32_t getBit (struct bits_state *bits_state,unsigned int index) {
    unsigned int word_offset = index >> SHIFT;  
    unsigned int offset  = index & MASK;
    return ((bits_state->bit_array[word_offset] & offset_mask[offset]) >> offset);     // use a mask to only get the bit at position bitOffset.
}

static void printBits(struct bits_state *bits_state) {
    for (unsigned int i = 0; i < bits_state->limit;i++) {
        printf("%u",getBit(bits_state,i));
    }
    printf("\n");
}

struct simulation {
    unsigned int nr_of_prisoners;
    unsigned int nr_of_times;
    unsigned int current_sim;
    unsigned int times_escaped;
    unsigned int times_not_escaped;
    unsigned int max_loop_size;
    bool verbose;
    unsigned int *boxes;
    struct bits_state *visited;
};

void print_boxes(struct simulation* sim,bool details) {

    for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
        printf("%'d ", sim->boxes[i]);
    }
    printf("\n");
    if (details) {
        for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
            printf("Box %d prisoner %d visited %u\n", i,sim->boxes[i],getBit(sim->visited,i));
        }
        
        printf("\n");
    }
}

unsigned int random_box_num(struct simulation* sim) {
    return rand() % sim->nr_of_prisoners;
}

unsigned int next_not_visited(struct simulation* sim) {
    for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
        if (getBit(sim->visited,i) == OFF) {
           return sim->boxes[i];
       }
    }
    return -1;
}

void shuffle_boxes(struct simulation* sim) {
    unsigned int swap_box_index;
    unsigned int old;

    for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
        swap_box_index               = random_box_num(sim);
        old                          = sim->boxes[i];
        sim->boxes[i]                = sim->boxes[swap_box_index];
        sim->boxes[swap_box_index]   = old;
    }

    if (sim->visited != NULL) {
        delete_bits(sim->visited);
    }
    sim->visited = create_bits(sim->nr_of_prisoners);
}

unsigned int find_loop_size(struct simulation* sim,unsigned int next_start) {
    unsigned int loop_size = 0;
    while (true) {
        if (getBit(sim->visited,next_start)) {
            break;
        }
        setBit(sim->visited,next_start);

        loop_size ++;
        next_start = sim->boxes[next_start];
    }
    return loop_size;
}

bool has_longer_than_max(struct simulation* sim) {
    unsigned int total_checked  = 0;
    unsigned int loop_size      = 0;
    
    unsigned int next_start;

    while (true) {
        next_start = next_not_visited(sim);
        if (next_start == -1) {
            printf("This should not never happen, some program error maybe?\n");
            exit(EXIT_FAILURE);
        }

        loop_size = find_loop_size(sim,next_start);
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

    sim->boxes = (unsigned int*) malloc(sim->nr_of_prisoners * sizeof(unsigned int));
    sim->visited = NULL;

    for (unsigned int i = 0; i < sim->nr_of_prisoners; i++) {
        sim->boxes[i] = i;
    }

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