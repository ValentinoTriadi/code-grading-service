
#include "listlinier.h"
#include "Boolean.h"

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    List l2;
    CreateList(&l2);
    Address p = l;
    insertFirst(&l2, p);
    for(int i = 0; i < length(l); i++){
        if(indexOf(l2, p) == IDX_UNDEF){
            insertLast(l2, NEXT(p));
            p = NEXT(p);
        }
        else{
            return p;
        }
    }
    return NULL;
}
