#include<stdio.h>
#define n 3

int main(){
  double A[n][n], B[n][n];
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

  for (i=0; i<n; i++)
    for(j=0; j<n; j++)
      B[j][i] = A[i][j];

  for (i=0; i<n; i++)
    for(j=0; j<n; j++)
      printf("[%d %d] : %lf :: [%d %d] : %lf \n", i, j, A[i][j], i, j, B[i][j]);
  return 1;
}
