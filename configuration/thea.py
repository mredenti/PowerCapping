#
# ReFrame THEA settings
#
from reframe.core.backends import register_launcher
from reframe.core.launchers import JobLauncher

@register_launcher('mpirun-mapby')
class MpirunLauncher(JobLauncher):
    def command(self, job):
        return ['mpirun', 
                '-np', str(job.num_tasks),
                f'--map-by ppr:{job.num_tasks_per_node}:node:PE={job.num_cpus_per_task}',
                '--report-bindings']
        
@register_launcher('srun-pmix')
class MpirunLauncher(JobLauncher):
    def command(self, job):
        return ['srun', 
                '--mpi=pmix',
                f'-N {job.num_tasks}',
                f'-n {job.num_tasks}',
                f'--cpus-per-task={job.num_cpus_per_task}',
               ]
        
@register_launcher('srun-pmi2')
class MpirunLauncher(JobLauncher):
    def command(self, job):
        return ['srun', 
                '--mpi=pmi2',
                f'-N {job.num_tasks}',
                f'-n {job.num_tasks}',
                f'--cpus-per-task={job.num_cpus_per_task}',
               ]

@register_launcher('mpirun-mapby-nsys')
class MpirunLauncher(JobLauncher):
    def command(self, job):
        return ['mpirun', 
                '-np', str(job.num_tasks),
                f'--map-by ppr:{job.num_tasks_per_node}:node:PE={job.num_cpus_per_task}',
                '--report-bindings',
                'nsys profile', 
                '-o ${PWD}/output_%q{OMPI_COMM_WORLD_RANK}',
                '-t cuda,nvtx', 
                '--stats=true',
                '--cuda-memory-usage=true']

site_configuration = {
    "systems": [
        {
            "name": "thea",
            "descr": "NVIDIA MULTI-NODE GRACE-HOPPER EVALUATION SYSTEM",
            "hostnames": [r'login\d+'],
            "modules_system": "tmod4",
            "partitions": [
                {
                    "name": "login",
                    "descr": "THEA X86 LOGIN NODE",
                    "scheduler": "local",
                    "launcher": "local",
                    "modules": [],
                    "access": [],
                    "environs": ["default"],
                    "max_jobs": 1,
                },
                {
                    "name": "ggcompile",
                    "descr": "THEA GRACE SUPERCHIP CPU+GPU COMPILATION NODE",
                    "scheduler": "slurm",
                    "sched_options": {
                        'use_nodes_option': True
                    },
                    "launcher": "mpirun",
                    "modules": [],
                    "access": [
                        "--partition=ggcompile",
                        "--oversubscribe",
                    ],
                    "resources": [
                        {
                            "name": "cpufreq", 
                            "options": ["--cpu-freq={cpufreq}"]
                        },
                    ],
                    "max_jobs": 1,
                    "prepare_cmds": [
                        ". /global/scratch/groups/gh/bootstrap-gh-env.sh",
                        "module purge"
                    ],
                    "environs": [
                        "default",
                        "gcc-12.3.0",
                        "nvhpc-24.9",
                    ],
                    "processor": {
                        "arch": "neoverse-v2",
                        "platform": "arm64",
                        "num_cpus": 144,
                        "num_cpus_per_core": 1,
                        "num_cpus_per_socket": 72,
                        "num_sockets": 2,
                    },
                },
                {
                    "name": "gh",
                    "descr": "THEA GRACE HOPPER",
                    "scheduler": "slurm",
                    "sched_options": {
                        'use_nodes_option': True
                    },
                    "launcher": "srun",
                    "max_jobs": 1,
                    "modules": [],
                    "access": [
                        "--partition=gh"
                    ],
                    "resources": [
                        {"name": "qos", "options": ["--qos={qos}"]},
                        {"name": "account", "options": ["--account={account}"]},
                        {"name": "nodes", "options": ["--nodes={nodes}"]},
                    ],
                    "prepare_cmds": [
                        ". /global/scratch/groups/gh/bootstrap-gh-env.sh",
                        "module purge"
                    ],
                    "container_platforms": [
                        {
                            'type': 'Singularity',
                            'default': True,
                            'modules': [],
                            'env_vars': []
                        }
                    ],
                    "environs": [
                        "default", 
                        "gcc-12.3.0", 
                        "nvhpc-24.9",
                    ],
                    "processor": {
                        "arch": "neoverse-v2",
                        "platform": "arm64",
                        "num_cpus": 72,
                        "num_cpus_per_core": 1,
                        "num_cpus_per_socket": 1,
                        "num_sockets": 1,
                    },
                    "devices": [
                        {
                            'type': 'gpu',
                            'arch': 'sm_90',
                            'num_devices': 1,
                        }
                    ],
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
            "name": "gcc-12.3.0",
            "modules": [
                "gcc/12.3.0-gcc-11.4.1-f7guf3f",
                "openmpi/4.1.6-gcc-12.3.0-wftkmyd",
                "cuda/12.3.0-gcc-12.3.0-b2avf4v",
                "fftw/3.3.10-gcc-12.3.0-6gumeie"
            ],
            "cc": "gcc",
            "cxx": "g++",
            "ftn": "f90",
            "features": ["openmp"],
            "extras": {"omp_flag": "-fopenmp"},
        },
        {
            "name": "nvhpc-24.9",
            "modules": [
                "nvhpc/24.9-gcc-12.3.0-ezrvqtt", 
                "openmpi/4.1.6-gcc-12.3.0-wftkmyd",
            ],
            "env_vars" : [
                [
                    "NVHPC_HOME", 
                    "/global/scratch/groups/gh/spack-dev/opt/spack/linux-rocky9-neoverse_v2/gcc-12.3.0/nvhpc-24.9-ezrvqttnnvhlkixzfqu4vhyqdia2b4pp"
                ]
            ],
            "cc": "nvcc",
            "cxx": "nvc++",
            "ftn": "nvf90",
            "features": ["openmp", "mpi"],
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
                        "%(check_job_completion_time)s,"
                        "reframe %(version)s,"
                        "%(check_info)s,"
                        "%(check_modules)s,"
                        "%(check_result)s,"
                        "%(check_executable)s,"
                        "%(check_executable_opts)s,"
                        "%(check_system)s,"
                        "%(check_environ)s,"
                        "%(check_partition)s,"
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
    "general": [
        {
            "check_search_path": ["checks/"], 
            "check_search_recursive": True,
            "use_login_shell": True,
            "module_map_file": ""
        }
    ],
}
