#include "cs.h"
/* print a sparse matrix; use %g for integers to avoid differences with csi */
csi cs_print (const cs *A, csi brief)
{
    csi p, j, m, n, nzmax, nz, *Ap, *Ai ;
    double *Ax ;
    if (!A) { printf ("(null)\n") ; return (0) ; }
    m = A->m ; n = A->n ; Ap = A->p ; Ai = A->i ; Ax = A->x ;
    nzmax = A->nzmax ; nz = A->nz ;
    for (j = 0 ; j < n ; j++)
    {
      for (p = Ap [j] ; p < Ap [j+1] ; p++)
      {
        printf ("[%d %d] : %lf\n", Ai[p], j, Ax[p]) ;
      }
    }
    return (1) ;
}
