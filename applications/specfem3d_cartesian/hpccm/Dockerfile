# Container recipe

FROM docker.io/nvidia/cuda@sha256:1608a19a5d6f013d36abfb9ad50a42b4c0ef86f4ab48e351c6899f0280b946c1 AS devel

# Python
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 && \
    rm -rf /var/lib/apt/lists/*

# Mellanox OFED version 5.8-2.0.3.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox | apt-key add - && \
    mkdir -p /etc/apt/sources.list.d && wget -q -nc --no-check-certificate -P /etc/apt/sources.list.d https://linux.mellanox.com/public/repo/mlnx_ofed/5.8-2.0.3.0/ubuntu22.04/mellanox_mlnx_ofed.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ibverbs-providers \
        ibverbs-utils \
        libibmad-dev \
        libibmad5 \
        libibumad-dev \
        libibumad3 \
        libibverbs-dev \
        libibverbs1 \
        librdmacm-dev \
        librdmacm1 && \
    rm -rf /var/lib/apt/lists/*

# KNEM version 1.1.4
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        git && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch knem-1.1.4 https://gitlab.inria.fr/knem/knem.git knem && cd - && \
    mkdir -p /usr/local/knem && \
    cd /var/tmp/knem && \
    mkdir -p /usr/local/knem/include && \
    cp common/*.h /usr/local/knem/include && \
    rm -rf /var/tmp/knem
ENV CPATH=/usr/local/knem/include:$CPATH

# XPMEM branch master
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        ca-certificates \
        file \
        git \
        libtool \
        make && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch master https://github.com/hjelmn/xpmem.git xpmem && cd - && \
    cd /var/tmp/xpmem && \
    autoreconf --install && \
    cd /var/tmp/xpmem &&   ./configure --prefix=/usr/local/xpmem --disable-kernel-module && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/xpmem
ENV CPATH=/usr/local/xpmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/xpmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/xpmem/lib:$LIBRARY_PATH

# UCX https://github.com/openucx/ucx.git v1.13.1
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        autoconf \
        automake \
        binutils-dev \
        ca-certificates \
        file \
        git \
        libnuma-dev \
        libtool \
        make \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch v1.13.1 https://github.com/openucx/ucx.git ucx && cd - && \
    cd /var/tmp/ucx && \
    ./autogen.sh && \
    cd /var/tmp/ucx &&   ./configure --prefix=/usr/local/ucx --disable-assertions --disable-debug --disable-doxygen-doc --disable-logging --disable-params-check --enable-optimizations --with-cuda=/usr/local/cuda --with-knem=/usr/local/knem --with-rdmacm --with-verbs --with-xpmem=/usr/local/xpmem && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/ucx
ENV CPATH=/usr/local/ucx/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/ucx/lib:$LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH

# PMIX version 3.1.5
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        hwloc \
        libevent-dev \
        make \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openpmix/openpmix/releases/download/v3.1.5/pmix-3.1.5.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/pmix-3.1.5.tar.gz -C /var/tmp -z && \
    cd /var/tmp/pmix-3.1.5 &&   ./configure --prefix=/usr/local/pmix && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/pmix-3.1.5 /var/tmp/pmix-3.1.5.tar.gz
ENV CPATH=/usr/local/pmix/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/pmix/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/pmix/bin:$PATH

# OpenMPI version 4.1.6
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        file \
        hwloc \
        libnuma-dev \
        make \
        openssh-client \
        perl \
        tar \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://www.open-mpi.org/software/ompi/v4.1/downloads/openmpi-4.1.6.tar.bz2 && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/openmpi-4.1.6.tar.bz2 -C /var/tmp -j && \
    cd /var/tmp/openmpi-4.1.6 &&   ./configure --prefix=/usr/local/openmpi --disable-getpwuid --enable-mpi-fortran=yes --enable-orterun-prefix-by-default --with-cuda --with-pmix=/usr/local/pmix --with-ucx=/usr/local/ucx --with-verbs && \
    make -j$(nproc) && \
    make -j$(nproc) install && \
    rm -rf /var/tmp/openmpi-4.1.6 /var/tmp/openmpi-4.1.6.tar.bz2
ENV LD_LIBRARY_PATH=/usr/local/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/openmpi/bin:$PATH

ENV CUDA_INC=/usr/local/cuda-12.6/include \
    CUDA_LIB=/usr/local/cuda-12.6/lib64

RUN mkdir -p /opt && cd /opt && git clone --recursive https://gitlab.com/mir1995/specfem3d.git specfem3d && cd - && cd /opt/specfem3d && git checkout ea3d9648b4989454eeb1b2a3f370e009f5d4c81a && cd -

RUN cd /opt/specfem3d && \
    ./configure CC="gcc" CXX="g++" FC="gfortran" CFLAGS="-O3" FCFLAGS="-O3" MPIFC=mpif90 --with-mpi --with-cuda=cuda11 USE_BUNDLED_SCOTCH=1 && \
    make -j$(nproc)

ENV PATH=/opt/specfem3d/bin:$PATH

FROM docker.io/nvidia/cuda@sha256:4cf7f8137bdeeb099b1f2de126e505aa1f01b6e4471d13faf93727a9bf83d539 AS runtime

# Python
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 && \
    rm -rf /var/lib/apt/lists/*

# Mellanox OFED version 5.8-2.0.3.0
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget && \
    rm -rf /var/lib/apt/lists/*
RUN wget -qO - https://www.mellanox.com/downloads/ofed/RPM-GPG-KEY-Mellanox | apt-key add - && \
    mkdir -p /etc/apt/sources.list.d && wget -q -nc --no-check-certificate -P /etc/apt/sources.list.d https://linux.mellanox.com/public/repo/mlnx_ofed/5.8-2.0.3.0/ubuntu22.04/mellanox_mlnx_ofed.list && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ibverbs-providers \
        ibverbs-utils \
        libibmad-dev \
        libibmad5 \
        libibumad-dev \
        libibumad3 \
        libibverbs-dev \
        libibverbs1 \
        librdmacm-dev \
        librdmacm1 && \
    rm -rf /var/lib/apt/lists/*

# KNEM
COPY --from=devel /usr/local/knem /usr/local/knem
ENV CPATH=/usr/local/knem/include:$CPATH

# XPMEM
COPY --from=devel /usr/local/xpmem /usr/local/xpmem
ENV CPATH=/usr/local/xpmem/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/xpmem/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/xpmem/lib:$LIBRARY_PATH

# UCX
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libbinutils && \
    rm -rf /var/lib/apt/lists/*
COPY --from=devel /usr/local/ucx /usr/local/ucx
ENV CPATH=/usr/local/ucx/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/ucx/lib:$LD_LIBRARY_PATH \
    LIBRARY_PATH=/usr/local/ucx/lib:$LIBRARY_PATH \
    PATH=/usr/local/ucx/bin:$PATH

# PMIX
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libevent-2.* \
        libevent-pthreads-2.* && \
    rm -rf /var/lib/apt/lists/*
COPY --from=devel /usr/local/pmix /usr/local/pmix
ENV CPATH=/usr/local/pmix/include:$CPATH \
    LD_LIBRARY_PATH=/usr/local/pmix/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/pmix/bin:$PATH

# OpenMPI
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        hwloc \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*
COPY --from=devel /usr/local/openmpi /usr/local/openmpi
ENV LD_LIBRARY_PATH=/usr/local/openmpi/lib:$LD_LIBRARY_PATH \
    PATH=/usr/local/openmpi/bin:$PATH

COPY --from=devel /opt/specfem3d /opt/specfem3d

ENV PATH=/opt/specfem3d/bin:$PATH

ENTRYPOINT ["/bin/sh"]
