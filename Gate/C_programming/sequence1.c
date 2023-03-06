#include <stdio.h>
void main() {
    // get output till -1 and print length of longest increasing sub sequence
    int length = 0;
    int maxlen = 0;
    int pre;
    int curr;
    scanf("%d",&pre);
    if (!(pre == -1)) {
        length = 1;
        scanf("%d",&curr);
        while ( !(curr == -1)) {
            if ( pre < curr ) {
                // extend sequence
                length = length + 1;
            } else {
                if (maxlen < length) {
                // longer sub sequence found
                    maxlen = length;
                }
                // reset sequence
                length = 1;
            }
            pre = curr;
            scanf("%d",&curr);
        }
    }
    // no resets in between , sequence increasing from start
    if (maxlen < length) {
        maxlen = length;
    }
    printf("length = %d\n",maxlen);
}