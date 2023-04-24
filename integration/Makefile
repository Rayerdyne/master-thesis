CC  := gcc
WINCXX := x86_64-w64-mingw32-g++
CFLAGS = -Wall

DLL = external.dll
DEF = $(patsubst %.dll,%.def, $(DLL))
DLL_OBJS = external.o
DLL_SRCS = $(patsubst %.o,%.cpp, $(DLL_OBJS))
DLL_DIR = /home/f/Unif/tfe/work/integration/
PROG = main
PROG_OBJS = main.o
PROG_SRCS = $(patsubst %.o,%.cpp, $(PROG_OBJS))
# $(WINCC) -o $@ $(PROG_OBJS) -L$(DLL_DIR) -Wl,-rpath=$(DLL_DIR) -ltestdll

$(PROG): $(DLL) $(PROG_OBJS)
	$(WINCXX) -o $@ $(PROG_OBJS) -B. -static-libgcc -static-libstdc++ -lexternal

$(DLL): $(DLL_OBJS)
	$(WINCXX) -shared -o $@ $(DLL_OBJS) -static-libgcc -static-libstdc++ -B. -ltensorflow 

external.o: external.cpp
	$(WINCXX) -c -o $@ $^ $(CFLAGS) -pie

$(PROG_OBJS): $(PROG_SRCS)
	$(WINCXX) -c -o $@ $^ $(CFLAGS)

clean:
	rm *.o