#include "listlinier.h"
#include "Boolean.h"
#include <stdlib.h>

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    List arr[20] = {NULL};
    Address p = l;
    while(p!=NULL){
        if(arr[((int)p)%20]!=NULL){
            Address p2 = arr[((int)p)%20];
            while(p2!=NULL){
                if(((int)p)==INFO(p2)){
                    return p;
                }
                p2 = NEXT(p2);
            }
            insertLast(&(arr[((int)p)%20]),((int)p));
            p = NEXT(p);
            continue;
        }
        else{
            CreateList(&(arr[((int)p)%20]));
            insertLast(&(arr[((int)p)%20]),((int)p));
            p = NEXT(p);
            continue;
        }

    }
    return NULL;
}