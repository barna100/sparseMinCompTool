#include "cs.h"
int main (int argc, char **argv)
{
    cs *T, *A, *B, *C ;
    csi m ;    
    FILE *f1;
    double *x, *y;
    int i;
    int row = atoi(argv[argc-3]);
    int col = atoi(argv[argc-2]);
    f1 = fopen(argv[argc-1],"r");	
    T = cs_load (f1) ;               /* load triplet matrix T from stdin */
    A = cs_compress (T) ;               /* A = compressed-column form of T */
    cs_spfree (T) ;                     /* clear T */
    x = cs_malloc(col,sizeof(double));
    for (i=0; i<col; i++){
	*(x+i) = i*2;
    }
    cs_lsolve (A, x) ;   
//    printf ("A:\n") ; cs_print (A, 0) ; /* print A */
    for (i=0; i<col; i++)
	printf("[%d] : %lf\n", i, *(x+i));
    cs_spfree (A) ;                     
    return (0) ;
}
