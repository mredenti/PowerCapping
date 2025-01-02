# FALL3D

Version 0.9.0: Used for the SC5.2 Capacity Run on MN5: Volcanic dispersal at local scale: a reanalysis of the 2021 La Palma case. Ensemble runs https://fall3d-suite.gitlab.io/fall3d/tasks/setens.html are 
particularly important for this context as they would represent your typical early warning system simulation.

All the following has been based on the [FALL3D USER MANUAL](https://fall3d-suite.gitlab.io/fall3d/chapters/overview.html)

## Code Description

- [Missing Link]()
- [Container Registry](https://gitlab.com/fall3d-suite/fall3d/container_registry)

## Installation

Choose your preferred installation method:

- [Baremetal Installation](INSTALL_BAREMETAL.md)
- [Containerised Installation](INSTALL_CONTAINERISED.md)

## Validation 

- Test Suite Case
- Raikoka 

To fetch the LFS objects for the Raikoka test case, run this command:

```shell
git submodule update --init
git lfs fetch origin main # I do not know if I actually need this
```

## Simulation Cases 

- The Raikoke-2019 run case considers a deterministic (single scenario) SO2 dispersal simulation from the June 2019 Raikoke eruption. The simulation is driven by GFS model wind fields. 

- **Highly Relevant** [Eruption plumes extended more than 30 km in altitude in both phases of the Millennium eruption of Paektu (Changbaishan) volcano](https://doi.org/10.1038/s43247-023-01162-0) (Version 8.2.0 of FALL3D - no GPU acc) 
    - The simulation should be "reproducible" (TBD) as they provide Datasets, configuration input files and scripts used for the simulations described in the paper - see https://zenodo.org/records/10159966

## Suitability as Workflow 

- See [FALL3D workflow](https://fall3d-suite.gitlab.io/fall3d/chapters/tasks.html)