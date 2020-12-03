#ifndef IO500_PHASE_IOR_H
#define IO500_PHASE_IOR_H

#include <ior.h>
#include <io500-util.h>

typedef struct{
  int no_run;
  char * api;

  int filePerProc;
  int uniqueDir;
  char * transferSize;
  char * blockSize;
  char * hintsFileName;
  int verbosity;
} opt_ior_easy;

extern opt_ior_easy ior_easy_o;

typedef struct{
  int no_run;
  int collective;
  char * api;
  char * hintsFileName;

  int segments;
  int verbosity;
} opt_ior_hard;

extern opt_ior_hard ior_hard_o;

typedef struct{
  int no_run;
  char * api;
  char * hintsFileName;

  int random_prefill_bytes;
  uint64_t block_size;
  int verbosity;
} opt_ior_rnd;

extern opt_ior_rnd ior_rnd_o;


void ior_easy_add_params(u_argv_t * argv);
void ior_hard_add_params(u_argv_t * argv);
void ior_rnd_add_params(u_argv_t * argv);

// Generic helpers
double ior_process_write(u_argv_t * argv, FILE * out, IOR_point_t ** res_out);
double ior_process_read(u_argv_t * argv, FILE * out, IOR_point_t ** res_out);

#endif
