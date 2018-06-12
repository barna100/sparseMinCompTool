#include<stdio.h>
#define n 3

int main(){
  double x[n], y[n];
  double A[n][n];
  int i, j;

  for(i=0; i<n; i++){
    for(j=0; j<n; j++)
      A[i][j] = 0;
  }
  A[0][0] = 9;
  A[0][2] = 5;
  A[1][1] = 8;
  A[1][2] = 1;
  A[2][0] = 5;

  for(j=0; j<n; j++){
    x[j] = j+1;
    y[j] = 0;
  }
  

  for (i=0; i<n; i++)
    for(j=0; j<n; j++)
      y[i] = A[i][j] * x[j] + y[i];

  for (i=0; i<n; i++)
      printf("[%d] : %lf\n", i, y[i]);
  return 1;
}
