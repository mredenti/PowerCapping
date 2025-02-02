## Leonardo 

**Singularity**

```shell
hpccm \
    --format singularity \
    --singularity-version=3.2 \
    --recipe recipe.py \
    --userarg cluster=leonardo > singularity_leonardo.def
```

**Dockerfile**

```shell
hpccm \
    --format docker \
    --recipe recipe.py \
    --userarg cluster=leonardo > Dockerfile
```

## Thea

**Singularity**

```shell
hpccm \
    --format singularity \
    --singularity-version=3.2 \
    --recipe recipe.py \
    --userarg cluster=thea > singularity_thea.def
```

**Dockerfile**

```shell
hpccm \
    --format docker \
    --recipe recipe.py \
    --userarg cluster=thea > Dockerfile
```