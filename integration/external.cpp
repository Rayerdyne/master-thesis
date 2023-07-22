/**
 * @file external.cpp
 * @author François Straet
 * @brief Main file for the external library.
 * Edited from `vensim_external_functions.c`
 * 
 */
#include "external.h"

#include <cppflow/cppflow.h>

#define WANT_WINDOWS_INCLUDES /* the sample implementation of this requires windows includes/libraries */
#define VENEXT_GLOBALS
#include "./vensim.h"

#ifdef unix
#include <string.h>
#include <stdlib.h>
#else
#include <malloc.h>
#endif

/* custom imports */
#include <math.h>
#include <array>
#include <cstdio>
#include <iomanip>
#include <iterator>
#include <limits>
#include <math.h>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include <windows.h>

static const std::string MODEL_DIR_NAME = "model";
static std::unique_ptr<cppflow::model> model_ptr;

std::string exec(const char *);
GLOB_VARS *VENGV = NULL; /* the value for this is set by set_gv below */


/*******************************************
 1 - function ids - used to swich between choices
 *******************************************/

#define COMPUTE_A_FUNC 0
#define COMPUTE_DS_APPROX_FUNC 1

/*******************************************
 2 - function prototypes
*******************************************
each external function is prototyped here
arguments can reasonably be doubles - for normal number manipulation,
COMPREAL * for vector manipulation or int for indexing.  Recasting of
values takes place in
Note that if you use more than 1 file for the external function definitions
you should probably put these prototypes into a #include file.  Also, for
working with compiled simulation a # include file is helpfule, and should
be nested into vensim.h

Note that all the external functions are all upper case.  This is required
if you want to use compile simulations - since the calls in mdl.c will
be upper case.  Our apologies to those this offends.
*********************************************/
// see external.h

/****************************************************
 3 - Grouping of functions in a structure - see venext.h
 ***********************************************************/

static FUNC_DESC Flist[] = {
					{"COMPUTE_A"," {x} , {y} , {z} ",3,0,COMPUTE_A_FUNC,0,0,0,0},
					{"DISPASET_APPROXIMATOR"," {CapacityRatio} , {ShareFlex} , {ShareStorage} , {ShareWind} , {SharePV} , {rNTC} , {out_idx} ",7,0,COMPUTE_DS_APPROX_FUNC,0,0,0,0},
					{NULL,0,0,0} };


 /****************************************************************
  5 External function definitions
  ****************************************************************/

int VEFCC version_info() {
    return EXTERNAL_VERSION;
}

unsigned short VEFCC funcversion_info() {
    return 1;
}

int VEFCC set_gv(GLOB_VARS *vgv) {
	VENGV = vgv;

    // TODO: add cool stuff

	if (!VENGV
		|| VENGV->vgv_magic_start != VGV_MAGIC_START
		|| VENGV->vgv_magic_end != VGV_MAGIC_END)
	{
		return 0;
	}
	return 1;
}

/* ****************************
 This function is _exported and called multiple times at Vensim
 startup with an index  - it returns 1 on success and 0 to
 indicate the end of the function list.  For convenience the structure
 defined in section 3 is used, but all the functions could also be declared
 with a switch statement on i
*****************************************************************/

int VEFCC user_definition(
	int i, /* an index for requesting information - this is mapped to Flist
			  but could be used another way - vensim repeatedly calls
			  user_definition with i bigger by 1 until user_definition returns
			  0 */
	unsigned char **sym,/* the name of the function to be used in the Vensim model */
	unsigned char **argument_desc, /* description of arguments to be used by the function */
	int *num_arg, /* the number of arguments (in Vensim) the function takes
					 note that for user loop functions this will be one less
					 than the number of arguments the function actually takes on */
	int *num_vector, /* the number of arguments that are passed as real number vectors */
	int *func_index, /* a number between 0 and 254 that identifies the function
						vensim_external is called with this number */
	int *dim_act,  /* reserved - for doing dimensional analysis but not implemented */
	int *modify,  /* a flag to indicate that the function will modify value that
					 are passed to it -
					 0 is a normal function that does not modify its argument
					 1 is a function that does modify arguments
					 2 is a function that modifies arguments and serves as a solver
					   of a simultaneous set of conditions as FIND_ZERO */
	int *num_loop, /* the number of loops that are managed by the function -
					  this is nonzero (normally 1 or 2) for a function that
					  needs to return a vector or matrix of values - if this is
					  nonzero Vensim will put a pointer to the vector or array to
					  be filled in and pass it as the first argument to the function
					  NOTE use -1 for a constdef function and -2 for a datadef function */

	int *num_literal, /* the number of literals that are passed to the function -
						 arguments are always passed in the order literals,
						 lookups, vectors, numbers - if num_loop is set the
						 first argument is a vector even if num_literal is positive */
	int *num_lookup  /* the number of lookup functions passed - this structure is
						not currently accessible but will be made so in the future */
)
{
	if (Flist[i].sym)
	{
		*sym = (unsigned char *)Flist[i].sym;
		*argument_desc = (unsigned char *)Flist[i].argument_desc;
		*num_arg = Flist[i].num_args;
		*num_vector = Flist[i].num_vector;
		*func_index = Flist[i].func_index;
		*dim_act = 0;
		*modify = Flist[i].modify;
		*num_loop = Flist[i].num_loop;
		*num_literal = Flist[i].num_literal;
		*num_lookup = Flist[i].num_lookup;
		return(1);
	}
	return(0); /* indicating the end of the list */
}

/***************************
 5a some memory management utility routines used by the examples that
	may be of value for other functions - note different routines
	to use Windows GlobalAlloc etc or just calloc etc
  ***************************************/

static HANDLE *Mem_used = NULL;
static int Num_mem_used = 0;
static int Max_mem_used = 0;

static void *vext_allocate(unsigned nbytes, HANDLE *hndl) {
	HANDLE lhndl;
	if (Num_mem_used >= Max_mem_used) {
		Max_mem_used += 100;
		if (Mem_used) {
			Mem_used = (HANDLE *)realloc(Mem_used, Max_mem_used * sizeof(HANDLE));
			memset(Mem_used + Max_mem_used - 100, '\0', 100 * sizeof(HANDLE));
		}
		else {
			Mem_used = (HANDLE *)calloc(Max_mem_used, sizeof(HANDLE));
		}
	}

	if (!Mem_used) {
		return NULL;
	}

	lhndl = (HANDLE)malloc(nbytes);

	if (!lhndl) {
		return NULL;
	}

	if (hndl) {
		*hndl = lhndl;
	}

	Mem_used[Num_mem_used++] = lhndl;
	return(lhndl);
}


static void *vext_reallocate(unsigned nbytes, HANDLE *hndl) {
	int i = 0;

	if (!*hndl) {
		return(vext_allocate(nbytes, hndl));
	}

	if (Mem_used) {
		/* find old - otherwise live with the memory leak */
		for (i = 0; i < Num_mem_used; i++) {
			if (Mem_used[i] == *hndl) {
				break;
			}
		}
	}

	*hndl = realloc(*hndl, nbytes);

	if (Mem_used) {
		if (i < Num_mem_used) {
			Mem_used[i] = *hndl;
		}
	}
	return(*hndl);
}


static void vext_clearmem() {
	int i;

	if (Mem_used) {
		for (i = 0; i < Num_mem_used; i++) {
			if (Mem_used[i]) {
				free(Mem_used[i]);
			}
		}
		free(Mem_used);
	}

	Mem_used = NULL;
	Num_mem_used = Max_mem_used = 0;

	// Matrix_invert_maxn = 0;
	// Internal_ror_fror = NULL;
}

/*********************************************************************
 6 - startup and shutdown routines
 *********************************************************************
	these two functions (if they exist and are exported)
	are called before the simulation starts and
	after it ends - in a normal simulation the order is
	   simulation_setup(1) ;
	   simulation_setup(0) ;
	   simulation_shutdown(0) ;
	   simulation_shutdown(1) ;
	for an optimization it the middle two calls are repeated for
	every simulation - the setup routine should return 0 on failure
	the return value is only used when iniflag == 1.  If the function
	returns 0 simulation will not proceed.
 ******************************************************************/

/**
 * @brief Vensim simulation setup function
 * 
 * On initializing the simulation, load the model that is expected to be placed in the same
 * directory than the dll, and be named according to MODEL_DIR_NAME.
 * 
 * @param iniflag 
 * @return CFUNCTION 
 */
CFUNCTION int VEFCC simulation_setup(int iniflag) {
    if (iniflag == 1) {
        /*
         * Getting this dll path at run time
         * Copied from https://stackoverflow.com/a/6924332
         */
        char this_path[512];
        HMODULE hm = NULL;

        if (GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | 
                GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                (LPCSTR) &version_info, &hm) == 0) {
            int ret = GetLastError();
            std::cerr << "GetModuleHandle failed, error = " << ret << std::endl;
        }
        if (GetModuleFileName(hm, this_path, sizeof(this_path)) == 0) {
            int ret = GetLastError();
            std::cerr << "GetModuleFileName failed, error = " << ret;
        }

        std::string sthis_path(this_path);
        int idx = sthis_path.rfind('\\');
        std::string model_path = sthis_path.substr(0, idx+1) + MODEL_DIR_NAME;        

        model_ptr.reset(new cppflow::model(model_path));
    }
	return 1;
}

/**
 * @brief Vensim simulation shutdown function
 * 
 * Frees the model loaded during simulation setup 
 * 
 * @param finalflag 
 * @return CFUNCTION 
 */
CFUNCTION int VEFCC simulation_shutdown(int finalflag) {
    if (finalflag == 1) {
        model_ptr.reset(nullptr);
    }
	vext_clearmem();
	return 1;
}

/*********************************************************************
 7 - vensim_external - the actual external function call
 *********************************************************************
   note that all the functions doing floating point are passed and
   return doubles to prevent any compiler specific problems from
   arising
 ******************************************************************/

CFUNCTION int VEFCC vensim_external(VV *val, int nval, int funcid)
{
	double rval;

	switch (funcid)
	{
	case COMPUTE_A_FUNC: /* simple function - call with double return double */
		rval = compute_a(val[0].val, val[1].val, val[2].val);
		break;
    
    case COMPUTE_DS_APPROX_FUNC:
        rval = compute_ds_approx(val[0].val, val[1].val, val[2].val, val[3].val, val[4].val, val[5].val, val[6].val);
        break;

	default:
		return(0); /* indicate an error condition to Vensim */
	}

	/* set val[0], this value will be used in the equation output */
	val[0].val = (COMPREAL) rval;
	return 1; /* a 1 return value signals vensim of successful completetion */
}

/*************************************************************************
 8 - actual function bodies - these could be a separate file
 *************************************************************************
 actual function bodies are all set up to use and return doubles
 (except when acting on vectors) this aids portability across different
 platforms and compilers as the C standard for floating point argument
 passing uses doubles.
 *************************************************************************/

constexpr auto max_precision {std::numeric_limits<long double>::digits10 + 1}; 

double compute_a(double a, double b, double c) {


    int aint = static_cast<int>(round(a));
    if (aint == 0) {
        VENGV->error_message(8, (unsigned char *) "Hem error message");
    }

    return a + b + c;
}

double compute_ds_approx(double CapacityRatio, double ShareFlex, double ShareStorage, double ShareWind, double SharePV, double rNTC, double output_idx) {

    if (CapacityRatio <= 0.5 || 1.8 <= CapacityRatio ||
        ShareFlex <= 0.01    || 0.90 <= ShareFlex    ||
        ShareStorage <= 0.0  || 0.5 <= ShareStorage  ||
        ShareWind <= 0.0     || 0.5 <= ShareWind     ||
        SharePV <= 0.0       || 0.5 <= SharePV       ||
        rNTC <= 0.0          || 0.7 <= rNTC) {
        
        VENGV->error_message(WARNING, (unsigned char *) "Input of Dispa-SET approximator out of range, weird output to be expected");
    }

    std::vector<float> data = { CapacityRatio, ShareFlex, ShareStorage, ShareWind, SharePV, rNTC };
    auto input = cppflow::tensor(data, {1, 6});
    // auto output = model_ptr->operator()(input);

    std::vector<cppflow::tensor> output = model_ptr->operator()({{"serving_default_normalization_input:0", input}}, 
                                                                {"StatefulPartitionedCall:0"});

    int idx = (int) round(output_idx);
    auto res = output[0].get_data<float>()[idx];

    return res;
}