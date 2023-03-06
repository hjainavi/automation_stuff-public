#include <stdio.h>
void main() {
    // sum of numbers
    int a;
    scanf("%d",&a);
    int sum = 0;
    while (!(a == -1)) {
        sum = sum + a;
        scanf("%d",&a);
    }
    printf("sum = %d\n",sum);
}