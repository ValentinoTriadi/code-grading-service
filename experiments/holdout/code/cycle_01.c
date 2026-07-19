#include "listlinier.h"
#include "Boolean.h"
#include <stdio.h>

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    Address list[100000];
    Address Q = FIRST(l);
    int idx = 0;
    list[idx] = Q;
    while (Q != NULL){
        for(int i =0; i <=idx; i++){
            if (next(Q)==list[i]) return list[i];
            ++idx;
            list[idx]=next(Q);
            Q=next(Q);
        }
    }
    return NULL;
}
