/****************************************************************************
   extern.c -  Version 5.8c
   Copyright (c) 1992-2005 Ventana Systems, Inc.
   Example external function file definitions for use
   with Vensim

  Background:

  At their simplest external functions are simply mathematical routines
  that do things it is hard to do in Vensim.  In practice, however, most
  of the value of external functions comes from the ability to do
  programming language things.  In particular loops, iterations and
  conditional computation.  Thus there are a number of different
  attributes an external function can have.

  1. Use only floating point numbers as inputs and output a floating point
	 number.

  2. Use a combination of floating point numbers and vectors (or arrays)
	 of values to output a floating point number.  External functions can
	 also take string variables and Lookups as arguments.

  3. Take over control of for variable loops from Vensim.

  4. Directly modify arguments passed as vectors.

  Of these number 1 is straightforward and is illustrated by the COSINE
  and INRANGE functions included here.  2 is straghtforward if you follow
  the example of the PSUM and MYMESSAGE function included here.  3 is tricky
  because the example of the Vensim function has 1 less argument than the
  real function, but should not cause problem if you follow example of the
  MATRIX_INVERT function included here.

  A special note on number 2 is that you can also use this function to
  create a simultaneous equation solver using your own solution algorithm.
  MYFINDZERO is an example of this.

  Number 4 is dangerous.  Vensim loses control of equation ordering and
  you can get unexpected results.  Use this only if you have to.  The
  MATRIX_INPLACE_INVERT function does this.  Be careful to study the model
  (venext.mdl) shipped with these examples.

  The rest of this file is broken up into 7 sections.  If you have more than
  a few functions, you should probably take section 2 and put it into a .h
  file.  Section 7 can be put in a separate file (or files) and the .h file
  included in thse files.  You most likely do not need to include <windows.h>
  in the other files (but <math.h> is a good idea.


  COMPILER NOTES

  Most of the development and testing of Vensim occurs using Microsoft
  compilers.  Visual C/C++

  If you want to write external functions in C plus plus you can rename this
  file to venext.cpp and everything should work OK.

  Note that you must include venext.def to get this all to work in your
  project (under Windows).

  CONFIGURATION NOTES

  Vensim's external functions can be used with Vensim DSS, Vensim Runtime,
  Vensim Application Runtime and the DLLs with the exception of the minimal
  DLL. In order to have external functions loaded in Application Runtime or
  the DLLs you will need to execute the command

	  SPECIAL>READINI|inifile.ini

  where inifile.ini contains the line

	  ExternalFunctionLibrary=c:\program files\vensim\comp\venext.dll

  set the path appropriate for where you have located you function library.
  There is no need to call the file venext.dll - any name will do.

  When you create your external function library you need to link with the
  .lib file associated with the program that will call your external functions.
  For Vensim DSS this is vensim.lib. For the Vensim DLL it is vendll32.lib
  and so on. If you do not do this loading the external functions will likely
  fail, possibly with a message that the application is not properly installed.


  PLATFORM NOTES

  Linux

  Standard C files such as this should work fine under Linux using shared
  object libraries. The sample make file venextun.mak can be used to build
  the shared object libary - alternatively just use the command

  gcc -shared venext.c -olibvenext.so

  because of the way Linux does runtime linking there is no need to reference
  the vensim symbols during compilation - references will be resolved at
  runtime.

  The format for indicating where to find the external function library
  is the same as on Windows - use the SPECIAL>READINI command. The path
  should follow Unix naming conventions eg

	 ExternalFunctionLibrary=/home/bob/newven/comp/libvenext.so

  Remember that Linux is case sensitive so it is best to keep all filenames
  lower case.

  One thing worth noting about Linux is that the symbol space for shared object
  libraries is common and this means that it is possible to inadvertantly
  create functions or global variables which conflict with names in Vensim
  proper. Unfortunately, this tends to manifest itself only by causing
  catastrophic failure when the wrong function is called or the wrong
  global variable refrenced. For example, GLOB_VARS *VENGV used to be
  just GV which is used internally in Vensim and this causes a failure.
  If you suspect this type of problem try renaming the functions or
  variables to see if it helps.



   */

#define WANT_WINDOWS_INCLUDES /* the sample implementation of this requires windows includes/libraries */
#define VENEXT_GLOBALS
#include "./vensim.h"

#ifdef unix
#include <string.h>
#include <stdlib.h>
#else
#include <malloc.h>
#endif

GLOB_VARS *VENGV = NULL; /* the value for this is set by set_gv below */



/*******************************************
 1 - function ids - used to swich between choices
 *******************************************/
#define COS_FUNC 0
#define INRANGE_FUNC 1
#define PSUM_FUNC 2
#define INVERT_FUNC 3
#define INPLACE_INVERT_FUNC 4
#define INTERNAL_ROR_FUNC 5
#define MYMESSAGE_FUNC 6
#define MYFINDZERO_FUNC 7
#define MYLOOKUP_FUNC 8
#define MYALLTYPES_FUNC 9
#define MYCONSTDEF_FUNC 10
#define MYDATADEF_FUNC 11

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
double COSINE(double x);
double INRANGE(double norm, double minval, double maxval);
double PSUM(VECTOR_ARG *vec, double num_arg, int maxarg);
double MATRIX_INVERT(VECTOR_ARG *invmat, VECTOR_ARG *mat1);
double MATRIX_INPLACE_INVERT(VECTOR_ARG *mat1);
double INTERNAL_ROR(double inval, double time, double minval, double maxval,
	int streamid, double do_compute);
double MYMESSAGE(const unsigned char *message, double time);
double MYFINDZERO(VECTOR_ARG *x, VECTOR_ARG *y, int narg);
double MYLOOKUP(TAB_TYPE *tab, double x);
double MYALLTYPES(VECTOR_ARG *lhs, const unsigned char *literal, TAB_TYPE *tab, VECTOR_ARG *vecarg, double x);
double MYCONSTDEF(CONSTANT_MATRIX *cmat, const unsigned char *literal);
double MYDATADEF(DATA_MATRIX *dmat, const unsigned char *literal);

/****************************************************
 3 - Grouping of functions in a structure - see venext.h
 ***********************************************************/

static FUNC_DESC Flist[] = {
					{"COSINE"," {x} ",1,0,COS_FUNC,0,0,0,0},
					{"INRANGE"," {x} , {minval} , {maxval} ",3,0,INRANGE_FUNC,0,0,0,0},
					{"PSUM"," {vector} , {nelm} , {nelmlimit} ",3,1,PSUM_FUNC,0,0,0,0},
					{"MATRIX_INVERT"," {matrix} ",1,1,INVERT_FUNC,2,0,0,0},
					{"MATRIX_INPLACE_INVERT"," {matrix} ",1,1,INPLACE_INVERT_FUNC,0,1,0,0},
					{"INTERNAL_ROR"," {x} , {time} , {minror} , {maxror} , {streamid} , {compute} ",6,0,INTERNAL_ROR_FUNC,0,0,0,0},
					{"MYMESSAGE"," {'message'} , {time} ",2,0,MYMESSAGE_FUNC,0,0,1,0},
					{"MYFINDZERO"," {vector_to_zero} , {nelement} ",2,1,MYFINDZERO_FUNC,1,2,0,0},
					{"MYLOOKUP"," {lookup} , {x} ",2,0,MYLOOKUP_FUNC,0,0,0,1},
					{"MYALLTYPES"," {'literal'} , {lookup} , {vector} , {x} ",4,1,MYALLTYPES_FUNC,1,0,1,1},
					{"MYCONSTDEF"," {'literal'} ",1,0,MYCONSTDEF_FUNC,CONSTDEF_MARKER,0,1,0},
					{"MYDATADEF"," {'literal'} ",1,0,MYDATADEF_FUNC,DATADEF_MARKER,0,1,0},
					{NULL,0,0,0} };

/******************************************************
 4 - DLL required functions LibMain and WEP
 Obsolete - 16 bit windows only
 ******************************************************/

 /****************************************************************
  5 External function definitions
  ****************************************************************/

  /**************************
   This function is a version check - it is required to be sure
   the external functions are compatible with the current Vensim
   version. Note that for 5.8c this number has changed but you can
   simply update this version number, the set_gv function and the
   funcversion_info function (these 2 return different value types)
   make no other changes to your external functions and they will
   work. To simplify use with different configurations (ie the
   Model Reader and DLLs) we recommend that you not link with
   vensim.lib or vensimdp.lib and replace

   vensim_error_message with (*VENGV->error_message)
   vensim_alloc_simmem with (*VENGV->alloc_simmem)
   vensim_execute_curloop with (*VENGV->execute_curloop)

 **********************/

int VEFCC version_info()
{
	return(EXTERNAL_VERSION);
}

/* When you make changes to functions update this. If Vensim opens a .vmf file
   that references aexternal functions and there is a mismatch a message will
   be given indicating that the model should be reformed and cleaned
   - if you return 0 no checking will occur

  If you have multiple external function libraries you can also use this to
  signal when a model is not matched to the library (though it won't indicate
  which library should be used) */
unsigned short VEFCC funcversion_info()
{
	return(1);
}

int VEFCC set_gv(GLOB_VARS *vgv)
{
	VENGV = vgv;

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
typedef struct _rorstr RORSTR;
struct _rorstr
{
	COMPREAL *times;
	HANDLE times_hndl;
	COMPREAL *vals;
	HANDLE vals_hndl;
	RORSTR *next;
	int streamid;
	int ntimes;
	int maxtimes;
};

/* any flags that individual function need set to perform properly on the next
   invocation must be reset by vext_clearmem */
static int Matrix_invert_maxn;
static RORSTR *Internal_ror_fror;

static HANDLE *Mem_used = NULL;
static int Num_mem_used = 0;
static int Max_mem_used = 0;


static void *vext_allocate(unsigned nbytes, HANDLE *hndl)
{
	HANDLE lhndl;
	if (Num_mem_used >= Max_mem_used)
	{
		Max_mem_used += 100;
		if (Mem_used)
		{
			Mem_used = (HANDLE *)realloc(Mem_used, Max_mem_used * sizeof(HANDLE));
			memset(Mem_used + Max_mem_used - 100, '\0', 100 * sizeof(HANDLE));
		}
		else
		{
			Mem_used = (HANDLE *)calloc(Max_mem_used, sizeof(HANDLE));
		}
	}

	if (!Mem_used)
	{
		return NULL;
	}

	lhndl = (HANDLE)malloc(nbytes);

	if (!lhndl)
	{
		return NULL;
	}

	if (hndl)
	{
		*hndl = lhndl;
	}

	Mem_used[Num_mem_used++] = lhndl;
	return(lhndl);
}


static void *vext_reallocate(unsigned nbytes, HANDLE *hndl)
{
	int i = 0;

	if (!*hndl)
	{
		return(vext_allocate(nbytes, hndl));
	}

	if (Mem_used)
	{
		/* find old - otherwise live with the memory leak */
		for (i = 0; i < Num_mem_used; i++)
		{
			if (Mem_used[i] == *hndl)
			{
				break;
			}
		}
	}

	*hndl = realloc(*hndl, nbytes);

	if (Mem_used)
	{
		if (i < Num_mem_used)
		{
			Mem_used[i] = *hndl;
		}
	}
	return(*hndl);
}


static void vext_clearmem()
{
	int i;

	if (Mem_used)
	{
		for (i = 0; i < Num_mem_used; i++)
		{
			if (Mem_used[i])
			{
				free(Mem_used[i]);
			}
		}
		free(Mem_used);
	}

	Mem_used = NULL;
	Num_mem_used = Max_mem_used = 0;

	Matrix_invert_maxn = 0;
	Internal_ror_fror = NULL;
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

CFUNCTION int VEFCC simulation_setup(int iniflag)
{
	return(1);
}

CFUNCTION int VEFCC simulation_shutdown(int finalflag)
{
	vext_clearmem();
	return(1);
}

/* this is a safety function to validate vector ranges when passing
   vectors to Vensim - you don't need to use it but it will help to
   prevent nasty memory errors */
static void validate_vector_arg(VECTOR_ARG *v, int nFirstIndex, int nLastIndex)
{
	int i;

	if (nFirstIndex > nLastIndex)
	{
		i = nFirstIndex;
		nFirstIndex = nLastIndex;
		nLastIndex = i;
	}

	if (v->vals + nFirstIndex < v->firstval
		|| v->vals + nLastIndex > v->firstval + v->dim_info->u1.tot_vol)
	{
		(*VENGV->error_message)(VERROR, (unsigned char *)"Vector argument out of bounds");
		v->vals[0] = (COMPREAL)0.0;
		v->vals[0] = (COMPREAL)(1.0 / v->vals[0]); /* generate a floating point exception */
	}
}


/*********************************************************************
 6 - vensim_external - the actual external function call
 *********************************************************************
   note that all the functions doing floating point are passed and
   return doubles to prevent any compiler specific problems from
   arising
 ******************************************************************/

CFUNCTION int VEFCC vensim_external(VV *val, int nval, int funcid)
{
	double rval;
	int n, n2;

	switch (funcid)
	{
	case COS_FUNC: /* simple function - call with double return double */
		rval = COSINE(val[0].val);
		break;

	case INRANGE_FUNC: /* simple function */
		rval = INRANGE(val[0].val, val[1].val, val[2].val);
		break;

	case PSUM_FUNC:
		n = (int)(val[1].val + .5); /* n and n2 are rounded to integers */
		n2 = (int)(val[2].val + .5);
		/* first argument is a vector - note the importance of telling Vensim
		how many arguments should be passed by address - if you attempt to
		use a floating point number as an address the function will not
		work */
		rval = PSUM(val[0].vec, n, n2);
		break;

	case INVERT_FUNC:
		/* note that this function is self looping and therefore
		Vensim has added in another argument to this function.
		and this argument is passed by address.  Vensim passes all arrays
		as vectors - the last subscripts varies the fastest - in some cases
		you may also need to pass the size of the containing array if you
		are not operating on all elements. */
		rval = MATRIX_INVERT(val[0].vec, val[1].vec);
		break;

	case INPLACE_INVERT_FUNC:
		/* the outgoing and returning matrix are the same, but the same
		underlying C function is called. */
		n = (int)(val[1].val + .5);
		rval = MATRIX_INPLACE_INVERT(val[0].vec);
		break;

	case INTERNAL_ROR_FUNC:
		n = (int)(val[4].val);
		rval = INTERNAL_ROR(val[0].val, val[1].val, val[2].val, val[3].val, n, val[5].val);
		break;

	case MYMESSAGE_FUNC:
		rval = MYMESSAGE(val[0].literal, val[1].val);
		break;

	case MYFINDZERO_FUNC:
		n = (int)(val[2].val + .5);
		rval = MYFINDZERO(val[0].vec, val[1].vec, n);
		break;

	case MYLOOKUP_FUNC:
		rval = MYLOOKUP(val[0].tab, val[1].val);
		break;

	case MYALLTYPES_FUNC:
		rval = MYALLTYPES(val[0].vec, val[1].literal, val[2].tab, val[3].vec, val[4].val);
		break;

	case MYCONSTDEF_FUNC:
		rval = MYCONSTDEF(val[0].constmat, val[1].literal);
		break;

	case MYDATADEF_FUNC:
		rval = MYDATADEF(val[0].datamat, val[1].literal);
		break;

	default:
		return(0); /* indicate an error condition to Vensim */
	}

	/* set val[0], this value will be used in the equation output */
	val[0].val = (COMPREAL)rval;
	return(1); /* a 1 return value signals vensim of successful completetion */
}


/*************************************************************************
 7 - actual function bodies - these could be a separate file
 *************************************************************************
 actual function bodies are all set up to use and return doubles
 (except when acting on vectors) this aids portability across different
 platforms and compilers as the C standard for floating point argument
 passing uses doubles.
 *************************************************************************/
double COSINE(double x)
{
	return(cos(x));
}

double INRANGE(double norm, double minval, double maxval)
{
	if (norm > maxval)
	{
		return(maxval);
	}

	if (norm < minval)
	{
		return(minval);
	}

	return(norm);
}


double PSUM(VECTOR_ARG *vec, double num_arg, int maxarg)
{
	double rval;
	int i, n;

	if (num_arg > maxarg)
	{
		num_arg = maxarg;
	}

	n = (int)(num_arg + .5);
	validate_vector_arg(vec, 0, n);

	for (i = 0, rval = 0.0; i < n; i++)
	{
		rval += vec->vals[i];
	}

	return(rval);
}


/****************************************************************
  **************************************************************
  7.2 MATRIX INVERSION

  This is done using an LU (Lower triangular, Upper triangular)
  decomposition.  Information on the algorithm is available in
	 Numerical Recipes in C as referenced in the Reference Manual

  Note that the C functions take COMPREAL * and a dimension while
  the function call passes just the matrix - the dispatch routine
  checks squareness and adds in dimension
  **************************************************************
  ***************************************************************/
#define TINY_VAL ((COMPREAL)1.0E-20) 
void lu_decomposition(COMPREAL *a, int n, int *indx, COMPREAL *d, COMPREAL *vv);
void lu_back_substitution(COMPREAL *a, int n, int *indx, COMPREAL *b);

double MATRIX_INPLACE_INVERT(VECTOR_ARG *mat)
{
	return(MATRIX_INVERT(mat, mat));
}

double MATRIX_INVERT(VECTOR_ARG *v_invmat, VECTOR_ARG *v_mat1)
{
	int i, j, k;
	COMPREAL d;
	double rval;
	COMPREAL *scratch;
	static HANDLE scr_hndl;
	static COMPREAL *tempmat;
	int *indx;
	COMPREAL *col;
	int n = 0;
	COMPREAL *invmat, *mat1;

	/* validate the last two dimensions are same on both and also the same
	if not issue an error message and cause a floating point exception to
	give more info about the error */

	i = 0;

	if (v_invmat->dim_info->tot_dim < 2 || v_mat1->dim_info->tot_dim < 2)
	{
		i = 1;
	}
	else
	{
		n = (int)v_invmat->dim_info->u2.d.dim[v_invmat->dim_info->tot_dim - 1];

		if (n != (int)v_invmat->dim_info->u2.d.dim[v_invmat->dim_info->tot_dim - 2]
			|| n != (int)v_mat1->dim_info->u2.d.dim[v_mat1->dim_info->tot_dim - 1]
			|| n != (int)v_mat1->dim_info->u2.d.dim[v_mat1->dim_info->tot_dim - 2])
		{
			i = 1;
		}
	}

	invmat = v_invmat->vals;
	mat1 = v_mat1->vals;

	if (i)
	{
		(*VENGV->error_message)(VERROR, (unsigned char *)"Matrix inversion can only be preformed on square arrays (in last two dimensions)");
		v_invmat->vals[0] = (COMPREAL)0.0;
		return(1.0 / invmat[0]);/* cause a floating point exception */
	}

	if (n > Matrix_invert_maxn)
	{
		if (!Matrix_invert_maxn)
		{
			tempmat = (COMPREAL *)vext_allocate(n*n * sizeof(COMPREAL) + n * (2 * sizeof(COMPREAL) + sizeof(int)), &scr_hndl);
		}
		else
		{
			tempmat = (COMPREAL *)vext_reallocate(n*n * sizeof(COMPREAL) + n * (2 * sizeof(COMPREAL) + sizeof(int)), &scr_hndl);
		}

		Matrix_invert_maxn = n;
	}

	scratch = tempmat + n * n;
	col = (scratch + n);
	indx = (int *)(col + n);

	/* first copy the matrix to its inverse, then work on inverse */
	for (i = 0, k = 0; i < n; i++)
	{
		for (j = 0; j < n; j++, k++)
		{
			tempmat[k] = mat1[k];
		}
	}

	lu_decomposition(tempmat, n, indx, &d, scratch);

	if (d != 0.0)
	{
		for (j = 0; j < n; j++)
		{
			for (i = 0; i < n; i++)
			{
				col[i] = (COMPREAL)0.0;
			}

			col[j] = (COMPREAL)1.0;
			lu_back_substitution(tempmat, n, indx, col);

			for (i = 0; i < n; i++)
			{
				invmat[i*n + j] = col[i];
			}
		}
	}

	if (d == 0.0)
	{ /* return a 0 matrix */
		for (i = 0, k = 0; i < n; i++)
		{
			for (j = 0; j < n; j++, k++)
			{
				invmat[k] = (COMPREAL)0.0;
			}
		}
	}

	rval = invmat[0]; /* return first element */
	return(rval);
}


void lu_decomposition(COMPREAL *a, int n, int *indx, COMPREAL *d, COMPREAL *vv)
{
	int i, j, k, imax = 0;
	COMPREAL big, dum, sum;

	*d = (COMPREAL)1.0;

	for (i = 0, k = 0; i < n; i++)
	{
		big = (COMPREAL)0.0;

		for (j = 0; j < n; j++, k++)
		{
			if (a[k] > big)
			{
				big = a[k];
			}
			else if (a[k] < 0 && -a[k] > big)
			{
				big = -a[k];
			}
		}

		if (big == 0.0)
		{
			*d = (COMPREAL)0.0;
			return;
		}

		vv[i] = (COMPREAL)(1.0 / big);
	}

	for (j = 0; j < n; j++)
	{
		for (i = 0; i < j; i++)
		{
			sum = a[i*n + j];
			for (k = 0; k < i; k++)
			{
				sum -= a[i*n + k] * a[k*n + j];
			}
			a[i*n + j] = sum;
		}

		big = (COMPREAL)0.0;

		for (i = j; i < n; i++)
		{
			sum = a[i*n + j];
			for (k = 0; k < j; k++)
			{
				sum -= a[i*n + k] * a[k*n + j];
			}

			a[i*n + j] = sum;
			dum = vv[i] * sum;

			if (dum < 0.0)
			{
				dum = -dum;
			}

			if (dum > big)
			{
				big = dum;
				imax = i;
			}
		}

		if (j != imax)
		{
			for (k = 0; k < n; k++)
			{
				dum = a[imax*n + k];
				a[imax*n + k] = a[j*n + k];
				a[j*n + k] = dum;
			}

			*d = -(*d);
			vv[imax] = vv[j];
		}

		indx[j] = imax;

		if (a[j*n + j] == 0.0)
		{
			a[j*n + j] = TINY_VAL;
		}

		if (j != n - 1)
		{
			dum = (COMPREAL)1.0 / a[j*n + j];
			for (i = j + 1; i < n; i++)
			{
				a[i*n + j] *= dum;
			}
		}
	}
} /* lu_decomposition */

void lu_back_substitution(COMPREAL *a, int n, int *indx, COMPREAL *b)
{
	int i, ii, ip, j;
	COMPREAL sum;

	ii = -1;

	for (i = 0; i < n; i++)
	{
		ip = indx[i];
		sum = b[ip];
		b[ip] = b[i];

		if (ii != -1)
		{
			for (j = ii; j < i; j++)
			{
				sum -= a[i*n + j] * b[j];
			}
		}
		else if (sum)
		{
			ii = i;
		}

		b[i] = sum;
	}

	for (i = n; i-- > 0;)
	{
		sum = b[i];

		for (j = i + 1; j < n; j++)
		{
			sum -= a[i*n + j] * b[j];
		}
		b[i] = sum / a[i*n + i];
	}

} /* lu_back_substitution */


double INTERNAL_ROR(double inval, double time, double minval, double maxval, int streamid, double compute_flag)
{
	RORSTR *ror;
	double result, npv, range;
	int granular;
	int i;

	for (ror = Internal_ror_fror; ror; ror = ror->next)
	{
		if (ror->streamid == streamid)
		{
			break;
		}
	}

	if (!ror)
	{
		ror = (RORSTR *)vext_allocate(sizeof(RORSTR), NULL);
		ror->streamid = streamid;
		ror->maxtimes = 101;
		ror->times = (COMPREAL *)vext_allocate(ror->maxtimes * sizeof(COMPREAL), &ror->times_hndl);
		ror->vals = (COMPREAL *)vext_allocate(ror->maxtimes * sizeof(COMPREAL), &ror->vals_hndl);
		ror->next = Internal_ror_fror;
		ror->ntimes = 0;
		Internal_ror_fror = ror;
	}

	if (compute_flag < 0.0)
	{
		ror->ntimes = 0;
	}

	if (compute_flag == 0.0)
	{
		return(0.0);
	}

	while (ror->ntimes > 0 && ror->times[ror->ntimes - 1] > time)
	{
		ror->ntimes--; /* back up if necessary */
	}

	if (ror->ntimes >= ror->maxtimes)
	{ /* reallocate */
		ror->maxtimes += 100;
		ror->times = (COMPREAL *)vext_reallocate(ror->maxtimes * sizeof(COMPREAL), &ror->times_hndl);
		ror->vals = (COMPREAL *)vext_reallocate(ror->maxtimes * sizeof(COMPREAL), &ror->vals_hndl);
	}

	ror->times[ror->ntimes] = (COMPREAL)time;
	ror->vals[ror->ntimes] = (COMPREAL)inval;
	ror->ntimes++;

	if (compute_flag > 1.0)
	{
		for (range = (maxval - minval) / 4.0, result = (minval + maxval) / 2.0, granular = 1; granular < 20; granular++, range /= 2.0)
		{
			npv = 0;
			for (i = 0; i < ror->ntimes; i++)
			{
				npv += ror->vals[i] * exp(result * (ror->times[0] - ror->times[i]));
			}

			if (npv < 0.0)
			{
				result -= range;
			}
			else if (npv > 0.0)
			{
				result += range;
			}
			else
			{
				break;
			}
		}
		return(result);
	}

	return(0.0);
}


/*************************/
double MYMESSAGE(const unsigned char *message, double time)
{
	char timestr[40];
	sprintf(timestr, "At time %g", time);

#ifdef unix
	printf("%s\n", timestr);
#else
	/* note that external functions will never execute in Vensim UI thread
	so a call like this will always create a new main window - it is
	better to use the Vensim messaging available as the second
	call here - Vensim will display that in its UI thread and pause
	this thread till the user takes action */
	MessageBox(GetActiveWindow(), (LPCSTR)message, timestr, MB_ICONSTOP | MB_OK);
#endif

	//return(1.0) ;                             
	/* note that we could also use the following call */
	(*VENGV->error_message)(INFORM, (unsigned char *)timestr);

	return(1.0);

}

/**********************************
 Note the following will often fail it is included
 here as an example only */
double MYFINDZERO(VECTOR_ARG *vx, VECTOR_ARG *vy, int narg)
{
	int i, j;
	int rval;
	double maxerr = 0;
	COMPREAL *x, *y;
	char buf[128];

	validate_vector_arg(vx, 0, narg);
	validate_vector_arg(vy, 0, narg);
	x = vx->vals;
	y = vy->vals;

	if (x[0] == NA)
	{ /* initialize */
		for (i = 0; i < narg; i++)
		{
			x[i] = (COMPREAL)1.0;
		}
	}

	for (j = 0; j < 50; j++)
	{
		rval = (*VENGV->execute_curloop)();

		if (!rval) /* execution failuer - give up - should not happen */
		{
			break;
		}

		if (rval == -1)
		{ /* floating point error */
			(*VENGV->error_message)(VERROR, (unsigned char *)"Floating point error in solving MYFINDZERO");

			/* now generate a floating point error so that Vensim can report back on the problem
			vensim still knows where it trapped the problem - can't use raise(SIGFPE) because
			this causes everyting to close (via an untrapped exit call) */

			maxerr = (1.0 + y[0]) / (x[0] - x[0]); /* compiling this will likely generate a warning message */
												/* now we use maxerr otherwise the the above line will never be executed
												when the code is optimized */

			if (maxerr < 0)
			{
				return -1;
			}

			return NA; /* give up for this example */
		}
		else
		{
			for (i = 0, maxerr = 0.0; i < narg; i++)
			{
				if (fabs(y[i]) > maxerr)
				{
					maxerr = fabs(y[i]);
				}

				x[i] += y[i] / 10;
			}

			if (maxerr < 1.0E-4)
			{
				break;
			}
		}
	}

	if (maxerr > 1.0E-4)
	{
		sprintf(buf, "MYFINDZERO convergance failure at time %g", VENGV->time);
		(*VENGV->error_message)(VERROR, (unsigned char *)buf);
	}

	return(x[0]);
}

double MYLOOKUP(TAB_TYPE *pTable, double x)
{
	REAL *xvals, *yvals;
	int i;
	int lstind;

	if (!VENGV)
	{
		return(NA);
	}

	lstind = (int)labs(pTable->nNumValsAndTableType);

	xvals = (REAL *)(VENGV->tabbase + pTable->x);
	yvals = (REAL *)(VENGV->tabbase + pTable->y);

	if (x <= xvals[0])
	{
		return(yvals[0]);
	}


	for (i = 0; i < lstind - 1; i++)
	{
		if (x <= xvals[i + 1])
		{
			break;
		}
	}

	if (i == lstind - 1)
	{
		return(yvals[lstind - 1]);
	}

	return(yvals[i] + (yvals[i + 1] - yvals[i])*(x - xvals[i]) / (xvals[i + 1] - xvals[i]));
}

/* this is just to illustrate how different arguments are passed and in what order
   this is a self looping function taking one each of the different argument types
   note that the first argument is the left hand side variable passed as a vector */
double MYALLTYPES(VECTOR_ARG *lhs, const unsigned char *literal, TAB_TYPE *tab, VECTOR_ARG *vecarg, double x)
{
	int i, n = 0;
	i = 0;

	if (lhs->dim_info->tot_dim == 0 || vecarg->dim_info->tot_dim == 0)
	{
		i = 1;
	}
	else
	{
		n = (int)lhs->dim_info->u2.d.dim[lhs->dim_info->tot_dim - 1];

		if (n != (int)vecarg->dim_info->u2.d.dim[vecarg->dim_info->tot_dim - 1])
		{
			i = 1;
		}
	}

	if (i)
	{
		(*VENGV->error_message)(VERROR, (unsigned char *)"The third argument must have same dimension as left hand side");
		lhs->vals[0] = (COMPREAL)0.0;
		return(1.0 / lhs->vals[0]);/* cause a floating point exception */
	}

	for (i = 0; i < n; i++)
	{
		lhs->vals[i] = (COMPREAL)(vecarg->vals[i] * x);
	}
	return(lhs->vals[0]);
}


double MYCONSTDEF(CONSTANT_MATRIX *cmat, const unsigned char *literal)
{
	int i, j;

	if (cmat->keyval != CONSTANT_MATRIX_KEY)
	{
		(*VENGV->error_message)(STOP, (unsigned char *)"Bad call to MYCONSTDEF");
		return 0;
	}

	/* just fill in the matrix with some simple numbers */
	(*VENGV->alloc_simmem)(NULL, cmat, 0);

	for (i = 0; i < cmat->nrow; i++)
	{
		for (j = 0; j < cmat->ncol; j++)
		{
			cmat->vals[i][j] = (COMPREAL)(i * 100.0 + j);
		}
	}

	return(cmat->vals[0][0]);
}


double MYDATADEF(DATA_MATRIX *dmat, const unsigned char *literal)
{
	int i, j;
	COMPREAL time, time_step, initial_time;

	/* get the data over the simulation range - this may not work if
	any of TIME_STEP, INITIAL TIME or FINAL TIME are not constants */

	if (dmat->keyval != DATA_MATRIX_KEY)
	{
		(*VENGV->error_message)(STOP, (unsigned char *)"Bad call to MYDATADEF");
		return 0;
	}

	if (VENGV->time_step > 0)
	{
		time_step = VENGV->time_step;
	}
	else
	{
		time_step = 1;
	}

	if (VENGV->initial_time != NA)
	{
		initial_time = VENGV->initial_time;
	}
	else
	{
		initial_time = 0.0;
	}

	if (VENGV->final_time > initial_time)
	{
		dmat->ntime = (long)((VENGV->final_time - initial_time) / time_step + 1.5);
	}
	else
	{
		dmat->ntime = 100;
	}

	(*VENGV->alloc_simmem)(dmat, NULL, 0);

	for (time = initial_time, j = 0; j < dmat->ntime; j++, time += time_step)
	{
		dmat->timevals[j] = time;
	}

	for (i = 0; i < dmat->nvar; i++)
	{
		for (j = 0; j < dmat->ntime; j++)
		{
			dmat->vals[i][j] = (COMPREAL)(i * 100.0 + j);
		}
	}

	return(dmat->vals[0][0]);
}

