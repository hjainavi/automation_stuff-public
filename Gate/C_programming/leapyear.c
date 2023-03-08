#include <stdio.h>
void main() {
    int year=20001;

    if (((year % 4 == 0) && !(year % 100 ==0)) || (year%400 ==0)) {
        printf("year %d is a leap year\n",year);
    } else {
        printf("%d not a leap year\n",year);
    }
}