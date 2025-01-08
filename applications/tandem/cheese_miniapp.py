import os
import re
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
import reframe.utility.osext as osext
from reframe.core.backends import getlauncher


class fetch_tandem(rfm.RunOnlyRegressionTest):

    descr = "Fetch TANDEM repository"

    repo_url = "https://github.com/TEAR-ERC/tandem.git"
    tag = variable(str, value="v1.1.0")  # baseline version

    executable = "git clone"
    executable_opts = [f"-b {tag}", "--recurse-submodules", f"{repo_url}"]

    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class build_xshells(rfm.CompileOnlyRegressionTest):
    descr = "Build xshells cheese2p-miniapp-fp32"

    build_system = "Make"
    build_prefix = variable(str)

    xshells_app = fixture(fetch_xshells, scope="session")

    modules = [
        "cmake/3.27.7",
        "gcc/12.2.0",
        "metis/5.1.0--gcc--12.2.0",
        "parmetis/4.0.3--openmpi--4.1.6--gcc--12.2.0",
        "petsc/3.20.1--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-mumps",  # petsc/3.20.1--openmpi--4.1.6--nvhpc--23.11-mumps
        "openmpi/4.1.6--gcc--12.2.0",
        "cuda/12.1",
    ]

    env_vars = {
        "LIBRARY_PATH": "$CUDA_HOME/lib64/:$LIBRARY_PATH",
        "CUDA_PATH": "$CUDA_HOME",
    }

    @run_before("compile")
    def prepare_build(self):

        fullpath = os.path.join(self.xshells_app.stagedir, "xshells")

        self.prebuild_cmds = [
            f"cd {fullpath}",
            f"echo -e 'nvidia\\n' | ./setup",
        ]

        self.build_system.cc = "mpicc"
        self.build_system.cxx = "mpicxx"
        self.build_system.ftn = "mpifort"
        self.build_system.srcdir = fullpath
        self.build_system.options = [
            "VERBOSE=1",
            "xsgpu_mpi",
        ]

        self.build_system.max_concurrency = 1


class xshells_base_benchmark(rfm.RunOnlyRegressionTest):
    """Base class of xshells miniapp runtime benchmarks"""

    valid_systems = ["leonardo:booster"]
    valid_prog_environs = ["default"]

    num_tasks = None
    num_nodes = variable(int)
    num_cpus_per_task = 8

    account_str = "cin_staff"
    qos = "normal"

    exclusive_access = True
    time_limit = "600"

    modules = [
        "gcc/12.2.0",
        "openmpi/4.1.6--gcc--12.2.0",
        "fftw/3.3.10--openmpi--4.1.6--gcc--12.2.0",
        "cuda",
    ]

    env_vars = {
        "LIBRARY_PATH": "$CUDA_HOME/lib64/:$LIBRARY_PATH",
        "CUDA_PATH": "$CUDA_HOME",
    }

    xshells_miniapp_binaries = fixture(build_xshells, scope="environment")

    @run_before("run")
    def setup_job_opts(self):
        self.num_nodes = max(int(self.num_gpus / 4), 1)
        self.num_gpus_per_node = int(self.num_gpus / self.num_nodes)
        self.num_tasks_per_node = self.num_gpus_per_node
        self.extra_resources = {
            "account": {"account": f"{self.account_str}"},
            "qos": {"qos": f"{self.qos}"},
            "gpu": {"num_gpus_per_node": f"{self.num_gpus_per_node}"},
            "nodes": {"nodes": f"{self.num_nodes}"},
        }

    @run_before("run")
    def set_dir(self):
        # Set the executable path using the stagedir and build prefix
        dir = os.path.join(
            self.xshells_miniapp_binaries.xshells_app.stagedir, "xshells"
        )
        self.prerun_cmds = [
            f"cd {dir}",
        ]

    @run_before("run")
    def replace_launcher(self):
        self.job.options = [
            opt for opt in self.job.options if not opt.startswith("--ntasks")
        ]
        self.job.launcher = getlauncher("local")()
        self.job.launcher.modifier = "mpirun"
        self.job.launcher.modifier_options = [
            f"-n {self.num_gpus}",
            f"--map-by socket:PE={self.num_cpus_per_task}",
            "--rank-by core",
            "--report-bindings",
            "bash -c 'export CUDA_VISIBLE_DEVICES=$((OMPI_COMM_WORLD_LOCAL_RANK % 4)); exec",
        ]

    @sanity_function
    def validate_test(self):
        return sn.assert_eq(self.job.exitcode, 0)

    @performance_function("s")
    def avg_time_per_eval(self):
        return sn.extractsingle(
            r"> average time per eval = (\S+)", self.stdout, 1, float
        )

    @performance_function("s")
    def std_avg_time_per_eval(self):
        return sn.extractsingle(
            r">\s*average time per eval = [\d.]+ \(\+/- ([\d.eE+-]+)\)",
            self.stdout,
            1,
            float,
        )


# can have small, medium, large test case


@rfm.simple_test
class xshells_medium_benchmark(xshells_base_benchmark):
    descr = "XSHELLS - MEDIUM TEST CASE "
    kind = "gpu"
    num_gpus = parameter([1, 2, 4, 8, 16, 32, 64])  # 16, 32, 64
    executable = "./xsgpu_mpi"
    executable_opts = ["xshells.par.medium'"]
    benchmark = "medium"
