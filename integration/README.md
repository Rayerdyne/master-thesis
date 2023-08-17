# Integration notes

**Important** the file [`vensim_external_functions.c`](vensim_external_functions.c), being shipped alongside Vensim DSS, is not be publicly disclosed. I also presume that it extends to [`external.cpp`](external.cpp)

I have been advise to put this repository private.

The license used for Vensim DSS is the one of my advisor, S. Quoilin.

## Cppflow

The library makes use of the [`cppflow`](https://github.com/serizba/cppflow) tool.

For installation, see [here](https://github.com/serizba/cppflow#how-to-run-it).

## Files

- `external.h`: header file for `external.cpp`
- `external.cpp`: main source file for the library
- `main.cpp`: code for running a test program
- `Makefile`: GNU make file for automating compilation