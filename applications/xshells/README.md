# xSHELLS 

## Mini app ID

XSHELLS is a high-performance code for simulating incompressible fluids in a
spherical cavity. Due to having very few dependences, and a dedicated set of input
test cases, the main code is also used as mini-app.

| **Mini-app**        | Mini-xSHELLS |
|---------------------|--------------|
| **Repository**       | [https://gricad-gitlab.univ-grenoble-alpes.fr/schaeffn/xshells/-/tree/cheese-miniapp-fp32](https://gricad-gitlab.univ-grenoble-alpes.fr/schaeffn/xshells/-/tree/cheese-miniapp-fp32) |
| **Versions**         | CPU, GPU (backends: CUDA, HIP) |
| **Examples**         | Multiple benchmark models, each with multiple sizes |
| **Validation**       | Python script (test.py) |
| **Built-in Metric**  | Average time per simulation step |
| **Dependencies**     | MPI, FFTW, Python (to run test script) |
| **Notes**            | It is suggested to run the geodynamo benchmark for testing. |


## Thea 

```shell
wget https://gricad-gitlab.univ-grenoble-alpes.fr/schaeffn/xshells/-/archive/cheese-miniapp-fp32/xshells-cheese-miniapp-fp32.tar.gz
tar xzf xshells-cheese-miniapp-fp32.tar.gz
```

or

```shell
git clone -b cheese-miniapp-fp32 --recurse-submodules https://gricad-gitlab.univ-grenoble-alpes.fr/schaeffn/xshells.git
```

```shell
ml load openmpi/4.1.6-gcc-12.3.0-wftkmyd
ml load gcc/12.3.0-gcc-11.4.1-f7guf3f
ml load cuda/12.3.0-gcc-12.3.0-b2avf4v
ml load fftw/3.3.10-gcc-12.3.0-6gumeie # only needed to pass configuration setup
```

```shell
export CUDA_PATH=$CUDA_HOME
```