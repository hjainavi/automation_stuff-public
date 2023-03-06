#include <stdio.h>
void main() {
    // sum of numbers
    int m;
    int n;
    scanf("%d",&m);
    scanf("%d",&n);
    if (m%n==0) {
        printf("%d\n",m/n);
    } else {
        printf("0\n");
    }

}