/** \file xshells.hpp
Compile-time parmeters and customizable functions for XSHELLS.
*/

#ifndef XS_H
	/* DO NOT COMMENT */
	#define XS_H

///  EXECUTION CONTROL  ///
/// 1. stable and tested features ///

/* call custom_diagnostic() (defined below) from main loop to perform and store custom diagnostics */
#define XS_CUSTOM_DIAGNOSTICS

/* enable variable time-step adjusted automatically */
#define XS_ADJUST_DT

/* XS_LINEAR use LINEAR computation : no u.grad(u), no J0xB0  */
//#define XS_LINEAR

/* Impose arbitrary stationary flow at the boundaries (for Diapir/Monteux) */
//#define XS_SET_BC

/* use variable conductivity profile eta(r) [see definition of profile in calc_eta() below */
//#define XS_ETA_PROFILE

/* Variable L-truncation : l(r) = LMAX * sqrt(r/(rmax*VAR_LTR))  +1 */
//#define VAR_LTR 0.5

///  EXECUTION CONTROL  ///
/// 2. unstable and beta features ///

/* Hyperdiffusion : enable enhanced diffusion constants (see xshells.par)*/
#define XS_HYPER_DIFF



#ifdef XS_ETA_PROFILE
	// variable magnetic diffusivity is used :
	#define XS_ETA_VAR
#endif

#else


#ifdef XS_CUSTOM_DIAGNOSTICS
/// compute custom diagnostics. They can be stored in the all_diags array , which is written to the energy.jobname file.
/// own(ir) is a macro that returns true if the shell is owned by the process (useful for MPI).
/// i_mpi is the rank of the mpi process (0 is the root).
/// This function is called outside an OpenMP parallel region, and it is permitted to use openmp parallel constructs inside.
/// After this function returns, the all_diags array is summed accross processes and written in the energy.jobname file.
void custom_diagnostic(diagnostics& all_diags)
{
	// Uncomment the lines below to use corresponding diagnostics.
	#include "diagnostics/split_energies.cpp"
	#include "diagnostics/nusselt_number.cpp"
	//#include "diagnostics/azimuthal_drift_rate.cpp"   // useful for the geodynamo benchmark
	#include "diagnostics/geodynamo_surface_dipole.cpp"
	//#include "diagnostics/bsurf_record.cpp"
	#include "diagnostics/dissipation.cpp"
	#include "diagnostics/convective_power.cpp"
	//#include "diagnostics/z_average.cpp"
}
#endif


#ifdef XS_ETA_PROFILE

/// define magnetic diffusivity eta as a function of r
/// discontinuous profiles supported.
void calc_eta(double eta0)
{
	static double etam = 0;
	
	if (etam==0) {
		etam = mp.var["etam"];		// value read from xshells.par file.
	}

	for (int i=0; i<NR; i++) {
		etar[i] = eta0;				// eta0 by default.
		if ((i > NM) && (etam))		etar[i] = eta0 * etam; 		// mantle almost insulating
	}
}
#endif


/* DO NOT REMOVE AND DO NOT ADD ANYTHING BEYOND THIS LINE */
#endif

