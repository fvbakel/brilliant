#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>
#include <locale.h>

int main(int argc, char **argv) {
    setlocale(LC_NUMERIC, "");

    printf("\n");
    printf("size_t              %ld\n", sizeof(size_t));

    printf("bool                %ld\n", sizeof(bool));
    printf("short int           %ld\n", sizeof(short int));
    printf("unsigned short int  %ld\n", sizeof(unsigned short int));
    printf("char                %ld\n", sizeof(char));
    printf("unsigned int        %ld\n", sizeof(unsigned int));
    printf("int                 %ld\n", sizeof(int));
    printf("unsigned long       %ld\n", sizeof(unsigned long));
    printf("long unsigned int   %ld\n", sizeof(long unsigned int));
    printf("__uint32_t          %ld\n", sizeof(__uint32_t));

    printf("\n");
    printf("Max values:\n");
    printf("SHRT_MAX            %'d\n", SHRT_MAX);
    printf("USHRT_MAX           %'d\n", USHRT_MAX);
    printf("INT_MAX             %'d\n", INT_MAX);
    printf("UINT_MAX            %'u\n", UINT_MAX);
    printf("LONG_MAX            %'ld\n", LONG_MAX);
    printf("ULONG_MAX           %'lu\n", ULONG_MAX);

    unsigned int mem_in_gb = 1;
    unsigned int mem_in_mb = mem_in_gb * 1024;
    unsigned int mem_in_kb = mem_in_mb * 1024;
    unsigned int mem_in_bytes = mem_in_kb * 1024;

    printf("\n");
    printf("%'d GB of mem can hold %'ld unsigned int values\n",mem_in_gb,mem_in_bytes / sizeof(unsigned int));

    printf("\n");





}