#include<stdio.h>
#define N 5

int main(){

int i;
int valA[5]={9,5,8,1,5};
int valB[4]={1,1,9,5};
int valC[N]={0,0,0,0,0};

valC[0]=valA[0];
valC[1]=valA[1]+valB[0];
valC[2]=valA[2]+valB[1];
valC[3]=valA[3]+valB[2];
valC[4]=valA[4]+valB[3];

for(i=0; i<N; i++)
  printf("valC[%d] : %d\n", i, valC[i]);

return 1;
}
