#
# ReFrame LEONARDO settings
#
from reframe.core.backends import register_launcher
from reframe.core.launchers import JobLauncher

@register_launcher('mpirun-mapby')
class MpirunLauncher(JobLauncher):
    def command(self, job):
        return ['mpirun', 
                '-np', str(job.num_tasks),
                f'--map-by socket:PE={job.num_cpus_per_task}',
                '--rank-by core',
                '--report-bindings']

@register_launcher('mpirun-nsys')
class MpirunLauncher(JobLauncher):
    def command(self, job):
        return ['mpirun', '-np', str(job.num_tasks), 
                '--report-bindings',
                'nsys', '-t cuda,nvtx', '--stats=true']

site_configuration = {
    "systems": [
        {
            "name": "leonardo",
            "descr": "LEONARDO",
            "hostnames": [r"^login\d+\.leonardo\.local$"],
            "modules_system": "tmod4",
            "partitions": [
                {
                    "name": "login",
                    "descr": "LEONARDO Login Nodes",
                    "scheduler": "local",
                    "launcher": "local",
                    "modules": [],
                    "access": [],
                    "max_jobs": 1,
                    "environs": ["default", "gcc", "openmpi-gcc", "openmpi-nvhpc"],
                    "processor": {
                        "arch": "icelake",
                        "platform": "x86_64",
                        "num_cpus": 32,
                        "num_cpus_per_core": 1,
                        "num_cpus_per_socket": 32,
                        "num_sockets": 1,
                    },
                },
                {
                    "name": "booster",
                    "descr": "LEONARDO Booster partition",
                    "scheduler": "slurm",
                    "sched_options": {
                        'use_nodes_option': True
                    },
                    "launcher": "srun",
                    "modules": [],
                    "container_platforms": [
                        {
                            'type': 'Singularity',
                            'default': True,
                            'modules': [],
                            'env_vars': [['ENV_VAR', 'VALUE']]
                        }
                    ],
                    "access": ["--partition=boost_usr_prod"],
                    "resources": [
                        {"name": "qos", "options": ["--qos={qos}"]},
                        {"name": "account", "options": ["--account={account}"]},
                        {"name": "gpu", "options": ["--gres=gpu:{num_gpus_per_node}"]},
                        {"name": "cpufreq", "options": ["--cpu-freq={cpufreq}"]},
                    ],
                    "max_jobs": 10,
                    "environs": [
                        "default",
                        "gcc",
                        "openmpi-gcc", 
                        "cuda",
                        "openmpi-nvhpc",
                    ],
                    "processor": {
                        "arch": "icelake",
                        "platform": "x86_64",
                        "num_cpus": 32,
                        "num_cpus_per_core": 1,
                        "num_cpus_per_socket": 32,
                        "num_sockets": 1,
                    },
                    "devices": [
                        {
                            'type': 'gpu',
                            'arch': 'sm_80',
                            'model': 'Ampere',
                            'num_devices': 4,
                        }
                    ],
                },
                {
                    "name": "dcgp",
                    "descr": "LEONARDO Data Centric General Purpose (DCGP) partition",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "max_jobs": 8,
                    "modules": [],
                    "access": ["--partition=dcgp_usr_prod"],
                    "resources": [
                        {"name": "qos", "options": ["--qos={qos}"]},
                        {"name": "account", "options": ["--account={account}"]},
                    ],
                    "environs": ["default", "gcc"],
                    "processor": {
                        "num_cpus": 112,
                        "num_cpus_per_core": 1,
                        "num_cpus_per_socket": 56,
                        "num_sockets": 2,
                    },
                },
            ],
        },
    ],
    "environments": [
        {
            "name": "default",
            "modules": [],
            "cc": "gcc",
            "cxx": "g++",
            "ftn": "gfortran",
            "features": ["openmp"],
            "extras": {"omp_flag": "-fopenmp"},
        },
        {
            "name": "gcc",
            "modules": ["gcc/12.2.0"],
            "cc": "gcc",
            "cxx": "g++",
            "ftn": "gfortran",
            "features": ["openmp"],
            "extras": {"omp_flag": "-fopenmp"},
        },
        {
            "name": "openmpi-gcc",
            "modules": ["gcc/12.2.0", "openmpi/4.1.6--gcc--12.2.0"],
            "cc": "gcc",
            "cxx": "g++",
            "ftn": "gfortran",
            "features": ["openmp", "mpi"],
            "extras": {"omp_flag": "-fopenmp"},
        },
        {
            "name": "openmpi-nvhpc",
            "modules": ["nvhpc/23.11", "openmpi/4.1.6--nvhpc--23.11"],
            "cc": "nvcc",
            "cxx": "nvc++",
            "ftn": "nvfortran",
            "features": ["openmp", "mpi"],
            "extras": {"omp_flag": "-fopenmp"},
        },
        {
            "name": "cuda",
            "modules": ["cuda/12.1"],
            "cc": "gcc",
            "cxx": "g++",
            "ftn": "gfortran",
            "features": ["openmp", "cuda"],
            "extras": {"omp_flag": "-fopenmp"},
        },
    ],
    "logging": [
        {
            "level": "debug",
            "handlers": [
                {
                    "type": "file",
                    "name": "reframe.log",
                    "level": "debug",
                    "format": "[%(asctime)s] %(levelname)s: %(check_name)s: %(message)s",  # noqa: E501
                    "append": False,
                },
                {
                    "type": "stream",
                    "name": "stdout",
                    "level": "info",
                    "format": "%(message)s",
                },
                {
                    "type": "file",
                    "name": "reframe.out",
                    "level": "info",
                    "format": "%(message)s",
                    "append": False,
                },
            ],
            "handlers_perflog": [
                {
                    "type": "filelog",
                    "prefix": "%(check_system)s/%(check_partition)s",
                    "level": "info",
                    "format": (
                        "%(asctime)s,"
                        "reframe %(version)s,"
                        "%(check_job_completion_time)s,"
                        "%(check_info)s,"
                        "%(check_modules)s,"
                        "%(check_result)s,"
                        "%(check_executable)s,"
                        "%(check_executable_opts)s,"
                        "%(check_system)s,"
                        "%(check_partition)s,"
                        "%(check_environ)s,"
                        "%(check_descr)s,"
                        "%(check_job_nodelist)s,"
                        "%(check_num_tasks_per_node)s,"
                        "%(check_num_cpus_per_task)s,"
                        "%(check_num_gpus_per_node)s,"
                        "%(check_num_tasks)s,"
                        "%(check_exclusive_access)s,"
                        "%(check_perfvalues)s"
                    ),
                    "format_perfvars": ("%(check_perf_value)s," "%(check_perf_unit)s,"),
                    "append": True,
                }
            ],
        }
    ],
    "modes": [
        {
            "name": "maintenance",
            "options": [
                "--exec-policy=async",
                "--reservation=maintenance",
                "--save-log-files",
                "--tag=acceptance",
                "--timestamp=%F_%H-%M-%S",
            ],
        },
    ],
    "general": [
        {
            "check_search_path": ["checks/"], 
            "check_search_recursive": True
        }
    ],
}
