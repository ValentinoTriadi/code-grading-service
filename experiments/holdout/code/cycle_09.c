#ifndef CYCLE_H
#define CYCLE_H
#include "listlinier.h"
#include "Boolean.h"
#include "stdlib.h"

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    Address p = l;
    int len = length(l);
    int a[len];
    for (int i=0; i< len; i++){
        a[i]= p;
        p= p->next;
    }
    int count;
    for (int i=0; i< len; i++){
        for (int j=0;j< len; j++){
            if (i!= j){
                if (a[i]==a[j]){
                    return a[i];
                }
            }
        }
    }
    return NULL;

};

#endif