#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <locale.h>
#include <time.h>
#include <stdint.h>

#define MASK 31U // this are all one's in 32 bit
#define SHIFT 5U // 2^5 = 32 bits

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

static inline void flipBit(struct bits_state *bits_state,unsigned int index) {
    unsigned int word_offset = index >> SHIFT;                // 1 word = 2ˆ5 = 32 bit, so shift 5, much faster than /32
    unsigned int offset  = index & MASK;                      // use & (and) for remainder, faster than modulus of /32
    bits_state->bit_array[word_offset] ^=  offset_mask[offset];
}

static inline void clearBit(struct bits_state *bits_state,unsigned int index) {
    unsigned int word_offset = index >> SHIFT;                // 1 word = 2ˆ5 = 32 bit, so shift 5, much faster than /32
    unsigned int offset  = index & MASK;                      // use & (and) for remainder, faster than modulus of /32
    bits_state->bit_array[word_offset] = bits_state->bit_array[word_offset] &~ offset_mask[offset];
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

int main(int argc, char **argv) {
    setlocale(LC_NUMERIC, "");
    unsigned int limit = 100;
    unsigned int nr_of_words = (limit >> 5U) + 1;

    printf("if each word contains 32 bits then %d words are required to hold %d bits\n",nr_of_words,limit);

    struct bits_state* bits = create_bits(limit);
    printBits(bits);
    setBit(bits,0);

    setBit(bits,1);
    clearBit(bits,1);

    setBit(bits,2);
    flipBit(bits,2);
    setBit(bits,3);
    flipBit(bits,2);
    flipBit(bits,2);

    setBit(bits,31);
    setBit(bits,32);
    setBit(bits,63);
    setBit(bits,64);
    setBit(bits,99);
    setBit(bits,100);
    printBits(bits);

}