#include<stdio.h>
#define n 3

int main(){
  double A[n][n], x[n];
  int i, j;

  for(i=0; i<n; i++){
    for(j=0; j<n; j++)
      A[i][j] = 0;
  }
  A[0][0] = 1;
  A[1][0] = 2;
  A[1][1] = 3;
  A[2][0] = 3;
  A[2][1] = 4;
  A[2][2] = 5;

  for(i=0; i<n; i++)
    x[i] = i*2;

  for (i=0; i<n; i++){
    for(j=0; j<i; j++)
      x[i] = x[i] - A[i][j] * x[j];
    x[i] = x[i] / A[i][i];
  }
  
  for (i=0; i<n; i++)
      printf("[%d] : %lf\n", i, x[i]);
  return 1;
}
