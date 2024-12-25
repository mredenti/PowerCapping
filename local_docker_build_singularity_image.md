## Instructions to build seissol-leonardo image from a Docker Singularity Image


I have shared the seissol.sif image on Leonardo in the directory ``


1. Store the Seissol and "Cuda" Singularity definition files in a directory, say `$HOME/DTGEO-SEISSOL`, which we will mount into the Docker container at the location `/home/singularity`. The built images will then be available on the host machine once the container exits. 

2. **Get the Singularity Docker Image**

```
docker pull quay.io/singularity/singularity:v3.9.8-slim
```

**Note:** We need to add the `--privileged` switch to our docker command line to be able to build an image using the Docker Singularity container

3. Run an interactive shell in the Docker Singularity container and bind the `$HOME/DTGEO-SEISSOL` directory to `/home/DTGEO-SEISSOL` within the container

```
docker run -it --entrypoint=/bin/sh --privileged --rm -v ${PWD}:/home/DTGEO-SEISSOL quay.io/singularity/singularity:v3.9.8-slim
```

4. **Build cuda.sif from cuda.def** [I have sticked to the same names they are using - be sure to uncomment the line  `cuda.sif ` in  `seissol.def` as the base local image or just rename things]

From within the Docker container run the following command to firstly build the  `cuda.sif` image
   
```
singularity build /home/DTGEO-SEISSOL/cuda.sif /home/DTGEO-SEISSOL/cuda.def
```

and then the  `seissol.sif` one

```
cd /home/DTGEO-SEISSOL/
singularity build ./seissol.sif ./seissol.def
```

## Small configuration changes were necessary


**Change number of parallel processes when building on local image**

<details>
  <summary>Click me</summary>
The installation of the LLVM in (see `cuda.def`) requires a lot of memory and on my laptop it crashed. One way to reduce the memory requirements at any one instance is to lower the number of parallel process that make uses to install the library. By default `nproc` corresponds to the number of available cores on your laptop. I made the following change:

```diff
Bootstrap: docker
From: nvidia/cuda:12.3.0-devel-ubuntu22.04
Stage: build

%post
DEBIAN_FRONTEND=noninteractive

apt-get update \
&& apt-get install -y \
autoconf \
autotools-dev \
cmake \
g++ \
gcc \
gfortran \
git \
gnupg \
libnuma-dev \
libnuma1 \
libomp-dev \
libreadline-dev \
libtool \
libyaml-cpp-dev \
lsb-release \
make \
pkg-config \
python3 \
python3-numpy \
python3-pip \
software-properties-common \
vim \
wget \
wget \
&& rm -rf /var/lib/apt/lists/*

mkdir -p /home/tools/src
export PATH=/home/tools/bin:$PATH
cd /home/tools/src

ls -la 

git clone --depth 1 --branch llvmorg-17.0.6 https://github.com/llvm/llvm-project.git 
mkdir -p llvm-project/build && cd llvm-project/build
CC=/usr/bin/gcc CXX=/usr/bin/g++ cmake ../llvm -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;openmp" -DGCC_INSTALL_PREFIX=/usr -DLLVM_BUILD_LLVM_DYLIB=ON
- make -j $(nproc) && make install && cd /home/tools/src
+ make -j 2 && make install && cd /home/tools/src

wget --progress=bar:force:noscroll https://boostorg.jfrog.io/artifactory/main/release/1.83.0/source/boost_1_83_0.tar.bz2
tar -xf ./boost_1_83_0.tar.bz2 && cd boost_1_83_0
./bootstrap.sh --with-toolset=gcc --with-libraries=serialization,wave,date_time,iostreams,locale,math,random,context,regex,program_options,atomic,timer,log,fiber,chrono,thread,exception,system,test,graph,filesystem
echo "using gcc : : /usr/bin/g++-11 ;" > user-config.jam
./b2 --clean
./b2 install threading=multi variant=release toolset=gcc link=shared cxxflags="-std=c++17" visibility=hidden address-model=64 architecture=x86 -j $(nproc) --user-config="user-config.jam" && cd /home/tools/src

git clone https://github.com/KhronosGroup/SPIRV-Tools.git
cd SPIRV-Tools && python3 utils/git-sync-deps
mkdir build && cd build
cmake .. && make -j $(nproc) && make install && cd /home/tools/src

git clone --depth 1 --branch v23.10.0 https://github.com/AdaptiveCPP/AdaptiveCPP
cd AdaptiveCPP
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE:String=Release -DWITH_CPU_BACKEND:Bool=True -DWITH_ROCM_BACKEND:Bool=False -DWITH_CUDA_BACKEND:Bool=TRUE -DLLVM_DIR:String=/usr/local/lib -DCLANG_INCLUDE_PATH:String=usr/local/include/clang -DCLANG_EXECUTABLE_PATH:String=/usr/local/bin/clang++ -DBOOST_ROOT:String=/usr -DCUDA_TOOLKIT_ROOT_DIR:String=/usr/local/cuda
make -j $(nproc) && make install && cd /home/tools/src

wget --progress=bar:force:noscroll https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.6.tar.bz2
tar -xf ./openmpi-4.1.6.tar.bz2 && cd ./openmpi-4.1.6
mkdir ./build && cd ./build
../configure --with-memory-manager=none --enable-static=yes --enable-shared --enable-mpirun-prefix-by-default --with-cuda=/usr/local/cuda
make -j $(nproc) && make install && cd /home/tools/src

ldconfig

rm -rf /home/tools/src
```

</details>

**Change name of local image**

<details>
  <summary>Click me</summary>
I made the following chance since the definition file was `cuda.def`. I am guessing there is an `mpi.def` somewhere that is used as the base image when building the CPU version.

```diff
Bootstrap: localimage
- #From: cuda.sif
+ From: cuda.sif
- From: mpi.sif
+ #From: mpi.sif
Stage: build

%post
ldconfig
mkdir -p /home/tools
DEBIAN_FRONTEND=noninteractive
export PATH=/home/tools/bin:$PATH
export PKG_CONFIG_PATH=/home/tools/lib/pkgconfig:$PKG_CONFIG_PATH
cd /tmp

echo "Build HDF5"
wget --progress=bar:force:noscroll https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.11/src/hdf5-1.10.11.tar.bz2 
tar -xf hdf5-1.10.11.tar.bz2 && cd hdf5-1.10.11
CFLAGS="-fPIC" CC=mpicc FC=mpif90 ./configure --enable-parallel --with-zlib --disable-shared --enable-fortran --prefix=/home/tools/ 
make -j$(nproc) && make install && cd /tmp

echo "Build NetCDF"
wget --progress=bar:force:noscroll https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.9.2.tar.gz 
tar -xf v4.9.2.tar.gz && cd netcdf-c-4.9.2 
CFLAGS="-fPIC" CC=/home/tools/bin/h5pcc ./configure --enable-shared=no --disable-dap --disable-libxml2 --disable-byterange --prefix=/home/tools 
make -j$(nproc) && make install && cd /tmp

echo "Build parMETIS"
wget https://ftp.mcs.anl.gov/pub/pdetools/spack-pkgs/parmetis-4.0.3.tar.gz 
tar -xvf parmetis-4.0.3.tar.gz && cd parmetis-4.0.3 
sed -i 's/IDXTYPEWIDTH 32/IDXTYPEWIDTH 64/g' ./metis/include/metis.h 
CC=mpicc CXX=mpicxx make config prefix=/home/tools 
make -j$(nproc) && make install 
cp build/Linux-x86_64/libmetis/libmetis.a /home/tools/lib 
cp metis/include/metis.h /home/tools/include && cd /tmp

echo "Build Eigen"
wget --progress=bar:force:noscroll https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz 
tar -xf eigen-3.4.0.tar.gz && cd eigen-3.4.0 
mkdir -p build && cd build && cmake .. -DCMAKE_INSTALL_PREFIX=/home/tools 
make -j$(nproc) install && cd /tmp

echo "Build libxsmm"
git clone https://github.com/hfp/libxsmm.git 
cd libxsmm && git checkout 1.16.1 
make -j$(nproc) generator 
cp bin/libxsmm_gemm_generator /home/tools/bin && cd /tmp

echo "Build ASAGI"
git clone https://github.com/TUM-I5/ASAGI.git 
cd ASAGI && git submodule update --init 
mkdir build && cd build 
CC=mpicc CXX=mpicxx cmake .. -DCMAKE_INSTALL_PREFIX=/home/tools -DSHARED_LIB=off -DSTATIC_LIB=on -DNONUMA=on -DCMAKE_PREFIX_PATH=/home/tools 
make -j$(nproc) && make install && cd /tmp

echo "Build ImpalaJIT"
git clone https://github.com/uphoffc/ImpalaJIT.git 
cd ImpalaJIT && mkdir build && cd build 
CXXFLAGS="-fPIE" cmake .. -DCMAKE_INSTALL_PREFIX=/home/tools && make -j $(nproc) install && cd /tmp

echo "Build LUA"
wget --progress=bar:force:noscroll https://www.lua.org/ftp/lua-5.3.6.tar.gz 
tar -xzvf lua-5.3.6.tar.gz && cd lua-5.3.6 
make linux CC=mpicc && make local 
cp -r install/* /home/tools && cd .. && cd /tmp

echo "Build easi"
git clone https://github.com/SeisSol/easi 
cd easi && mkdir build && cd build 
CC=mpicc CXX=mpicxx cmake .. -DEASICUBE=OFF -DLUA=ON -DCMAKE_PREFIX_PATH=/home/tools -DCMAKE_INSTALL_PREFIX=/home/tools -DASAGI=ON -DIMPALAJIT=ON .. 
make -j$(nproc) && make install && cd /tmp

echo "Install GEMMForge"
pip install --user git+https://github.com/SeisSol/gemmforge.git 
pip install --user git+https://github.com/SeisSol/chainforge.git

ls -la /home/tools/bin
ls -la /home/tools/lib
ls -la /home/tools/include

echo "Build SeisSol"
export NETCDF_DIR=/home/tools
export PARMETIS_DIR=/home/tools

cd /home/tools
git clone --recursive https://github.com/SeisSol/SeisSol.git 
cd SeisSol && git submodule update --init 
for o in 4 5 6; do
  mkdir -p build_cpu && cd build_cpu 
  CC=mpicc CXX=mpicxx cmake .. -DCMAKE_PREFIX_PATH=/home/tools -DGEMM_TOOLS_LIST=auto -DASAGI=ON -DNETCDF=ON -DORDER=${o} -DHOST_ARCH=skx -DCMAKE_BUILD_TYPE=Release -DPRECISION=single
  make -j$(nproc) && cp SeisSol* /home/tools/bin 
  cd .. 
  #mkdir -p build_gpu && cd build_gpu 
  #export CXXFLAGS=-isystem\ /usr/lib/llvm-14/lib/clang/14.0.0/include
  #CC=mpicc CXX=mpicxx cmake .. -DCMAKE_PREFIX_PATH=/home/tools -DGEMM_TOOLS_LIST=auto -DASAGI=ON -DNETCDF=ON -DORDER=${o} -DHOST_ARCH=skx -DDEVICE_ARCH=sm_86 -DDEVICE_BACKEND=cuda -DCMAKE_BUILD_TYPE=Release -DPRECISION=single 
  #make -j$(nproc) && cp SeisSol* /home/tools/bin && cp seissol-launch /home/tools/bin
  #cd ..
done

%environment
  export PATH=/home/tools/bin:$PATH
```
</details>