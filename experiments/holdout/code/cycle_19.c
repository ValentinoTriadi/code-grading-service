#include "listlinier.h"
#include "Boolean.h"
#include <stdio.h>

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l) {
    if (l == NULL) {
        return NULL;
    }
    else if (INFO(l) == -123456789) {
        return l;
    }
    ElType temp = INFO(l);
    INFO(l) = -123456789;
    Address ret = findCycleEntryPoint(NEXT(l));
    INFO(l) = temp;
    return ret;
}