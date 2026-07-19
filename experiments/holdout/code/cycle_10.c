#include "listlinier.h"
#include <stdio.h>
#include "cycle.h"
#include "Boolean.h"

/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
Address findCycleEntryPoint(List l){
    Address isi[length(l)+1];
    Address current = FIRST(l);
    boolean found = FALSE;
    int idxFound;
    int idx = 0;
    while (current != NULL && found == FALSE)
    {
        isi[idx] = current;
        if (idx > 0){
            for(int i = 0; i <= idx; i++){
                if(current == isi[i]){
                    found == TRUE;
                    idxFound = i;
                }
            }
        }
        current = current->next;
        idx++;
    }
    if(found){
        return isi[idxFound];
    }
    return NULL;
}


//  int main(){
//     List l;
//     int idx = 1;
//     CreateList(&l);

//     int n = 0;
//     int i = 0;

//     while(i < n){
//         ElType el;
//         scanf("%d", &el);
//         insertLast(&l, el);
//         i++;
//     }

    

//     displayList(l); printf("\n");  
// }