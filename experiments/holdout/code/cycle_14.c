#include "cycle.h"
#include <stdlib.h>
#include <stdio.h>

int find(Address arrAdd[], int n, Address val) {
    for (int i = 0; i < n; i++) {
        if (arrAdd[i] == val) return i;
    }
    return -1;
}


Address findCycleEntryPoint(List l) {
    Address addr[100000];
    int i = 0;
    while (l != NULL) {
        addr[i++] = l;
        l = l->next;
        int found = find(addr, i, l);
        if (found != -1) return addr[found];
    }
}


// int main() {
//     int n, val; scanf("%d", &n);
//     List *l; CreateList(l);
//     for (int i = 0; i < n; i++) {
//         scanf("%d", &val);
//         insertLast(l, val);
//     }

//     Address coba = (*l);
//     Address loop;
//     for (int i = 0; i < n; i++) {
//         printf("i = %d, addr = %p\n", i, coba);
//         coba = coba->next;
//         if (i == n - 3) {
//             loop = coba;
//             printf("loop = %d, addr = %p\n", i, loop);
//         }
//     }
//     Address ketemu = findCycleEntryPoint(*l);
//     printf("K = %p\n", ketemu);
// }