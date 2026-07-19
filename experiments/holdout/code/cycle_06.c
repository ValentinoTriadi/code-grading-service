#include "listlinier.h"
#include <stdio.h>
#include <stdlib.h>
/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    List curr = l;
    while ((curr!=NULL))
    {
        int found = 0;
        List debug = curr->next;
        while (debug != NULL)
        {
            if(debug == curr) return debug;
            debug = debug->next;
        }
        
        curr = curr->next;
    }
    return NULL;
}