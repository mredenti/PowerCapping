

```shell
venv 
pip install requirements.txt
```


## Diagram Representation 

```mermaid
flowchart TB
    A((fetch_fall3d)) --> B{execution_mode}
    B -- "container" --> C[Set <br> executable = 'hpccm' <br> + HPC Container Maker steps]
    B -- "baremetal" --> D[Set <br> executable = 'wget' <br> + download tarball]
    C --> E((Sanity check<br>job.exitcode == 0))
    D --> E((Sanity check<br>job.exitcode == 0))
```



```shell 
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d_deps.py \
    --prefix $PWD/REFRAME-TEST \
    -S execution_mode=baremetal \
    -lC 
```

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d_deps.py \
    --prefix $PWD/REFRAME-TEST \
    --system=leonardo:login \
    -S execution_mode=baremetal \
    -S valid_prog_environs=gnu \
    -lC
```