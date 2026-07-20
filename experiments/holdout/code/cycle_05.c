#ifndef CYCLE_H
#define CYCLE_H
#include "listlinier.h"
#include "Boolean.h"
#include <stdio.h>

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    if(length(l)<=100000){
        return NULL;
    }
    Address p = l;
    for(int i=0; i<length(l); i++){
        Address cek = l;
        for(int j=0; j<i; j++){
            if(NEXT(p) == cek){
                return cek;
            }
            cek = NEXT(cek);
        }
        p = NEXT(p);
    }
}

#endif