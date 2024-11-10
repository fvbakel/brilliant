#include <stdio.h>
#include <stdlib.h>

void write_array_to_file(const char *filename, unsigned int *array, size_t size) {
    FILE *file = fopen(filename, "wb");
    if (file == NULL) {
        perror("Error opening file for writing");
        exit(EXIT_FAILURE);
    }

    // Write the array to the file in binary format
    if (fwrite(array, sizeof(unsigned int), size, file) != size) {
        perror("Error writing array to file");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    fclose(file);
}

unsigned int read_value_from_file(const char *filename, size_t position) {
    FILE *file = fopen(filename, "rb");
    if (file == NULL) {
        perror("Error opening file for reading");
        exit(EXIT_FAILURE);
    }

    unsigned int value;

    // Seek to the specific position in the file
    if (fseek(file, position * sizeof(unsigned int), SEEK_SET) != 0) {
        perror("Error seeking in file");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Read the integer at the specified position
    if (fread(&value, sizeof(unsigned int), 1, file) != 1) {
        perror("Error reading value from file");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    fclose(file);
    return value;
}

void make_initial_prison_file(const char *filename, unsigned int nr_of_prisoners) {
    FILE *file = fopen(filename, "wb");
    if (file == NULL) {
        perror("Error opening file for writing");
        exit(EXIT_FAILURE);
    }

    for (unsigned int i = 0; i < nr_of_prisoners;i++) {
        if (fwrite(&i, sizeof(unsigned int), 1, file) != 1) {
            perror("Error writing initial prisoners to file");
            fclose(file);
            exit(EXIT_FAILURE);
        }
    }

    fclose(file);
}


void swap_values_in_file(const char *filename, size_t pos1, size_t pos2) {
    FILE *file = fopen(filename, "r+b"); // Open in read and write binary mode
    if (file == NULL) {
        perror("Error opening file for reading and writing");
        exit(EXIT_FAILURE);
    }

    unsigned int val1, val2;

    // Seek and read the first value
    if (fseek(file, pos1 * sizeof(unsigned int), SEEK_SET) != 0) {
        perror("Error seeking to position 1 in file");
        fclose(file);
        exit(EXIT_FAILURE);
    }
    if (fread(&val1, sizeof(unsigned int), 1, file) != 1) {
        perror("Error reading value at position 1");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Seek and read the second value
    if (fseek(file, pos2 * sizeof(unsigned int), SEEK_SET) != 0) {
        perror("Error seeking to position 2 in file");
        fclose(file);
        exit(EXIT_FAILURE);
    }
    if (fread(&val2, sizeof(unsigned int), 1, file) != 1) {
        perror("Error reading value at position 2");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Write val2 to pos1
    if (fseek(file, pos1 * sizeof(unsigned int), SEEK_SET) != 0) {
        perror("Error seeking to position 1 for writing");
        fclose(file);
        exit(EXIT_FAILURE);
    }
    if (fwrite(&val2, sizeof(unsigned int), 1, file) != 1) {
        perror("Error writing value to position 1");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Write val1 to pos2
    if (fseek(file, pos2 * sizeof(unsigned int), SEEK_SET) != 0) {
        perror("Error seeking to position 2 for writing");
        fclose(file);
        exit(EXIT_FAILURE);
    }
    if (fwrite(&val1, sizeof(unsigned int), 1, file) != 1) {
        perror("Error writing value to position 2");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    fclose(file);
}


int main() {
    unsigned int array[] = {10, 20, 30, 40, 50};
    size_t size = sizeof(array) / sizeof(array[0]);
    const char *filename = "integers.bin";

    // Write the array to a binary file
    write_array_to_file(filename, array, size);
    printf("Array written to file '%s'.\n", filename);

    // Read a specific value from the file
    size_t position = 3;  
    if (position >= size) {
        fprintf(stderr, "Position out of bounds\n");
        return EXIT_FAILURE;
    }

    unsigned int value = read_value_from_file(filename, position);
    printf("Value at position %zu: %u\n", position, value);

    const char *filename_prisoners = "prisoners.bin";
    make_initial_prison_file(filename_prisoners,10);

    swap_values_in_file(filename_prisoners,3,8);

    make_initial_prison_file("1m.bin",1000000);

    return 0;
}