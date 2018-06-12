#include "cs.h"
int main (int argc, char **argv)
{
    cs *T, *A, *B, *C ;
    csi i, m ;    
    FILE *f1;
    f1 = fopen(argv[argc-2],"r");	
    T = cs_load (f1) ;               /* load triplet matrix T from stdin */
    A = cs_compress (T) ;               /* A = compressed-column form of T */
    cs_spfree (T) ;                     /* clear T */
    f1 = fopen(argv[argc-1],"r");	
    T = cs_load (f1) ;               /* load triplet matrix T from stdin */
    B = cs_compress (T) ;               /* A = compressed-column form of T */
    cs_spfree (T) ;                     /* clear T */
    C = cs_add (A, B, 1, 1) ;   
    printf ("A:\n") ; cs_print (A, 0) ; /* print A */
    printf ("B:\n") ; cs_print (B, 0) ; /* print B */
    printf ("C:\n") ; cs_print (C, 0) ; /* print C */
    cs_spfree (A) ;                     
    cs_spfree (B) ;                     
    cs_spfree (C) ;
    return (0) ;
}
