#include <stdio.h>
#include "cycle.h"
#include "listlinier.h"
#include <stddef.h>

Address findCycleEntryPoint(List l){
    List new;
    CreateList(&new);
    Address p = l;
    int found = 0;
    Address x;
    while(p != NULL && !found){
        Address q = new;
        while(q != NULL){
            if(INFO(q) == INFO(p)){
                // printf("%d\n",INFO(p));
                found = 1;
                x = p;
                break;
            }
            q = NEXT(q);
        }
        insertLast(&new, INFO(p));
        p = NEXT(p);
        if(found){
            break;
        }
    }
    if(found){
        return x;
    }else{
        return NULL;
    }
}

// int main(){
//     Node n1,n2,n3, n4;
//     n1.info = 1; n1.next = &n2;
//     n2.info = 2; n2.next = &n3;
//     n3.info = 3, n3.next = &n4;
//     n4.info = 4; n4.next = &n2;
//     Address l = &n1;
//     findCycleEntryPoint(l);
// }