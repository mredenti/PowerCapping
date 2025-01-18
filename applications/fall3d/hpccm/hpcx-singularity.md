## Intro
This page describes an approach to create a standalone Singularity container
with MLNX_OFED and HPCX inside. Container image contains all dependencies and
may contain any OS different from host OS.

This instruction can be used as a guide for creating containers with any OS and
HPCX inside, the only limitation is that MLNX_OFED, HPCX, and OS should be
compatible with each other.

Singularity is a container solution with some [differences](http://singularity.lbl.gov/faq#what-is-so-special-about-singularity).

Singularity web: http://singularity.lbl.gov/

## Table of content
* [Build container](#build-container)
* [Run container](#run-container)
* [Notes](#notes)

## Build container
Initial setup:
```sh
$ uname -a
Linux r-vmb-ubuntu16-u4-x86-64-mofed-checker 4.4.0-59-generic #80-Ubuntu SMP Fri Jan 6 17:47:47 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux

$ lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 16.04.1 LTS
Release:        16.04
Codename:       xenial

$ pwd
/opt/sing

$ tree -A -L 2
.
├── hpcx -> hpcx-v2.1.0-gcc-MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64
├── hpcx-u16.04.singularity
├── hpcx-v2.1.0-gcc-MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64
│   ├── archive
│   ├── fca -> hcoll
│   ├── hcoll
│   ├── hpcx-cuda-init-ompi-a7dfd94.sh
│   ├── hpcx-cuda-init.sh -> hpcx-cuda-init-ompi-a7dfd94.sh
│   ├── hpcx-init-ompi-a7dfd94.sh
│   ├── hpcx-init.sh -> hpcx-init-ompi-a7dfd94.sh
│   ├── hpcx-mt-init-ompi-a7dfd94.sh
│   ├── hpcx-mt-init.sh -> hpcx-mt-init-ompi-a7dfd94.sh
│   ├── knem
│   ├── modulefiles
│   ├── mxm
│   ├── ompi-a7dfd94
│   ├── README.txt
│   ├── sharp
│   ├── sources
│   ├── ucx
│   ├── utils
│   └── VERSION
├── hpcx-v2.1.0-gcc-MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64.tbz
└── MOFED
    ├── MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64
    ├── MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64.iso
    └── MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64.tgz
```

Where:
 - `hpcx-v2.1.0-gcc-MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64/` is an unpacked HPCX v2.1 package for Ubuntu 16.04, can be downloaded with this command: `wget http://www.mellanox.com/downloads/hpc/hpc-x/v2.1/hpcx-v2.1.0-gcc-MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64.tbz`. `hpcx` link is used for simplification of the recipe file.
 - 'MOFED/' contains MLNX_OFED v4.3-1.0.1.0 for Ubuntu 16.04.
 - `hpcx-u16.04.singularity` is a Singularity Recipe file with build instructions.

Build Singularity sandbox (_editable_ image):
```sh
export SINGULARITY_CACHEDIR=/opt/sing/.cache
sudo -E singularity build --sandbox u16.04-sandbox hpcx-u16.04.singularity
```
Directory `u16.04-sandbox/` will be created.

Create `/opt/sing/` in container so Singularity will mount it automatically:
```sh
sudo singularity exec -w u16.04-sandbox/ mkdir -p /opt/sing
```

Now step into the container and install MOFED:
```
$ sudo singularity exec -w u16.04-sandbox/ bash
(singularity)# cd MOFED/MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64
(singularity)# ./mlnxofedinstall
```

Creating a portable (read-only) image:
```sh
$ sudo -E singularity build hpcx-u16.04.simg u16.04-sandbox/
Building image from sandbox: u16.04-sandbox/
Building Singularity image...
Singularity container built: hpcx-u16.04.simg
Cleaning up...
```


## Run container
To use Singularity in Mellanox/HPCX need to load env module: `module load tools/singularity`.

Run `osu_latency` test:
```sh
$ mpirun -np 2 --map-by node -mca btl self singularity exec hpcx-u16.04.simg /hpcx/ompi-a7dfd94/tests/osu-micro-benchmarks-5.3.2/osu_latency
# OSU MPI Latency Test v5.3.2
# Size          Latency (us)
0                       1.55
1                       1.55
2                       1.55
4                       1.55
8                       1.54
16                      1.55
32                      1.55
64                      1.65
128                     2.19
256                     2.23
512                     2.35
1024                    2.64
2048                    2.89
4096                    3.51
8192                    5.00
16384                   6.44
32768                   8.91
65536                  14.12
131072                 25.05
262144                 27.31
524288                 49.03
1048576                92.53
2097152               178.95
4194304               351.24
```

## Notes
 - Installing MOFED into container works nice only if host and container OS are
   the same. MOFED installers required distro specific packages and kernel
   version, so even installing them can be a problem since container OS doesn't
   have its own kernel. If it is still required, MOFED could be installed with
   `--user-space-only` option.
 - Some binaries (like `ucx_info` and test executables) might loose execution
   bit on copying to container. The recipe contains a fix for it.
