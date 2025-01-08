import os
import re
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
import reframe.utility.osext as osext
from reframe.core.backends import getlauncher


class fetch_specfemd3d_miniapps(rfm.RunOnlyRegressionTest):

    descr = "Fetch SPECFEM3D mini-apps repository"

    repo_url = "https://gitlab.com/specfem_cheese_2p/mini_specfem/specfem_mini_app.git"
    commit_hash = variable(
        str, value="39cb869b8547e19edba1a8ff693a7028bc8a29cd"
    )  # version = variable(str, value='7.3')

    executable = "git clone"
    executable_opts = [f"{repo_url}"]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class build_specfem3d_miniapps(rfm.CompileOnlyRegressionTest):
    descr = "Build Specfem3d mini-app"

    build_system = "Make"
    build_prefix = variable(str)
    # build_locally = False # check first whether you can pass it from the command line
    num_gpus = parameter([1])

    specfem3d_miniapps = fixture(fetch_specfemd3d_miniapps, scope="test")

    @run_before("compile")
    def prepare_build(self):
        # turn cuda into a parameter or variable

        self.build_prefix = "specfem_mini_app/elastic_iso_cuda_mpi"
        self.build_system.makefile = "Makefile_nvidia"
        fullpath = os.path.join(self.specfem3d_miniapps.stagedir, self.build_prefix)

        self.build_system.srcdir = fullpath
        self.build_system.options = [
            "VERBOSE=1",
            'LIBS="-lstdc++ -lcudart -L$NVHPC_HOME/Linux_aarch64/24.9/cuda/lib64"',
        ]
        self.build_system.max_concurrency = 1

        gpus = int(self.num_gpus)
        npx = int(gpus / int(gpus**0.5))
        npy = int(gpus**0.5)

        self.prebuild_cmds = [
            f"cd {fullpath}",
            f"sed -i 's/NPX_config *= *[0-9]\+/NPX_config = {npx}/g; s/NPY_config *= *[0-9]\+/NPY_config = {npy}/g' {os.path.join(fullpath, 'config_mod.f90')}",
        ]


class specfemd3d_base_benchmark(rfm.RunOnlyRegressionTest):
    """Base class of Specfem3d mini-aps runtime tests"""

    valid_systems = ["*"]
    valid_prog_environs = ["*"]
    
    exclusive_access = True
    time_limit = "600"

    specfemd3d_miniapps_binaries = fixture(
        build_specfem3d_miniapps, scope="environment"
    )
   
    # kind = variable(str)
    # benchmark = variable(str)
    # metric = variable(typ.Str[r'latency|bandwidth'])
    @run_before("run")
    def setup_job_opts(self):
        procinfo = self.current_partition.processor
        self.num_cpus_per_task = procinfo.num_cores
        self.num_nodes = self.specfemd3d_miniapps_binaries.num_gpus 
        self.num_gpus_per_node = int(self.specfemd3d_miniapps_binaries.num_gpus / self.num_nodes)
        self.num_tasks_per_node = self.num_gpus_per_node
        self.num_tasks = self.specfemd3d_miniapps_binaries.num_gpus
        self.extra_resources = {
            "nodes": {"nodes": f"{self.num_nodes}"},
        }

    @run_before("run")
    def set_executable_path(self):
        # Set the executable path using the stagedir and build prefix
        self.executable = os.path.join(
            self.specfemd3d_miniapps_binaries.specfem3d_miniapps.stagedir,
            self.specfemd3d_miniapps_binaries.build_prefix,
            "xspecfem_mini_app",
        )

    @run_before("run")
    def replace_launcher(self):
        self.job.options = [
            opt for opt in self.job.options if not opt.startswith("--ntasks")
        ]
        self.job.launcher = getlauncher("local")()
        self.job.launcher.modifier = "mpirun"
        self.job.launcher.modifier_options = [
            f"-np {self.specfemd3d_miniapps_binaries.num_gpus}",
            "--map-by ppr:1:node:PE=72",
            "--report-bindings",
        ]

    @sanity_function
    def validate_test(self):
        return sn.assert_eq(self.job.exitcode, 0)

    @performance_function("s")
    def end_time_iteration_loop(self):
        return sn.extractsingle(
            r"End of time iteration loop\.\.\.\s+(\S+)", self.stdout, 1, float
        )

    @performance_function("count")
    def time_step_count(self):
        return sn.extractsingle(r"time step\s*:\s*\d+\s*/\s*(\d+)", self.stdout, 1, int)


@rfm.simple_test
class specfemd3d_iso_benchmark(specfemd3d_base_benchmark):
    descr = "Elastic Iso [MPI + CUDA]"
    kind = "pt2pt/standard"
    benchmark = "osu_latency"
    metric = "latency"
    # executable_opts = ['-x', '3', '-i', '10']
