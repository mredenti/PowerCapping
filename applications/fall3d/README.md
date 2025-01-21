# FALL3D

[FALL3D USER MANUAL](https://fall3d-suite.gitlab.io/fall3d/chapters/overview.html)

## Validation Case 

<details>
  <summary>Click me</summary>

### Raikoke 

- The Raikoke-2019 run case considers a deterministic (single scenario) SO2 dispersal simulation from the June 2019 Raikoke eruption. The simulation is driven by GFS model wind fields. 

- To fetch the LFS objects for the Raikoke-2019 test case, run this command:

```shell
module load git-lfs # needs to be installed on Thea
git submodule update --init
```

#### Leonardo 

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    --module-mappings power-capping/applications/fall3d/leonardo_modmap.txt \
    -S build_locally=True \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=baremetal \
    --dry-run
```

**Container**

At the moment we assume that the SIF image has already been pulled/build to the local file system. Thus, please see [HPCCM_FALL3D](./hpccm/README.md) for more information on the build process. Eventually we might consider opening the remote registry to the public and have Singularity automatically pull the image at runtime.  

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --performance-report \
    -M openmpi:openmpi/4.1.6--nvhpc--24.3 \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=container \
    -S fall3d_raikoke_test.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/fall3d.sif \
    --dry-run
```

</details>

#### Thea

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    --module-mappings power-capping/applications/fall3d/thea_modmap.txt \
    -p default \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=baremetal \
    --dry-run
```

**Container**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --performance-report \
    -M openmpi:nvhpc/24.11-gcc-12.3.0-ixv \
    -p default \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=container \
    -S fall3d_raikoke_test.image=$SCRATCH/SIF_IMAGES/fall3d.sif \
    --dry-run
```

</details>

</details>


## Test case


<details>
  <summary>Click me</summary>

#### Leonardo 

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    --module-mappings power-capping/applications/fall3d/leonardo_modmap.txt \
    -S build_locally=True \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_large_test \
    -S fall3d_raikoke_large_test.execution_mode=baremetal \
    --dry-run
```

|asctime            |reframe version|job_completion_time|info                                                                      |modules|result|executable                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |executable_opts|system  |partition|environ|descr                         |job_nodelist|num_tasks_per_node|num_cpus_per_task|num_gpus_per_node|num_tasks|exclusive_access|elapsed_time_value|elapsed_time_unit|FIELD21|FIELD22|FIELD23|FIELD24|FIELD25|FIELD26|FIELD27|FIELD28|FIELD29|FIELD30|
|-------------------|---------------|-------------------|--------------------------------------------------------------------------|-------|------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|--------|---------|-------|------------------------------|------------|------------------|-----------------|-----------------|---------|----------------|------------------|-----------------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
|2025-01-21T12:35:59|reframe 4.7.2  |2025-01-21T12:35:55|fall3d_raikoke_large_test %num_gpus=8 /1aacb0d6 @leonardo:booster+default |nvhpc  |netcdf-fortran|cmake                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |openmpi        |pass    |/leonardo_scratch/large/userinternal/mredenti/REFRAME-FALL3D-BAREMETAL/stage/leonardo/booster/default/build_fall3d/build/bin/Fall3d.x|All    |Raikoke-2019.inp              |4           |2                 |1                |leonardo         |booster  |default         |Fall3d Raikoke-2019 large test|lrdn2926         |lrdn2946|4      |8      |4      |8      |true   |566.0  |s      |       |       |
|2025-01-21T14:07:50|reframe 4.7.2  |2025-01-21T14:07:46|fall3d_raikoke_large_test %num_gpus=4 /bd4223ae @leonardo:booster+default |nvhpc  |netcdf-fortran|cmake                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |openmpi        |pass    |/leonardo_scratch/large/userinternal/mredenti/REFRAME-FALL3D-BAREMETAL/stage/leonardo/booster/default/build_fall3d/build/bin/Fall3d.x|All    |Raikoke-2019.inp              |2           |2                 |1                |leonardo         |booster  |default         |Fall3d Raikoke-2019 large test|lrdn0508         |4      |8      |4      |4      |true   |856.0  |s      |       |       |       |
|2025-01-21T14:10:03|reframe 4.7.2  |2025-01-21T14:09:58|fall3d_raikoke_large_test %num_gpus=16 /4a520641 @leonardo:booster+default|nvhpc  |netcdf-fortran|cmake                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |openmpi        |pass    |/leonardo_scratch/large/userinternal/mredenti/REFRAME-FALL3D-BAREMETAL/stage/leonardo/booster/default/build_fall3d/build/bin/Fall3d.x|All    |Raikoke-2019.inp              |4           |4                 |1                |leonardo         |booster  |default         |Fall3d Raikoke-2019 large test|lrdn2300         |lrdn2562|lrdn2582|lrdn2606|4      |8      |4      |16     |true   |359.0  |s      |


**Container**

At the moment we assume that the SIF image has already been pulled/build to the local file system. Thus, please see [HPCCM_FALL3D](./hpccm/README.md) for more information on the build process. Eventually we might consider opening the remote registry to the public and have Singularity automatically pull the image at runtime.  

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --performance-report \
    -M openmpi:openmpi/4.1.6--nvhpc--24.3 \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_large_test \
    -S fall3d_raikoke_large_test.execution_mode=container \
    -S fall3d_raikoke_large_test.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/fall3d.sif \
    --dry-run
```

|asctime            |reframe version|job_completion_time|info                                                                      |modules|result|executable                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |executable_opts|system  |partition|environ|descr                         |job_nodelist|num_tasks_per_node|num_cpus_per_task|num_gpus_per_node|num_tasks|exclusive_access|elapsed_time_value|elapsed_time_unit|FIELD21|FIELD22|FIELD23|
|-------------------|---------------|-------------------|--------------------------------------------------------------------------|-------|------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|--------|---------|-------|------------------------------|------------|------------------|-----------------|-----------------|---------|----------------|------------------|-----------------|-------|-------|-------|
|2025-01-21T12:09:02|reframe 4.7.2  |2025-01-21T12:08:56|fall3d_raikoke_large_test %num_gpus=16 /4a520641 @leonardo:booster+default|openmpi|pass  |singularity exec -B"/leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/power-capping/applications/fall3d/raikoke-2019-large:/leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/power-capping/applications/fall3d/raikoke-2019-large" -B"/leonardo_scratch/large/userinternal/mredenti/REFRAME-FALL3D-CONTAINER/stage/leonardo/booster/default/fall3d_raikoke_large_test_4a520641:/rfm_workdir" --nv --pwd /rfm_workdir --no-home /leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/SIF_IMAGES/fall3d_take2.sif Fall3d.x All Raikoke-2019.inp 4 4 1|               |leonardo|booster  |default|Fall3d Raikoke-2019 large test|lrdn0371    |lrdn0396          |lrdn3204         |lrdn3210         |4        |8               |4                 |16               |true   |362.0  |s      |
|2025-01-21T12:10:17|reframe 4.7.2  |2025-01-21T12:10:10|fall3d_raikoke_large_test %num_gpus=8 /1aacb0d6 @leonardo:booster+default |openmpi|pass  |singularity exec -B"/leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/power-capping/applications/fall3d/raikoke-2019-large:/leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/power-capping/applications/fall3d/raikoke-2019-large" -B"/leonardo_scratch/large/userinternal/mredenti/REFRAME-FALL3D-CONTAINER/stage/leonardo/booster/default/fall3d_raikoke_large_test_1aacb0d6:/rfm_workdir" --nv --pwd /rfm_workdir --no-home /leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/SIF_IMAGES/fall3d_take2.sif Fall3d.x All Raikoke-2019.inp 4 2 1|               |leonardo|booster  |default|Fall3d Raikoke-2019 large test|lrdn0402    |lrdn0406          |4                |8                |4        |8               |true              |561.0            |s      |       |       |
|2025-01-21T12:15:09|reframe 4.7.2  |2025-01-21T12:15:03|fall3d_raikoke_large_test %num_gpus=4 /bd4223ae @leonardo:booster+default |openmpi|pass  |singularity exec -B"/leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/power-capping/applications/fall3d/raikoke-2019-large:/leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/power-capping/applications/fall3d/raikoke-2019-large" -B"/leonardo_scratch/large/userinternal/mredenti/REFRAME-FALL3D-CONTAINER/stage/leonardo/booster/default/fall3d_raikoke_large_test_bd4223ae:/rfm_workdir" --nv --pwd /rfm_workdir --no-home /leonardo_scratch/large/userinternal/mredenti/POWER_CAPPING/SIF_IMAGES/fall3d_take2.sif Fall3d.x All Raikoke-2019.inp 2 2 1|               |leonardo|booster  |default|Fall3d Raikoke-2019 large test|lrdn2995    |4                 |8                |4                |4        |true            |854.0             |s                |       |       |       |


</details>

#### Thea

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    --module-mappings power-capping/applications/fall3d/thea_modmap.txt \
    -p default \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=baremetal \
    --dry-run
```

**Container**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --performance-report \
    -M openmpi:nvhpc/24.11-gcc-12.3.0-ixv \
    -p default \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=container \
    -S fall3d_raikoke_test.image=$SCRATCH/SIF_IMAGES/fall3d.sif \
    --dry-run
```

  </details>