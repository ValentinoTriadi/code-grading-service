#include "listlinier.h"
#include "Boolean.h"
#include "stdlib.h"
#include "stdio.h"

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    int found = 1;
    Address temp = l;
    int arr[100005];
    int pos = 0;
    Address res = NULL;

    while(temp != NULL){
        // -1 berarti sudah diikunjungi
        if( INFO(temp) == -1 ){
            res = temp;
        }

        arr[pos] = INFO(temp);
        INFO(temp) = -1;
        pos++;
        temp = temp->next;
    }

    if( res == NULL ){
        return NULL;
    }

    pos = 0;
    temp = l;
    int count = 0;
    while(count < 2){
        // -1 berarti sudah diikunjungi
        if( temp == res ) count++;
        
        if( temp < 2 ){
            if( INFO(temp) == -1 ){
                res = temp;
            }

            arr[pos] = INFO(temp);
            INFO(temp) = arr[pos];
            pos++;
        }
        temp = temp->next;
    }
    return temp;
}

// int main(){
//     printf("doen");
//     Address a1 = newNode(1);
//     Address a2 = newNode(2);
//     Address a3 = newNode(3);
//     Address a4 = newNode(4);
//     Address a5 = newNode(4);
//     Address a6 = newNode(4);
//     a1->next = a2;
//     a2->next = a3;
//     a3->next = a4;
//     a4->next = a5;
//     a5->next = a6;
//     a6->next = a3;
//     List l; CreateList(&l);
//     l = a1;
//     printf("%d", INFO(findCycleEntryPoint(l)));
// }