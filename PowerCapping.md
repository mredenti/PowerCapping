# Planned Activity Summary

This planned activity is organized into two main milestones:

1. **Milestone 1**: Compilation, testing, and identification of suitable test cases for each CHEESE app.
2. **Milestone 2**: Running a power capping study on the selected applications.

Below you can find more information about the CHEESE-2P flagship codes being considered and the current status for Milestone 1.

### Code IDs

<details>
  <summary>Click me</summary>

| Code                                                         | Domain                                  | Description                                                                                                                                                                                                                                                                                | Version | Dependencies                                                                                   |
|--------------------------------------------------------------|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|------------------------------------------------------------------------------------------------|
| [FALL3D](applications/fall3d/README.md)                     | Physical Volcanology                    | Simulates the transport and deposition of volcanic ash/tephra produced by explosive eruptions.                                                                                                                                                                                      | 9.0.1   | Fortran, (MPI), OpenACC (NVFortran), netCDF-Fortran with netCDF-4 support, (PnetCDF)                                                |
| [SPECFEM3D_Cartesian](https://github.com/SPECFEM/specfem3d)  | Computational Seismology                | Simulates acoustic (fluid), elastic (solid), coupled acoustic/elastic, poroelastic seismic wave propagation in any type of conforming mesh of hexahedra.                                                                                                                  | v4.1.1  | Fortran2003, (CUDA), (MPI), (CUBIT), (SCOTCH), (ADIOS), (HDF5)                                                         |
| [SPECFEM3D_GLOBE](https://github.com/SPECFEM/specfem3d_globe)| Computational Seismology                | Simulates global and regional (continental-scale) seismic wave propagation.                                                                                                                                                                                                | -       | Fortran, MPI                                                                                    |
| [XSHELLS](applications/xshells/README.md)                   | Magneto-Hydrodynamics (Earth’s Interior)| Simulates geophysical and astrophysical flows in rotating spherical shells, including magnetic field generation and evolution in magneto-hydrodynamic contexts.                                                                                                                     | -       | NVHPC, Vulkan FFT, MPI                                                                          |
| seissol                                                      | -                                       | -                                                                                                                                                                                                                                                                                          | -       | -                                                                                              |
| elmer-ice                                                    | -                                       | -                                                                                                                                                                                                                                                                                          | -       | -                                                                                              |
| exa-hype                                                     | -                                       | -                                                                                                                                                                                                                                                                                          | -       | -                                                                                              |

---

## Backup Codes

The following codes are to be considered if any of the main targeted codes does not come through

| Code                                                          | Domain                     | Description                                                                                                                                                              | Version | Dependencies |
|---------------------------------------------------------------|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|--------------|
| [TANDEM](https://tandem.readthedocs.io/en/latest/)            | Computational Seismology  | A scalable discontinuous Galerkin code on unstructured curvilinear grids for linear elasticity problems and sequences of earthquakes and aseismic slip                  | -       | C++, Petsc   |



</details>

## Milestone 1

### Compilation Status, Testing Status, and Test Case Identified


<details>
  <summary>Click me</summary>

| Code                                                                    | leonardo-baremetal                                                         | leonardo-container | thea-baremetal | thea-container | Validation Test | Test Case Identified |
|-------------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------|----------------|----------------|-----------------|----------------------|
| [FALL3D](applications/fall3d/README.md)                                 | :heavy_check_mark:                                                                         | :heavy_check_mark:                   |:heavy_check_mark:              | :heavy_check_mark:            |      :heavy_check_mark:            | :heavy_check_mark:                   |
| [Seissol](applications/seissol/local_docker_build_singularity_image.md)                                 | :heavy_check_mark:                                                                          | Not Started                 | Not Started            | Ongoing             |      Ongoing          | :heavy_check_mark:                   |
| [ExaHype](https://gitlab.lrz.de/exahype/ExaHyPE-Engine)                                 | Not Started                                                                          | Not Started                 | Not Started            | Ongoing             |      Ongoing          | Meeting scheduled to discuss                   |
| [SPECFEM3D_Cartesian](https://github.com/SPECFEM/specfem3d)              | :heavy_check_mark:                                                                          | Not started        | Not started    | Not started    |      Not started            | :heavy_check_mark:, Waiting Data From Developers                  | 
| [SPECFEM3D_GLOBE](https://github.com/SPECFEM/specfem3d_globe)            | :heavy_check_mark:                                                                         | Not started        | Not started    | Not started    |        Not started          | :heavy_check_mark:, Waiting Data From Developers                   |
| [ELMER_ICE](https://elmerice.elmerfem.org/)            | Not Started                                                                          | Not started        | Not started    | Not started    |        Not started          | :heavy_check_mark:, Waiting Data From Developers                   |
| [XSHELLS](applications/xshells/README.md)                              | OK                                                                          | Not started        | OK | Not started    |      Not started           | :heavy_check_mark: , waiting data from developers                  |
| [TANDEM](https://tandem.readthedocs.io/en/latest/)                      | Ok                                                                          | Not started        | Ok             | Not started    |         Not started        | Backup if no response from XSHELLS                   |



_Note: The table will be updated as we make progress. Once the applications are successfully compiled and tested, suitable test cases will be chosen and documented._

</details>


## Containerisation 


<details>
  <summary>Click me</summary>

- [NVIDIA HPC SDK](https://ngc.nvidia.com/catalog/containers/nvidia:nvhpc) containers are available on NGC. Two types of containers are provided, "devel" containers which contain the entire HPC SDK development environment, and "runtime" container which include only the components necessary to redistribute software built with the HPC SDK. Some care must will have to be taken in ensuring the UCX library has been configured with all communication mechanmism of interest, eg. `cuda_ipc`, `gdrcopy`. Alternatively one can install all the stack using the HPCCM building blocks, see for example [Generic recipe to build a OFED+UCX+MPI+CUDA container environment](https://github.com/NVIDIA/hpc-container-maker/blob/master/recipes/osu_benchmarks/common.py)
- [HPC CONTAINER MAKER DOCS](https://docs.nvidia.com/hpc-sdk//hpc-sdk-container/index.html)
- [NVIDIA HPC SDK CATALOG - NVIDIA GPU Cloud](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags)

## Important considerations 

**Note** The dataset should be typically mounted from the host into the running container. Including datasets in the container image is bad practice and is not recommended. Datasets can be large and bloat the size of the container image and are often specific to a particular usage. https://docs.nvidia.com/hpc-sdk//hpc-sdk-container/index.html#multi-architecture-support

However, this raises an important question about reproducibility aspects. We are not developing a tutorial. In order to have our work fully reproducible we must also make available the data input (input files, mesh files and so on). We will have to consider whether actually embedding this input data in the image or alternatively make it available somewhere. In CINECA we do not have a registry for the images and thush we will probably have to resort to Docker Hub or Singularity Hub. For the data we also need to find a solution. Git lfs pointers to remote repositories like FALL3D does are out of the question as they are not under our direct control and we can not ensure they will still be there in the future

</details>

## Useful References

<details>
  <summary>Click me</summary>
  
  - **Specfem3d**
    - [SPECFEM3D won the Gordon Bell award for best performance at the SuperComputing 2003](https://dl.acm.org/doi/10.1145/1048935.1050155)
  - **Reproducibility with Containers**
    - [The Scientific Filesystem](https://doi.org/10.1093/gigascience/giy023)
  - **Power Capping**  
    - [Understanding the Impact of Dynamic Power Capping on Application Progress](https://gitlab.hpc.cineca.it/cheese2p-hls/power-capping/-/blob/thea/fall3d/specfem/PowerCapping.md)
  - **GraceHopper**
    - [Understanding Data Movement in Tightly Coupled Heterogeneous Systems: A Case Study with the Grace Hopper Superchip](https://arxiv.org/pdf/2408.11556v2)
  - **Scientific Impact**
    - [In this video from the PASC18 conference in Basel, Alice-Agnes Gabriel presents: Unravelling Earthquake Dynamics through Extreme-Scale Multiphysics Simulations.](https://www.youtube.com/watch?v=nJlzFwYtau0&t=10s) 
  
</details>