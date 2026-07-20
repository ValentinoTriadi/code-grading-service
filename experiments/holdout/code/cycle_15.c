#include "cycle.h"
#include "listlinier.h"
#include <stdio.h>

Address findCycleEntryPoint(List l){
    Address temp = FIRST(l);
    int counterTemp = 0;
    while(temp != NULL){
        Address first = FIRST(l);
        int counterFirst = 0;
        while(first != temp && first != NULL){
            counterFirst++;
            first = NEXT(first);
        }
        // printf("counterTemp: %d; counterFirst: %d\n", counterTemp, counterFirst);
        if(counterTemp != counterFirst){
            return temp;
        }
        counterTemp++;
        temp = NEXT(temp);
    }
    return NULL;
}

// int main(){
//     List l1;
//     CreateList(&l1);
//     printf("hit\n");
//     insertLast(&l1, 1);
//     printf("hit\n");
//     insertLast(&l1, 2);
//     insertLast(&l1, 3);
//     printf("hit\n");
//     insertLast(&l1, 4);
//     Address temp = FIRST(l1);
//     for(int i = 0; i < 1; i++){
//         temp = NEXT(temp);
//     }
//     printf("hit\n");
//     Address tempL1 = FIRST(l1);
//     while(NEXT(tempL1) != NULL){
//         printf("tempL1 info: %d; address:%p\n", INFO(tempL1), tempL1);
//         tempL1 = NEXT(tempL1);
//     }
//     printf("tempL1 info: %d; address:%p\n", INFO(tempL1), tempL1);
//     printf("hit\n");
//     printf("Address tempL1: %p; temp: %p\n", tempL1, temp);
//     NEXT(tempL1) = temp;
//     printf("hit\n");
//     Address result = findCycleEntryPoint(l1);
//     printf("result info: %d; address: %p\n", INFO(result), result);
//     return 0;
// }