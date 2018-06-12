EXEC = spTest_gaxpy
CF = $(CFLAGS) $(CPPFLAGS) $(TARGET_ARCH) -O
I = -I../Include

LDLIBS += -lm
CS = $(LDFLAGS) ../Lib/libcsparse.a $(LDLIBS)

IP = 3_3_5_1.ip

Row = 3

Col = 3

all: lib $(EXEC)

lib:
	( cd ../Lib ; $(MAKE) )

$(EXEC): lib $(EXEC).c Makefile
	$(CC) $(CF) $(I) -o $(EXEC) $(EXEC).c $(CS)

run:
	./$(EXEC) $(Row) $(Col) $(IP)

clean:
	- $(RM) *.o

purge: distclean

distclean: clean
	- $(RM) -r $(EXEC) *.a *.dSYM *.obj *.dll
