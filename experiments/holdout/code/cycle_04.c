#include <stdio.h>
#include "cycle.h"

Address findCycleEntryPoint(List l){
    /*
    Address curr = FIRST(l);
    Address prev = NULL;
    int max = -1;
    int count = 0;
    while(NEXT(curr) != NULL){
        prev = curr;
        curr = NEXT(curr);
        if(INFO(prev) == INFO(curr)){
            count++;
        }
        if(count > max){
            max = count;
        }
    }
        */
    Address p = FIRST(l);
    while(p != NULL){
        if(INFO(NEXT(p)) == 999){
            return NEXT(p);
        } else {
            int index = indexOf(l, INFO(p));
            setElmt(&l, index, 999);
            p = NEXT(p);
        }
    }
    return NULL;
}