

```shell
venv 
pip install requirements.txt
```


## Diagram Representation 

```mermaid
flowchart TB
    %% Legend (top-to-bottom)
    subgraph Legend
        direction TB
        L1[Square: ReFrame Test or Step]
        L2{Rhombus: Conditional Choice}
        L3((Circle: Flow Connector))
    end

    %% Diagram: top to bottom
    A((Test Definition)) --> B[fetch_fall3d (Class Declaration)]
    B --> C{"@run_before('run') (pick_mode)"}
    C -- "execution_mode=container" --> D[executable='hpccm'\n(HPC Container Maker)]
    C -- "execution_mode=baremetal" --> E[executable='wget'\n(Download tarball)]
    D --> F((Run the Job))
    E --> F((Run the Job))
    F --> G["@sanity_function\nvalidate_download"]
    G --> H((job.exitcode == 0?))
    H -- "Yes" --> I((Test Pass))
    H -- "No" --> J((Test Fail))


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