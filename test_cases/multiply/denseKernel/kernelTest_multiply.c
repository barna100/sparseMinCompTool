#include<stdio.h>
#define n 3

int main(){
  double A[n][n], B[n][n], C[n][n];
  int i, j, k;

  for(i=0; i<n; i++){
    for(j=0; j<n; j++)
      A[i][j] = 0;
      B[i][j] = 0;
      C[i][j] = 0;
  }
  A[0][0] = 9;
  A[0][2] = 5;
  A[1][1] = 8;
  A[1][2] = 1;
  A[2][0] = 5;

  B[0][2] = 1;
  B[1][1] = 1;
  B[1][2] = 9;
  B[2][0] = 5;

  for (i=0; i<n; i++)
    for(j=0; j<n; j++)
      for(k=0; k<n; k++)
        C[i][j] = C[i][j] + A[i][k] * B[k][j];

  for (i=0; i<n; i++)
    for(j=0; j<n; j++)
      printf("[%d %d] : %lf\n", i, j, C[i][j]);

  return 1;
}
