EXEC = spTest_add
CF = $(CFLAGS) $(CPPFLAGS) $(TARGET_ARCH) -O
I = -I../Include

LDLIBS += -lm
CS = $(LDFLAGS) ../Lib/libcsparse.a $(LDLIBS)

IP1 = 3_3_5_1.ip

IP2 = 3_3_4_1.ip

all: lib $(EXEC)

lib:
	( cd ../Lib ; $(MAKE) )

$(EXEC): lib $(EXEC).c Makefile
	$(CC) $(CF) $(I) -o $(EXEC) $(EXEC).c $(CS)

run:
	./$(EXEC) $(IP1) $(IP2)

clean:
	- $(RM) *.o

purge: distclean

distclean: clean
	- $(RM) -r $(EXEC) *.a *.dSYM *.obj *.dll
