cmake_minimum_required(VERSION 3.10)
project(TestMPI Fortran)

# Request that CMake find an MPI installation for C, C++, and Fortran
find_package(MPI REQUIRED)

# Print out what was found
message(STATUS "MPI_C_FOUND: ${MPI_C_FOUND}")
message(STATUS "MPI_CXX_FOUND: ${MPI_CXX_FOUND}")
message(STATUS "MPI_Fortran_FOUND: ${MPI_Fortran_FOUND}")

message(STATUS "MPI_C_COMPILER: ${MPI_C_COMPILER}")
message(STATUS "MPI_C_INCLUDE_PATH: ${MPI_C_INCLUDE_PATH}")
message(STATUS "MPI_C_LIBRARIES: ${MPI_C_LIBRARIES}")

message(STATUS "MPI_CXX_COMPILER: ${MPI_CXX_COMPILER}")
message(STATUS "MPI_CXX_INCLUDE_PATH: ${MPI_CXX_INCLUDE_PATH}")
message(STATUS "MPI_CXX_LIBRARIES: ${MPI_CXX_LIBRARIES}")

message(STATUS "MPI_Fortran_COMPILER: ${MPI_Fortran_COMPILER}")
message(STATUS "MPI_Fortran_INCLUDE_PATH: ${MPI_Fortran_INCLUDE_PATH}")
message(STATUS "MPI_Fortran_LIBRARIES: ${MPI_Fortran_LIBRARIES}")


