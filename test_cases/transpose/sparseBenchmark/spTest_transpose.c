#include "cs.h"
int main (int argc, char **argv)
{
    cs *T, *A, *AT;
    csi i, m ;    
    FILE *f1;
    f1 = fopen(argv[argc-1],"r");	
    T = cs_load (f1) ;               /* load triplet matrix T from stdin */
    A = cs_compress (T) ;               /* A = compressed-column form of T */
    cs_spfree (T) ;                     /* clear T */
    AT = cs_transpose (A, 1) ;
    printf ("A:\n") ; cs_print (A, 0) ; /* print A */
    printf ("AT:\n") ; cs_print (AT, 0) ; /* print C */
    cs_spfree (A) ;                     
    cs_spfree (AT) ;                     
    return (0) ;
}
