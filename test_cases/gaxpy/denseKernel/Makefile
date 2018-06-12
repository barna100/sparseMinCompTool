EXEC = kernelTest_gaxpy

all:
	gcc $(EXEC).c -o $(EXEC)

run:
	./$(EXEC)

clean:
	- $(RM) *.o

purge:
	distclean

distclean:
	clean
	- $(RM) -r $(EXEC) *.a *.dSYM *.obj *.dll
