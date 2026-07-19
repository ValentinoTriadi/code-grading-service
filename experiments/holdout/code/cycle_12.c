#include "cycle.h"
#include "listlinier.h"
#include <stdio.h> 
#include <stdlib.h> 

Address findCycleEntryPoint(List l){
    Address a = FIRST(l);
    while (a != NULL){
        if (NEXT(a) == NULL){
            return NULL;
        }
        Address slow = NEXT(a);
        if (NEXT(slow) == NULL){
            return NULL;
        }
        Address fast = NEXT(slow);
        while(slow != fast && fast != NULL){
            if (NEXT(fast) == NULL){
                return NULL;
            }
            if (fast == a){
                return a;
            }
            fast = NEXT(NEXT(fast));
            slow = NEXT(slow);

        }

        a = NEXT(a);
    } 
}