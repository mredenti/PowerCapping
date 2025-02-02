**Leonardo**

```shell
hpccm \
    --format singularity \
    --singularity-version=3.2 \
    --recipe hpcx_recipe.py \
    --userarg cluster=leonardo > singularity_leonardo.def
```

**Thea**

```shell
hpccm \
    --format singularity \
    --singularity-version=3.2 \
    --recipe hpcx_recipe.py \
    --userarg cluster=thea > singularity_thea.def
```