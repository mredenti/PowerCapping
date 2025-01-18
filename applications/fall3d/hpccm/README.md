# Docker/Singularity container specification files with Nnvidia HPCCM


Below you can find the instructions to generate the Singularity definition file for Fall3d targeting the Leonardo and Thea supercomputers

**Leonardo**

```shell
hpccm \
    --format singularity \
    --singularity-version=3.2 \
    --recipe spack_recipe.py \
    --userarg cluster=leonardo > singularity_leonardo.def
```

**Thea**

```shell
hpccm \
    --format singularity \
    --singularity-version=3.2 \
    --recipe spack_recipe.py \
    --userarg cluster=thea > singularity_thea.def
```



