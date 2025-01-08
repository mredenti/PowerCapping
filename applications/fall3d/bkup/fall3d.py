import os
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher
import math

class fetch_fall3d(rfm.RunOnlyRegressionTest):  
    descr = 'Fetch FALL3D'
    
    maintainers = ['mredenti']
    
    # FALL3D version
    version = variable(str, value='9.0.1')
    
    executable = 'wget'
    tarball = f'fall3d-{version}.tar.gz'
    srcdir = tarball[:-7]
    executable_opts = [
                    f'https://gitlab.com/fall3d-suite/fall3d/-/archive/{version}/'
                    f'{tarball}'
                ]
    postrun_cmds= [f'tar xzf {tarball}']
    
    # Run fetch step on login node
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class build_fall3d(rfm.CompileOnlyRegressionTest):
    descr = 'Build FALL3D'
    
    build_system = 'CMake'
    fall3d_source = fixture(fetch_fall3d, scope='session')
    
    #purge_environment=True
    modules = ['netcdf-fortran']
    
    # precision
    
    @run_before('compile')
    def prepare_build(self):
        
        configuredir = os.path.join(self.fall3d_source.stagedir, self.fall3d_source.srcdir)
        installdir = os.path.join(self.stagedir, 'install')
        
        self.build_system.builddir = 'build'
        # remote reframe default compiler flags
        self.build_system.flags_from_environ = False
        # CMake configuration flags
        self.build_system.config_opts= [
            '-D CMAKE_Fortran_COMPILER=nvfortran',
            '-D DETAIL_BIN=NO',
            '-D WITH-MPI=YES',
            '-D WITH-ACC=YES', 
            '-D WITH-R4=NO', 
            f'-D CMAKE_INSTALL_PREFIX={installdir}',
            f'-S {configuredir}'
        ]
        # generator
        self.build_system.max_concurrency = 8
        # keep_files = ["cp2k.out"]


class fall3d_base_test(rfm.RunOnlyRegressionTest):
    '''Base class of Fall3d runtime tests'''
    
    fall3d_binaries = fixture(build_fall3d, scope='environment')
    kind = variable(str)
    benchmark = variable(str)
    
    valid_systems = ['*']
    valid_prog_environs = ['default'] # ['+mpi']

    execution_mode = variable(typ.Str[r'baremetal|container'])
    #platform = variable(typ.Str[r'baremetal|container'])
    #image = variable(str) # path to image - no default
    # maybe something about cpu and gpu
    
    num_tasks = None
    num_tasks_per_node = None
    exclusive_access = True
    
    @run_after('setup')
    def set_config(self): # find a better name
        accelerator = self.current_partition.devices
        self.num_tasks = self.num_gpus
        self.num_gpus_per_node =  self.num_gpus if self.num_gpus < accelerator[0].num_devices else accelerator[0].num_devices
        self.num_tasks_per_node = self.num_gpus_per_node
        # --nodes is set automatically as job.num_tasks // num_tasks_per_node
    
    @run_before('run')
    def set_extra_resources(self):
        self.extra_resources = {
            "gpu": {"num_gpus_per_node": f"{self.num_gpus_per_node}"},
        }
    
    @run_before('run')
    def load_modules(self):
        self.modules = self.fall3d_binaries.modules

    @run_before("run")
    def replace_launcher(self):
        self.job.launcher = getlauncher("mpirun")() # turn this into a custome launcher
        #self.job.launcher.modifier = "mpirun"
        #self.job.launcher.modifier_options = [
        #    "--map-by ppr:1:node:PE=72",
        #    "--report-bindings",
        #]
    
    @run_before('run')
    def prepare_run(self):
        self.executable = os.path.join(
            self.fall3d_binaries.stagedir,
            self.fall3d_binaries.build_system.builddir,
            'bin', 'Fall3d.x'
        )
        #The total number of processors is NPX × NPY × NPY × SIZE and should be equivalent to the argument np
        npx=npy=npz=1
        while npx*npy*npz != int(self.num_gpus):
            # Find which dimension is smallest and increment it
            if npx <= npy and npx <= npz:
                npx *= 2
            elif npy <= npz:
                npy *= 2
            else:
                npz *= 2
        
        self.executable_opts += [str(npx), str(npy), str(npz)]
        
        """_summary_

        Returns:
            _type_: _description_
        @run_before('run')
        def set_container_variables(self):
        if self.platform != 'native':
            self.container_platform = self.platform
            self.container_platform.command = (
            f'{nbody_exec} -benchmark -fp64 '
            f'-numbodies={self.num_bodies_per_gpu * self.gpu_count} ' 
            f'-numdevices={self.gpu_count}'
            )
            mount points https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.containers.ContainerPlatform.mount_points
            options = Additional options to be passed to the container runtime when executed.
            pull_image = False ? this should pull the image locally
            workdir¶
            The working directory of ReFrame inside the container.
            self.container_platform.with_mpi = True for Sarus but not singularity?
            with_cuda¶ Enable CUDA support when launching the container. I guess this will add the --nv flag
            self.container_platform.command = self.executable
            self.container_platform.image = 'nvcr.io/nvidia/pytorch:22.08-py3'
        """

    @sanity_function
    def validate_run(self):
        '''Check that a line indicating a successful run is present.'''
        return sn.assert_found(
            r'^<LOG>\s+The program has been run successfully\s*$', 
            self.stdout
        )

@rfm.simple_test
class fall3d_raikoke_test(fall3d_base_test):
    descr = 'Fall3d raikoke test'
    kind = 'mpi/openacc' # 'openacc', 'mpi'
    benchmark = 'osu_allreduce'
    #metric = 'bandwidth'
    sourcesdir = 'raikoke-2019/Input'
    readonly_files = [
        'Raikoke-2019.inp',
        'Raikoke-2019.sat.nc',
        'Raikoke-2019.gfs.nc',
        'GFS.tbl',
        'Sat.tbl'
        ]
    executable_opts = ['All', 'Raikoke-2019.inp']
    prerun_cmds = [
        # There is a typo in the name of the file
        '[ -f raikoke-2019.gfs.nc ] && mv raikoke-2019.gfs.nc Raikoke-2019.gfs.nc'
        ]    
     # maybe we can run a prerun hook which fetches the lfs
    keep_files = [
        'Raikoke-2019.SetSrc.log', 
        'Raikoke-2019.SetTgsd.log',
        'Raikoke-2019.SetDbs.log',
        'Raikoke-2019.Fall3d.log'
        ]
    
    num_gpus = 4
    time_limit = '1200'
    
    @sanity_function
    def validate_test(self):
        """
        If the run was successful, you should obtain a log file Example.Fall3d.log a successful end message
        https://fall3d-suite.gitlab.io/fall3d/chapters/example.html#checking-the-results
        """
        log_fname = 'Raikoke-2019.Fall3d.log'
        
        return sn.all([
            sn.assert_found(r'^  Number of warnings\s*:\s*0\s*$', log_fname),
            sn.assert_found(r'^  Number of errors\s*:\s*0\s*$', log_fname),
            sn.assert_found(r'^  Task FALL3D\s*:\s*ends NORMALLY\s*$', log_fname)
        ])

    
