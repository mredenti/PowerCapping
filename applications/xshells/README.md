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

