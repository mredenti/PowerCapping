# Power Capping

## Requirements & Setup

<details><summary>Click to expand</summary>

Before getting started, ensure that you have the following software installed on your system

- [Reframe v4.7.2](https://reframe-hpc.readthedocs.io/en/v4.7.2/)
- [HPC Container Maker v24.10.0](https://github.com/NVIDIA/hpc-container-maker/blob/v24.10.0/README.md) - an open source tool to ease the creation of container specification files

You can follow these steps to create a virtual environment and install the necessary Python packages listed in the `requirements.txt` file:

1. **Create a pip virtual environment**

```shell
python3 -m venv venv/power_capping
source venv/power-capping
```

2. **Install the requirements**

```shell 
pip install -r requirements.txt
```

</details>


## Reframe Leonardo Settings

<details><summary>Click to expand</summary>

![Leonardo Configuration](img/leonardo_settings.svg)

</details>
