#include <stdio.h>
#include "cycle.h"
#include "listlinier.h"
#include "Boolean.h"

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l) {
    Address arr[10000];
    int idx = 0;
    Address p = FIRST(l);
    while (p != NULL) {
        if (idx==0) {
            arr[idx] = p;
            idx++;
            p = NEXT(p);
            continue;
        }


        for (int i=0; i<idx; i++) {
            if (p == arr[i]) {
                return p;
            }
        }

        arr[idx] = p;
        p = NEXT(p);
        idx++;
    }
    return NULL;
}
