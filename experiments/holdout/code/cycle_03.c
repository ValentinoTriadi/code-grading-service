#include "listlinier.h"
#include "Boolean.h"

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    int a = length(l);
    int b[a];
    for(int i = 0; i < a; i++){
        b[i] = getElmt(&l, i);
    }
    int target = -1;
    for(int i = 0; i < a-1; i++){
        if(b[i] > b[i+1]){
            target = b[i];
            break;
        }
    }
    Address p;
    for(int i = 0; i < a; i++){
        if(b[i] == target){
            p = i;
            break;
        }
    }

    return p;
}