/*************************************************************
  Vensim.h Copyright 1992-2004 Ventana Systems, Inc.

  This header file is for use in compiled simulations and external
  functions.  Do not change anything in this file.  If you want to add
  to this file do so below the terminating comment 
 *********************************************/

#ifndef _VENSIM_H_
#define _VENSIM_H_

/*******************************
 Part 0 - version information - this needs to be matched
          with Vensim exactly - do not change this if
          it does not match - get the updated file from
          the installer for the Vensim DSS version you are
          using 
*****************************/
#if !defined(_VDFX)
#define _VDFX
#endif

#if !defined(VDFX)
#define VDFX
#endif

#if !defined(DBLPREC)
#define DBLPREC
#endif

#if !defined(DPMATH)
#define DPMATH
#endif

#if defined(_VDFX) || defined(VDFX)
#if defined(DBLPREC) || defined(DPMATH)
#define EXTERNAL_VERSION 62051
#define COMPILED_VERSION 62051
#else
#define EXTERNAL_VERSION 62050 /* for external function */
#define COMPILED_VERSION 62050 /* for compiled models */  
#endif
#else
#if defined(DBLPREC) || defined(DPMATH)
#define EXTERNAL_VERSION 52051
#define COMPILED_VERSION 52051
#else
#define EXTERNAL_VERSION 52050 /* for external function */
#define COMPILED_VERSION 52050 /* for compiled models */  
#endif
#endif

#define VGV_MAGIC_START 0x3F278CB1
#define VGV_MAGIC_END   0x872E1DF3

#ifndef VERSION_ONLY

/***********************************************************
  Part 1 

  Common definitions and structures

  ***********************************************************/
#ifdef unix
#define VEFCC
#define FAR
#define LPSTR char *
#define WORD unsigned int
#define _export
#define HANDLE void *
#define HWND HANDLE
#define HDC HANDLE
#define UINT unsigned int
#define WPARAM UINT
#define LPARAM UINT
#define __cdecl
#define __stdcall
#define CALLBACK
#define LOGFONT int
#define TEXTMETRIC int
#define HINSTANCE HANDLE
#define DWORD UINT
#define LRESULT long
#define VOID void
#else
#define VEFCC __stdcall

/* if WANT_WINDOWS_INCLUDES is set we include windows.h - otherwise
   just define a few basic things - the default venext.c needs windows.h
   but compiling does not require this */
#ifdef WANT_WINDOWS_INCLUDES
#include <windows.h>
#elif !defined( _WINDOWS_)
/* the following are windows definitions and don't need to be included
   if windows.h is included */
#define FAR
#define LPSTR char *
#define _stdcall
#define WORD unsigned int
#define HANDLE void *
#define HWND HANDLE
#define HDC HANDLE
#define UINT unsigned int
#define WPARAM UINT
#define LPARAM UINT
#define CALLBACK
#define LOGFONT int
#define TEXTMETRIC int
#define HINSTANCE HANDLE
#define DWORD UINT
#define LRESULT long
#define VOID void
#endif
#ifndef PASCAL
#define PASCAL VEFCC /* to make it easier for older source venext.c files */
#endif

#endif
#include <stdio.h>
#include <math.h>
#define VLARGE
#ifdef __cplusplus
#define CFUNCTION extern "C"
#else
#define CFUNCTION extern
#endif

#define MARKET_MATCH_X01 MARKET_MATCH /* temporary */
#define NA (COMPREAL)(-1.2980742146337069E33) /* - 2 to the 109 makes == ok  */


/* error types */
#define NOT_ERROR 0
#define CONT_ERROR 1
#define NOT_USED 2
#define WARNING 3
#define NOT_DEFINED 4
#define VERROR 5
#define INFORM 6
#define YIELD 7
#define STOP 8
#define FATAL 9
#define PROGRAM 10

/* maximum number of dimensions supported by vensim */
#define MAX_DIM 8

typedef unsigned char charutf8 ;

typedef unsigned short V2BYTEU ;
typedef signed short V2BYTES ;
typedef unsigned long V4BYTEU ;
typedef signed long V4BYTES ; 
typedef long long V8BYTES;
typedef unsigned long long V8BYTEU; 

typedef float REAL ;
typedef double BigREAL ;
#ifdef DBLPREC 
typedef double COMPREAL ;
#else
typedef float COMPREAL ;
#endif

#if defined(_VDFX) || defined(VDFX)
typedef double				VDF_STORAGE_TYPE ;
typedef unsigned long long	VAL_OFF ;
typedef	REAL				LOOKUP_TABLE_VAL_TYPE;												
#else
typedef REAL				VDF_STORAGE_TYPE;
typedef V4BYTEU				VAL_OFF ;
typedef	REAL				LOOKUP_TABLE_VAL_TYPE;
#endif

typedef V4BYTES SUBVAL_OFF ;
typedef V4BYTEU *BLOCKBASE ; /* block base */
typedef V4BYTEU BWORD ; /* word type for a block */
typedef V4BYTEU VCOLOR ; /* used for color passing and storing */
typedef V2BYTEU OB_INDEX ;
typedef V4BYTEU BLK_OFFSET ; 
typedef V4BYTEU ST_INDEX ;  
typedef V4BYTES SST_IND ; /* sorted symbol table index (ST_INDEX should be called ST_OFFSET) */
typedef V4BYTES VFILE_OFF ;  
typedef V4BYTES EDLINE_IND ; 
typedef V2BYTES VDF_VALCOUNT ;

#if defined(_VDFX) || defined(VDFX)
typedef struct tag_table_range_vdfx
{
#ifdef USE_OFFSET_HANDLES
	VAL_OFF history ;
#else
#ifndef _x64
	V4BYTES x86_Padding_01;
#endif
	charutf8 *history ;
#endif
	VAL_OFF first ;
	VAL_OFF tot_vol ;
	BLK_OFFSET next ;
} TABLE_RANGE_VDFX ;
#endif


typedef struct tag_table_range_vdf
{
#ifdef USE_OFFSET_HANDLES
	V4BYTEU history ;
#else
#if defined(_VDFX) || defined(VDFX)
	V4BYTES history ;
#else
	charutf8 *history ;
#endif
#endif
#if defined(_VDFX) || defined(VDFX)
	V4BYTEU first ;
	V4BYTEU tot_vol ;
#else
	VAL_OFF first ;
	VAL_OFF tot_vol ;
#endif
	BLK_OFFSET next ;
} TABLE_RANGE_VDF ;

#if defined(_VDFX) || defined(VDFX)
	#define TABLE_RANGE TABLE_RANGE_VDFX
#else
	#define TABLE_RANGE TABLE_RANGE_VDF
#endif

typedef V4BYTEU ST_INDEX_VDF;
typedef	REAL	LOOKUP_TABLE_VAL_TYPE;

typedef struct tag_tab_type_vdfx
{
	LOOKUP_TABLE_VAL_TYPE base ; /* the base val */
	LOOKUP_TABLE_VAL_TYPE xgap ; /* the time gap to the next x value */
	LOOKUP_TABLE_VAL_TYPE ygap ; /* the value gap the the next y value */
	LOOKUP_TABLE_VAL_TYPE lstx ; /* the x value of the  base */
	LOOKUP_TABLE_VAL_TYPE nextx ; /* the x value of the next entry after base */
	BLK_OFFSET x ; /* pointer to the x values */
	BLK_OFFSET y ; /* pointer to the y values */
	V4BYTES curind ; /* the current index value (matches base) */
	V4BYTES nNumValsAndTableType; /* the number of value for the tabe */
	TABLE_RANGE range[1] ; /* used for reporting over under and in messages */
} TAB_TYPE_VDFX ;

typedef struct tag_tab_type_vdf
{
   REAL base ; /* the base val */
   REAL xgap ; /* the time gap to the next x value */
   REAL ygap ; /* the value gap the the next y value */
   REAL lstx ; /* the x value of the  base */
   REAL nextx ; /* the x value of the next entry after base */
   BLK_OFFSET x ; /* pointer to the x values */
   BLK_OFFSET y ; /* pointer to the y values */
   V4BYTES curind ; /* the current index value (matches base) */
   V4BYTES nNumValsAndTableType; // this used to be lstind, but since 7.3.7 it can be negative which indicates that the table is a S_LOOKUPDEF_FUNC rather than S_LOOKUP  /* the number of value for the tabe */
   TABLE_RANGE_VDF range[1] ; /* used for reporting over under and in messages */
} TAB_TYPE_VDF ;
/* globally available structures */

#if defined(_VDFX) || defined(VDFX)
	#define TAB_TYPE TAB_TYPE_VDFX
#else
	#define TAB_TYPE TAB_TYPE_VDF
#endif

//#ifdef _VDFX
typedef struct tag_dim_info_vdfx
{
	BLK_OFFSET next ;

	union
	{
		V4BYTEU tot_vol ; /* the total size  */
		BLK_OFFSET parent ; /* the parent dimensions for exceptions */
	} u1 ;
	
	union
	{
		struct
		{
			//V4BYTEU PADDING;
			VAL_OFF dim[MAX_DIM] ;     /* total size of a dimension */
			VAL_OFF dim_vol[MAX_DIM] ; /* the total volume for one subscript */
		} d ;
		struct
		{
			char *except_flag_ptr ; /* for large one - scr_alloced so not permanent */
			VAL_OFF except_off[2*MAX_DIM-1] ; /* for small number of exceptions */
		} e ;
	} u2 ;
	ST_INDEX fam[MAX_DIM] ;   /* families for elements - actual entries for excemptions : TONY. I think this is a symbol table entry */
	V2BYTES tot_dim ; /* number of elements */
	V2BYTES except_type ; /* the number of exceptions, but capped at 30000 */
} DIM_INFO_VDFX ;
//#endif

typedef struct tag_dim_info_vdf
{
	BLK_OFFSET next ;

	union
	{
		V4BYTEU tot_vol ; /* the total size  */
		BLK_OFFSET parent ; /* the parent dimensions for exceptions */
	} u1 ;
	
	union
	{
		struct
		{
#if defined(_VDFX) || defined(VDFX)
			V4BYTEU dim[MAX_DIM] ;     /* total size of a dimension */
			V4BYTEU dim_vol[MAX_DIM] ; /* the total volume for one subscript */
#else
			VAL_OFF dim[MAX_DIM] ;     /* total size of a dimension */
			VAL_OFF dim_vol[MAX_DIM] ; /* the total volume for one subscript */
#endif
			// dim_vol seems to be combinatorial, starting at the end, so
			// if the dimensions have size 4,3,2,
			// dim_vol will be 6,2,1
		} d ;
		struct
		{
#if defined(_VDFX) || defined(VDFX)
			V4BYTEU except_flag_ptr ; /* for large one - scr_alloced so not permanent */
			V4BYTEU except_off[2*MAX_DIM-1] ; /* for small number of exceptions */
#else
			char *except_flag_ptr ; /* for large one - scr_alloced so not permanent */
			VAL_OFF except_off[2*MAX_DIM-1] ; /* for small number of exceptions */
#endif
		} e ;
	} u2 ;
	ST_INDEX_VDF fam[MAX_DIM] ;   /* families for elements - actual entries for excemptions */
	V2BYTES tot_dim ; /* number of elements */
	V2BYTES except_type ; /* the number of exceptions, but capped at 30000 */
} DIM_INFO_VDF ;

#if defined(_VDFX) || defined(VDFX)
#define DIM_INFO DIM_INFO_VDFX
#else
#define DIM_INFO DIM_INFO_VDF
#endif


typedef struct
{
	COMPREAL VLARGE *vals ;
	const COMPREAL VLARGE *firstval ;
	const DIM_INFO *dim_info ;
	const charutf8 *varname ;
} VECTOR_ARG ;


typedef struct
{
	#if !defined(_x64) && defined(VDFX)
	V4BYTES x86_Padding_vals;
	#endif
	COMPREAL VLARGE *vals ;

	#if !defined(_x64) && defined(VDFX)
	V4BYTES x86_Padding_firstval;
	#endif
	const COMPREAL VLARGE *firstval ;
	
	#if !defined(_x64) && defined(VDFX)
	V4BYTES x86_Padding_dim_info;
	#endif
	const DIM_INFO *dim_info ;

	#if !defined(_x64) && defined(VDFX)
	V4BYTES x86_Padding_varname;
	#endif
	const charutf8 *varname ;

} VECTOR_ARG_tmp ;

typedef struct {
   unsigned long keyval ;
   char *varname ;
   COMPREAL *timevals ;
   COMPREAL **vals ;
   long nvar ;
   long ntime ;
   } DATA_MATRIX ;
typedef struct {
   unsigned long keyval ;
   char *varname ;
   COMPREAL **vals ;
   long ncol ;
   long nrow ;
   } CONSTANT_MATRIX ;
#define DATA_MATRIX_KEY   0x33F27413
#define CONSTANT_MATRIX_KEY 0xF722438E
typedef union { /* arguments are loaded on a vector and passed either */
  COMPREAL val ;  /* by value as floats or */
  VECTOR_ARG *vec ; /* by address - normally the first element in an array */
  TAB_TYPE *tab ;
  const unsigned char *literal ;
  CONSTANT_MATRIX *constmat ;
  DATA_MATRIX *datamat ;
  } VV ;
  
typedef struct tag_st_head_struct {
          VAL_OFF num_lev ; /* the number of level variable in the model */
          VAL_OFF num_delay ; /* pure delays - included in num_lev */
          } ST_HEAD  ;


#pragma pack(push,8)

typedef struct tag_glob_vars  { /* global variables - like a common block */
  unsigned vgv_magic_start ;
  VAL_OFF lastpos ; /* the last position computed */
  COMPREAL VLARGE *LEVEL ; /* vector of all model values */
  COMPREAL VLARGE *RATE ;
  TAB_TYPE *TAB ; /* the table list - used only at runtime */
  //char *pTabTypes; ///TAB Types in the TAB above, used to distinquish between S_LOOKUP and S_LOOKUPDEF_FUNC
  /* the following are used in compiled simulation and available to external functions  */
  BLOCKBASE tabbase ; /* for table values (x-y) */
  BLOCKBASE strbase ; /* for string variables BLK_FIRST_OFF has vector with offsets */
  ST_HEAD *simulation_sinfo ;/* the symbol table header - not used internally */
  COMPREAL time ; /* the time for the current simulation  */
  COMPREAL time_step ; /* the time step */
  COMPREAL time_plus ; /* time plus half of time step for testing */
  COMPREAL time_minus ;/* time minus half of the time step for testing */
  COMPREAL final_time ; /* the last time in the simulation */
  COMPREAL initial_time ; /* the initial time of the simulation */
  COMPREAL save_time ; /* the next time at which saving should happen */
  COMPREAL saveper ; /* the interval to the next save time */
#ifndef VENPLP
  VECTOR_ARG *vector_arglist ; /* vector argument information */
#endif
  char simulation_state ; /* see sim.h  */
  char gaming_state ; /* see sim.h */
  char integ_type ;
  char simulation_type ;  /* see sim.h */

  /* overrides for SyntheSim */
  int fs_override_active ; /* 0  no |1 for element by element |2 for visible structure */
  COMPREAL *fs_override_vals ; /* the value to override with - computed or held  */
  charutf8 *fs_overridden ; /* flag to indicate a variable is overridden - value in fs_override_val */
  /* addition stuff on fs below */

  /* functions called back to by compiled simulations and external functions
     these are not exported so that we don't need to link differently for
     different engines */
int (VEFCC *add_vecarg_info)(ST_INDEX *stlist,int n) ;
BigREAL (VEFCC *ALLOC_P) (BigREAL request,BigREAL priority,BigREAL width,BigREAL mp) ;
BigREAL (VEFCC *ALLOCATE_AVAILABLE) (VECTOR_ARG *allocation,VECTOR_ARG *request,VECTOR_ARG *request_p,BigREAL available) ;
BigREAL (VEFCC *ALLOCATE_BY_PRIORITY) (VECTOR_ARG *allocation,VECTOR_ARG *request,VECTOR_ARG *priority,int size,BigREAL width,BigREAL supply) ;
int (VEFCC *COMPARE_SIMULT_VALUES)(int storeflag) ;
BigREAL (VEFCC *FIND_MARKET_PRICE) (VECTOR_ARG *d,VECTOR_ARG *d_p,VECTOR_ARG *s,VECTOR_ARG *sp) ;
void (VEFCC *EXTERNAL_FUNCTION)(VV *val,int nval,int funcid) ;
BigREAL (VEFCC *FIND_ZERO) (VECTOR_ARG *vx,VECTOR_ARG *vsx,VECTOR_ARG *vz,VECTOR_ARG *vsz,VECTOR_ARG *inix,BigREAL fn,BigREAL fns,BigREAL tolerance,BigREAL fmax_iter,BigREAL method) ;
BigREAL (VEFCC *GET_DATA_AT_TIME) (VECTOR_ARG *v,BigREAL t) ;
BigREAL (VEFCC *GET_DATA_ATTRIBUTE) (int attrib,VECTOR_ARG *v,BigREAL t,BigREAL mode) ;
BigREAL (VEFCC *GET_DATA_BETWEEN_TIMES) (VECTOR_ARG *v,BigREAL t,BigREAL mode) ;
BigREAL (VEFCC *GET_DATA_FIRST_TIME) (VECTOR_ARG *v) ;
BigREAL (VEFCC *GET_DATA_LAST_TIME) (VECTOR_ARG *v) ;
BigREAL (VEFCC *GET_DATA_TOTAL_POINTS) (VECTOR_ARG *v) ;
BigREAL (VEFCC *GET_TIME_VALUE)(BigREAL relativeto,BigREAL offset,BigREAL measure) ;
BigREAL (VEFCC *INIT_PURE_DELAY) (int type,VAL_OFF deloff,VAL_OFF valoff,double deltime,double initval,double missval_or_order,TAB_TYPE *tab,TAB_TYPE *tab2) ;
BigREAL (VEFCC *INIT_SINTEG) (int type,VAL_OFF deloff,VAL_OFF valoff,double initval,double minval,double maxval,double quantval,double specval,double tolerance) ;
BigREAL (VEFCC *INVERT_MATRIX) (VECTOR_ARG *ainv,VECTOR_ARG *a,BigREAL n) ;
BigREAL (VEFCC *LOOKUP_AREA) (TAB_TYPE *tab,BigREAL start,BigREAL end) ;
BigREAL (VEFCC *LOOKUP_BACKWARD) (TAB_TYPE *tab,BigREAL in) ;
BigREAL (VEFCC *LOOKUP_EXTRAPOLATE) (TAB_TYPE *tab,BigREAL in) ;
BigREAL (VEFCC *LOOKUP_FORWARD) (TAB_TYPE *tab,BigREAL in) ;
BigREAL (VEFCC *LOOKUP_INVERT) (TAB_TYPE *tab,BigREAL in) ;
BigREAL (VEFCC *LOOKUP_SLOPE) (TAB_TYPE *tab,BigREAL x,BigREAL mode) ;

#ifdef  LPALLOCFN
#ifndef _MACX
BigREAL (VEFCC *LP_ALLOC) (VECTOR_ARG *allocation, VECTOR_ARG *ds_priority, VECTOR_ARG *ds_capacity, VECTOR_ARG *d_capacity, VECTOR_ARG *s_capacity) ;
#endif
#endif

BigREAL (VEFCC *MARKET_DS) (VECTOR_ARG *ds,VECTOR_ARG *ds_p,BigREAL price,int isdemand) ;
BigREAL (VEFCC *MARKET_MATCH) (VECTOR_ARG *sales,VECTOR_ARG *demandq,VECTOR_ARG *dshape,VECTOR_ARG *seller_attract,VECTOR_ARG *supplyq,VECTOR_ARG *sshape,VECTOR_ARG *buyer_priority,VECTOR_ARG *dqsconversion) ;
BigREAL (VEFCC *MARKETP) (VECTOR_ARG *request,VECTOR_ARG *priority,int size,BigREAL width,BigREAL supply) ;
BigREAL (VEFCC *MESSAGE) (unsigned char *msg,BigREAL severity) ;
BigREAL (VEFCC *QUEUE_GETINFO)(VECTOR_ARG *v,BigREAL youngest,BigREAL oldest,int action) ;
BigREAL (VEFCC *RANDOM_0_1 ) (void) ;
BigREAL (VEFCC *RANDOM_BETA) (BigREAL xmin,BigREAL xmax,BigREAL alpha,BigREAL beta,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_BINOMIAL) (BigREAL xmin,BigREAL xmax,BigREAL p,BigREAL n,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_EXPONENTIAL) (BigREAL xmin,BigREAL xmax,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_GAMMA) (BigREAL xmin,BigREAL xmax,BigREAL a,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_LOOKUP) (TAB_TYPE *look,BigREAL xmin,BigREAL xmax,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_NEGATIVE_BINOMIAL) (BigREAL xmin,BigREAL xmax,BigREAL p,BigREAL n,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_NORMAL) (BigREAL xmin,BigREAL xmax,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_POISSON) (BigREAL xmin,BigREAL xmax,BigREAL a,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_TRIANGULAR) (BigREAL xmin,BigREAL xmax,BigREAL peak,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_UNIFORM) (BigREAL xmin,BigREAL xmax,BigREAL streamid) ;
BigREAL (VEFCC *RANDOM_WEIBULL) (BigREAL xmin,BigREAL xmax,BigREAL shape,BigREAL shift,BigREAL stretch,BigREAL streamid) ;
BigREAL (VEFCC *SHIFT_IF_TRUE) (VECTOR_ARG *array,BigREAL cond,BigREAL arrsize,BigREAL cumulate,BigREAL startval) ;
BigREAL (VEFCC *STORE_PURE_DELAY) (VAL_OFF deloff,double val,double outval,double delaytime,double changerate,TAB_TYPE *tab) ;
BigREAL (VEFCC *TABLE) (TAB_TYPE *tab,BigREAL in) ;
BigREAL (VEFCC *TIME_BASE) (BigREAL intecept,BigREAL slope) ;
BigREAL (VEFCC *VECTOR_ELM_MAP) (VECTOR_ARG *in,BigREAL shift) ;
BigREAL (VEFCC *VECTOR_LOOKUP) (VECTOR_ARG *in,BigREAL x,BigREAL xmin,BigREAL xmax,BigREAL mode) ;
BigREAL (VEFCC *VECTOR_RANK) (VECTOR_ARG *outvector,VECTOR_ARG *invector,BigREAL d) ;
BigREAL (VEFCC *VECTOR_REORDER) (VECTOR_ARG *outvector,VECTOR_ARG *invector,VECTOR_ARG *sortvector) ;
BigREAL (VEFCC *VECTOR_SORT_ORDER) (VECTOR_ARG *outvector,VECTOR_ARG *invector,BigREAL d) ;
void (VEFCC *vselect_error)(int action,int errtype,int elmcount) ;

/* functions available to external functions (error_message also used in compiled simulations */
void (VEFCC *error_message)(int severity,unsigned char *str) ;
int (VEFCC *execute_curloop)(void) ;
void *(VEFCC *alloc_simmem)(DATA_MATRIX *dm,CONSTANT_MATRIX *cm,V4BYTEU bytes) ;
int (VEFCC *varname_from_offset)(unsigned offset,unsigned char *buf,int maxbuflen) ;
int (VEFCC *get_val)(const char *name,float *val) ;
int (VEFCC *get_dpval)(const char *name,double *val) ;
int (VEFCC *get_vecvals)(const V4BYTEU *vecoff,float *vals,int nvals) ;
int (VEFCC *get_dpvecvals)(const V4BYTEU *offsets,double *dpvals,int veclen) ;
unsigned (VEFCC *get_varoff)(const char *varname) ;
int (VEFCC *check_status)(void) ;
int (VEFCC *get_varnames)(const char *infilter,int vartype,char *buf,int maxbuflen) ;
int (VEFCC *get_varattrib)(const char *varname,int attrib,char *buf,int maxbuflen) ;
int (VEFCC *get_info)(int infowanted,char *buf,int maxbuflen) ;
int (VEFCC *vdde_initiate)(charutf8 *servname,charutf8 *topic) ;
int (VEFCC *vdde_request)(int dde_channel,charutf8 *item,charutf8 **buf,unsigned max_wait) ;
int (VEFCC *vdde_vrequest)(int dde_channel,charutf8 **item,charutf8 **buf,int nitem,unsigned max_wait) ;
int (VEFCC *vdde_poke)(int dde_channel,charutf8 *item,charutf8 *value) ;
int (VEFCC *vdde_terminate)(int dde_channel) ;
int (VEFCC *vdde_execute)(int dde_channel,charutf8 *ddecommand) ;
int (VEFCC *vdde_wait_execute)(int dde_channel,charutf8 *ddecommand,unsigned maxwait) ;
void (VEFCC *vensim_transmit_dde)(void) ;

BigREAL (VEFCC *DateSerial_Excel)(int nYear, int nMonth, int nDay, int nHour, int nMin, int nSec);
BigREAL (VEFCC *ExcelDateSerial_YEAR)(BigREAL fExcelSerialDate);
BigREAL (VEFCC *ExcelDateSerial_MONTH_OF_YEAR)(BigREAL fExcelSerialDate);
BigREAL (VEFCC *ExcelDateSerial_WEEK_OF_YEAR)(BigREAL fExcelSerialDate);
BigREAL (VEFCC *ExcelDateSerial_HOUR)(BigREAL fExcelSerialDate);
BigREAL (VEFCC *ExcelDateSerial_MINUTE)(BigREAL fExcelSerialDate);
BigREAL (VEFCC *ExcelDateSerial_SECOND)(BigREAL fExcelSerialDate);
BigREAL (VEFCC *ExcelDateSerial_DAY_OF_YEAR)(BigREAL fExcelSerialDate);
BigREAL (VEFCC *ExcelDateSerial_DAY_OF_WEEK)(BigREAL fExcelSerialDate);
BigREAL (VEFCC *ExcelDateSerial_DAY_OF_MONTH)(BigREAL fExcelSerialDate);

unsigned vgv_magic_end ;
} GLOB_VARS ; /* globaly available variables */

#pragma pack(pop)


#define SS_IDLE 0   /* GV.simulation_state */
#define SS_ONSCREEN 1 /* getting changes from sketch screen */
#define SS_LOCKED 2 /* GV.LEVEL is locked - no user interaction */
#define SS_INIT  3
#define SS_ACTIVE 4 /* simulation is running */ 
#define SS_INTEG 5 /* integration is in process - suppress messages */
#define GS_NONE 0 /* GV.gaming_state not in a gaming state */
#define GS_PREP 1 /* gaming - need to format results and store data */
#define GS_CONTINUE 2  /* continuing an existing game - just add to results file */   
#define GS_FINISHED 3 /* model has run to completion - nothing to do */  
#define GS_STARTING 4 /* model is just starting or has been backed up to start point */
#define ST_NORMAL 0 /* just simulate */
#define ST_PARTIAL 1 /* simulate holding some things constant */
#define ST_GAME 2 /* gaming mode */
#define ST_REALITY_CHECK 3 /* reality check */   
#define IT_EULER 0
#define IT_DIFFERENCE 2
#define IT_RK2F 3
#define IT_RK2 4
#define IT_RK4F 5
#define IT_RK4 1   

#define F_QUEUE_AGE_OLDEST 137   /* these are also used in vensim.h for compiled sims */
#define F_QUEUE_AGE_IN_RANGE 138
#define F_QUEUE_AGE_AVERAGE 139
#define F_QUEUE_ATTRIB_MIN 140
#define F_QUEUE_ATTRIB_MAX 141
#define F_QUEUE_ATTRIB_AVERAGE 142
#define F_QUEUE_ATTRIB_IN_RANGE 143 
#define F_QUEUE_ATTRIB_QUANTITY 144 /* end of things used in vensim.h */






/**************************************************************************
 Part 3 (part 2 have been moved to simext.c not needed for external function)

  fuction prototypes and structure definitions specific to external functions

  ***************************************************************************/

/* this is used as a convenient way to store function info */
typedef struct _fnct_desc {
   char *sym ; /* function names - as it will be used in Vensim */
   char *argument_desc ; /* description of arguments use in equation editor */
   unsigned char num_args ; /* 0 - 255 */
   unsigned char num_vector ; /* for manipulating vectors or changing the
                                 value of model variables */
   unsigned short func_index ; /* the index for the user function 0-32000 */
   char num_loop  ; /* the number of user managed loops - for defining
               more than one element of an array or matrix  - use -1 to signal
               a constant definition function and -2 a data definition function */
   unsigned char modify ; /* flag to indicate that function may change its
                             its inputs - only makes sense if num_vector > 0 */
   unsigned char num_literal ;
   unsigned char num_lookup ;
   }  FUNC_DESC ;


/* imports from Vensim */
CFUNCTION int VEFCC vdde_initiate(char *servname,char *topic) ;
CFUNCTION int VEFCC vdde_request(int dde_channel,char *item,char **buf,unsigned max_wait) ;
CFUNCTION int VEFCC vdde_vrequest(int dde_channel,char **item,char **buf,int nitem,unsigned max_wait) ;
CFUNCTION int VEFCC vdde_poke(int dde_channel,char *item,char *value) ;
CFUNCTION int VEFCC vdde_terminate(int dde_channel) ;
CFUNCTION int VEFCC vdde_execute(int dde_channel,char *ddecommand) ;
CFUNCTION int VEFCC vdde_wait_execute(int dde_channel,char *ddecommand,unsigned maxwait) ;
CFUNCTION void VEFCC vensim_error_message(int severity,char *str) ;
CFUNCTION void VEFCC vensim_transmit_dde(void) ;
CFUNCTION int VEFCC vensim_execute_curloop(void) ;
/* exports to Vensim */
CFUNCTION int VEFCC version_info(void) ;
CFUNCTION int VEFCC check_struct_sizes(int *pInt);
CFUNCTION unsigned short VEFCC funcversion_info(void) ;
CFUNCTION int VEFCC set_gv(GLOB_VARS *vgv) ;
CFUNCTION int VEFCC user_definition(
   int i, /* an index for requesting information - this is mapped to Flist
             but could be used another way - vensim repeatedly calls
             user_definition with i bigger by 1 until user_definition returns
             0 */
   unsigned char **sym,/* the name of the function to be used in the Vensim model */
   unsigned char **argument_desc, /* description of arguments to be shown in equation editor */
   int *num_arg, /* the number of arguments (in Vensim) the function takes 
                    note that for user loop functions this will be one less
                    than the number of arguments the function actually takes on */
   int *num_vector, /* the number of arguments that are passed as real number vectors */
   int *func_index, /* a number between 0 and 32000 that identifies the function
                       vensim_external is called with this number - normally these are sequential */
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
                    be filled in and pass it as the first argument to the function */

  int *num_literal, /* the number of literals that are passed to the function - 
                       arguments are always passed in the order literals, 
                       lookups, vectors, numbers - if num_loop is set the
                       first argument is a vector even if num_literal is positive */
  int *num_lookup  /* the number of lookup functions passed - this structure is
                      not currently accessible but will be made so in the future */
  ) ;
CFUNCTION int VEFCC simulation_setup(int iniflag) ;
CFUNCTION int VEFCC simulation_shutdown(int finalflag) ;

#define CONSTDEF_MARKER -1
#define DATADEF_MARKER -2

static void vec_arglist_init(void) ;

/* we use different names for the global variables pointer in external fucntions
   and compiled simulations to prevent name space conflicts under Linux */
#ifdef VENEXT_GLOBALS
extern GLOB_VARS *VENGV ; 
#endif

/****************************************************************************
   TERMINATING COMMENT
   do not modify anything above this comment.  If you want to add to this file
   do so below this comment 

   *************************************************************************/

#endif /* if VERSION_ONLY only version codes are included */
#endif /* do not include twice */
