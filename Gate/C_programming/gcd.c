#include <stdio.h>
void main() {
    // gcd of numbers
    int a;
    int b;
    int swap;
    scanf("%d",&a);
    scanf("%d",&b);
    // loop invariant GCD(A,B) == GDC(a,b) (original input and changed a and b thru the loop)
    while (!(a%b == 0)) {
        printf("a = %d;",a);
        printf("b = %d;",b);
        printf("a mod b = %d\n",a%b);

        swap = a;
        a = b;
        b = swap%b;
    }
    printf("gcd is %d\n",b);
}