#include<stdio.h>
#define N 3

int main(){

int i;
int valA[5]={9,5,8,1,5};
int X[3]={1,2,3};
int valY[3]={0,0,0};

valY[0]=valA[0]*X[0]+valA[1]*X[2]+valY[0];
valY[1]=valA[2]*X[1]+valA[3]*X[2]+valY[1];
valY[2]=valA[4]*X[0]+valY[2];

for(i=0; i<N; i++)
  printf("valY[%d] : %d\n", i, valY[i]);

return 1;
}

