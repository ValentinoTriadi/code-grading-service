#include "cycle.h"
#include <stdio.h>
#include <stdbool.h>

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l) {
    Address r[100000];
    Address p = FIRST(l);
    int lengthListR = 0;
    while (p != NULL) {
        bool found = false;
        for (int i = 0; i < lengthListR && !found; i++) {
            if (p == r[i]) {
                return p;
            }
        }
        if (found == false) {
            r[lengthListR] = p;
            lengthListR++;
            p = NEXT(p);
        }
    }
    return NULL;
}