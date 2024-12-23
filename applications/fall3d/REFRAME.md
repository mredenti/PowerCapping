

```shell
venv 
pip install requirements.txt
```


## Diagram Representation 

```mermaid
flowchart TB
    %% Legend
    subgraph Legend
    L1[Square: ReFrame Test or Step]:::test
    L2{Rhombus: Conditional Choice}:::conditional
    L3([Circle: Flow Connector]):::flow
    end

    classDef test fill:#f8f8ff,stroke:#000,stroke-width:1px
    classDef conditional fill:#faf7f0,stroke:#000,stroke-width:1px,stroke-dasharray: 5 5
    classDef flow fill:#ffffff,stroke:#000,stroke-width:2px

    %% Diagram
    subgraph "ReFrame Workflow"
    A((Test Definition)):::flow --> B["fetch_fall3d\n(Class Declaration)"]:::test
    B --> C{@run_before('run')\n(pick_mode hook)}:::conditional
    C -- "execution_mode = container" --> D["Set executable='hpccm'\n+ HPC Container Maker steps"]:::test
    C -- "execution_mode = baremetal" --> E["Set executable='wget'\n+ Wget tarball download steps"]:::test
    D --> F((Run the job)):::flow
    E --> F((Run the job)):::flow
    F --> G(["@sanity_function\nvalidate_download"]):::test
    G --> H((job.exitcode == 0?)):::conditional
    H -- "Yes" --> I((Test Pass))
    H -- "No" --> J((Test Fail))
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