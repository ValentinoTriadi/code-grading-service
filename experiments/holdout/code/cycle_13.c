#include "listlinier.h"
#include "Boolean.h"
#include <stdio.h>
/**
 * I.S. List l terdefinisi
 * F.S. Mengembalikan address node yang merupakan entrypoint dari cycle
 * Jika tidak ada cycle, kembalikan NULL
 */
int searching(Address arr[], Address check, int cnt){
    for (int i = 0; i <= cnt; i++)
    {
        if (arr[i] == check)
        {
            return 1;
        }
    }
    return 0;
}
Address findCycleEntryPoint(List l){
    Address satu[100];
    int count = 0;
    Address point = l;
    while (point != NULL)
    {
        if (searching(satu, point, count))
        {
            return point;
        }
        satu[count++] = point;
        point = NEXT(point);
    }
    return NULL; 
}  

//  int main(){
//      List l;
//      CreateList(&l);
//      insertFirst(&l, 1);
//      insertLast(&l, 2);
//      insertLast(&l, 3);
//      insertLast(&l, 4);
//      insertLast(&l, 2);

//      removeAll(&l, 2);
//      displayList(l);
//  }