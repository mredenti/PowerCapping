import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.typecheck as typ
import reframe.utility.udeps as udeps


@rfm.simple_test
class fetch_fall3d(rfm.RunOnlyRegressionTest):    
    descr = 'Fetch FALL3D'
    
    maintainers = ['mredenti']
    
    # Reframe variable that can be set to 'baremetal' or 'container'
    execution_mode = variable(typ.Str[r'baremetal|container']) 
    
    # FALL3D version
    version = variable(str, value='9.0.1')
    
    executable = 'wget'
    executable_opts = [
                    f'https://gitlab.com/fall3d-suite/fall3d/-/archive/{version}/'
                    f'fall3d-{version}.tar.gz'
                ]
    
    # Run fetch step on login node
    local = True
    valid_systems = ['*']
    valid_prog_environs = ['default']
    
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class build_fall3d(rfm.CompileOnlyRegressionTest):
    descr = 'Build FALL3D'
    
    build_system = 'CMake'
    build_prefix = variable(str)
    
    valid_systems = ['*']
    valid_prog_environs = ['*']
    
    # Reframe variable that can be set to 'baremetal' or 'container'
    execution_mode = variable(typ.Str[r'baremetal|container']) # TEMPORARY
    
    @run_after('init')
    def add_dependencies(self):
        self.depends_on('fetch_fall3d', udeps.by_part)

    @require_deps
    def prepare_build(self, fetch_fall3d):
        target = fetch_fall3d(part='login', environ='default')
        tarball = f'fall3d-{target.version}.tar.gz'
        self.build_prefix = tarball[:-7]  # remove .tar.gz extension

        fullpath = os.path.join(target.stagedir, tarball)
        self.prebuild_cmds = [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]
        self.build_system.max_concurrency = 4

""" 
    @run_before('run')
    def pick_mode(self):
        '''Dynamically switch between baremetal or HPC Container Maker depending
        on the execution_mode variable.'''
        
        # Define dictionary with mode specific configurations
        mode_data = {
            'baremetal': {
                'descr': f'Fetch FALL3D {self.version} via wget',
                'executable': 'wget',
                'executable_opts': [
                    f'https://gitlab.com/fall3d-suite/fall3d/-/archive/{self.version}/'
                    f'fall3d-{self.version}.tar.gz'
                ]
            },
            'container': {
                'descr': f'Build HPC container file for FALL3D {self.version}',
                'executable': 'hpccm',
                'executable_opts': [
                    # Example HPC Container Maker + Docker workflow
                    f'--recipe fall3d_recipe.py --format docker > Dockerfile && '
                    # --cpu-target
                    # pass other options to hpccm recipe
                    #--working-directory WORKING_DIRECTORY, --wd WORKING_DIRECTORY
                    # set container working directory
                    #f'docker build -t fall3d:{self.version} .'
                ]
            }
        }
        
        # Pick the appropriate dictionary entry based on execution_mode
        config = mode_data.get(self.execution_mode)
        if not config:
            # Handle invalid values
            raise ValueError(f'Unknown execution_mode: {self.execution_mode}')

        # Dynamically set attributes for this test
        self.descr = config['descr']
        self.executable = config['executable']
        self.executable_opts = config['executable_opts']


class osu_base_test(rfm.RunOnlyRegressionTest):
    '''Base class of OSU benchmarks runtime tests'''

    valid_systems = ['pseudo-cluster:compute']
    valid_prog_environs = ['gnu-mpi']
    num_tasks = 2
    num_tasks_per_node = 1
    kind = variable(str)
    benchmark = variable(str)
    metric = variable(typ.Str[r'latency|bandwidth'])

    @run_after('init')
    def add_dependencies(self):
        self.depends_on('build_osu_benchmarks', udeps.by_env)

    @require_deps
    def prepare_run(self, build_osu_benchmarks):
        osu_binaries = build_osu_benchmarks()
        self.executable = os.path.join(
            osu_binaries.stagedir, osu_binaries.build_prefix,
            'c', 'mpi', self.kind, self.benchmark
        )
        self.executable_opts = ['-x', '100', '-i', '1000']

    @sanity_function
    def validate_test(self):
        return sn.assert_found(r'^8', self.stdout)

    def _extract_metric(self, size):
        return sn.extractsingle(rf'^{size}\s+(\S+)', self.stdout, 1, float)

    @run_before('performance')
    def set_perf_vars(self):
        make_perf = sn.make_performance_function
        if self.metric == 'latency':
            self.perf_variables = {
                'latency': make_perf(self._extract_metric(8), 'us')
            }
        else:
            self.perf_variables = {
                'bandwidth': make_perf(self._extract_metric(1048576), 'MB/s')
            }


@rfm.simple_test
class osu_latency_test(osu_base_test):
    descr = 'OSU latency test'
    kind = 'pt2pt/standard'
    benchmark = 'osu_latency'
    metric = 'latency'
    executable_opts = ['-x', '3', '-i', '10']


@rfm.simple_test
class osu_bandwidth_test(osu_base_test):
    descr = 'OSU bandwidth test'
    kind = 'pt2pt/standard'
    benchmark = 'osu_bw'
    metric = 'bandwidth'
    executable_opts = ['-x', '3', '-i', '10']


@rfm.simple_test
class osu_allreduce_test(osu_base_test):
    descr = 'OSU Allreduce test'
    kind = 'collective/blocking'
    benchmark = 'osu_allreduce'
    metric = 'bandwidth'
    executable_opts = ['-m', '8', '-x', '3', '-i', '10']


import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class ContainerFALL3DTest(rfm.RunOnlyRegressionTest):
    container_platform = 'Singularity'  # Tells ReFrame to look up the config
    valid_systems = ['thea:gh', 'thea:gg'] 
    valid_prog_environs = ['*']
    
    @rfm.run_before('run')
    def set_container_opts(self):
        # Suppose we have already pre-staged a .sif image on scratch
        self.container_platform.image = '/global/scratch/groups/gh/sif_images/pytorch-23.12-py3.sif'
        # Possibly pass any runtime options: e.g. --nv
        self.container_platform.options = ['--nv']
        # Then define the "command" inside the container
        self.container_platform.command = (
            'python3 my_benchmark_script.py --arg1=foo'
        )

    @sanity_function
    def check_run(self):
        return sn.assert_eq(self.job.exitcode, 0)
"""