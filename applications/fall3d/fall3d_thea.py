import os
import reframe as rfm
import reframe.utility.udeps as udeps
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher

    #@run_after('setup')
     #def check_files_exist(self):
     #   """Ensure input data and container exist."""
     #   if not os.path.exists(self.input_data_dir):
     #       raise FileNotFoundError(f"Input data directory {self.input_data_dir} not found")
     #   if not os.path.isfile(self.container_image):
     #       raise FileNotFoundError(f"Container image {self.container_image} not found")


# =================================================================
# Fall3d Base Test Class: 
#   The actual simulation test that creates the staged environment.
# =================================================================
class fall3d_base_test(rfm.RunOnlyRegressionTest):
    '''Base class of Fall3d runtime tests'''
    
    descr = 'Create stage files'
    
    maintainers = ['mredenti'] 
    
    valid_systems = ['thea:gh']  # Adjust for your cluster
    valid_prog_environs = ['default']
    
    # add some description
    base_dir = os.path.join("$SCRATCH_FAST", "FALL3D")
    
    exclusive_access = True
    
    workdir = None
            
    @run_after('setup')
    def prepare_workdir_and_symlinks(self):
        """
        Staging the FALL3D input data, creating a unique workdir and setting up symlinks.
        """
        
        self.workdir = os.path.join(self.base_dir, f"{self.test_prefix}-gpus{self.num_gpus}-{self.launcher}")
        
        self.prerun_cmds = [
            f'mkdir -p {self.workdir} && cd {self.workdir}', # eventually we could use a timestamp
        ] + [
            # Append symlink commands with error checking (-f) - see -r for relative
            f'ln -s {os.path.join(self.base_dir, self.data_dir, file)} {file}' for file in self.read_only_files
        ] + self.prerun_cmds + ['']
        
    @run_after('setup')
    def copy_log_files(self):
        """
        Staging the FALL3D input data, creating a unique workdir and setting up symlinks.
        """
        
        self.workdir = os.path.join(self.base_dir, f"{self.test_prefix}-gpus{self.num_gpus}-{self.launcher}")
        
        self.postrun_cmds = [
            # Append symlink commands with error checking (-f) - see -r for relative
            f'\nrsync -auvx --progress {os.path.join(self.workdir, file)} {self.stagedir}' for file in self.log_files
        ] 
        
    @run_after('setup')
    def set_resources(self): # find a better name
        accelerator = self.current_partition.devices
        self.num_tasks = self.num_gpus
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = self.current_partition.processor.num_cpus

    @run_before("run")
    def replace_launcher(self):
        launcher_cls = getlauncher(self.launcher) 
        self.job.launcher = launcher_cls()
    
    @run_after('setup')
    def prepare_run(self):
        #The total number of processors is NPX × NPY × NPY × SIZE and should be equivalent to the argument np
        npx=npy=npz=1
        while npx*npy*npz != self.num_gpus:
            # Find which dimension is smallest and increment it
            if npx <= npy:
                npx *= 2
            else:
                npy *= 2
        
        self.executable_opts += [str(npx), str(npy), str(npz)]
        
        self.container_platform.image = os.path.join(self.base_dir, self.image)
        # adds --nv flag to singularity exec
        self.container_platform.with_cuda = True 
        # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.containers.ContainerPlatform.mount_points
        
        # handle symlinks of read only input files 
        input_dir = os.path.join(self.base_dir, self.data_dir) 
        self.container_platform.mount_points = [
            (input_dir, input_dir),
            (self.workdir, '/workdir') 
        ]
        self.container_platform.workdir = os.path.join("/workdir")
        self.container_platform.command = f"Fall3d.x {' '.join(map(str, self.executable_opts))}"

    # before sanity step, rsync log files back to home stage directory
    
    @sanity_function
    def assert_simulation_success(self):
        log_prefix = self.test_prefix  # Using the class attribute
        # Generate log file names dynamically.
        log_setsrc  = f'{log_prefix}.SetSrc.log'
        log_settgsd = f'{log_prefix}.SetTgsd.log'
        log_setdbs  = f'{log_prefix}.SetDbs.log'
        log_fall3d  = f'{log_prefix}.Fall3d.log'

        conditions = [
            sn.assert_found(r'^.*Task\s+SetTgsd\s*:\s*ends NORMALLY\s*$', log_settgsd),
            sn.assert_found(r'^.*Task\s+SetDbs\s*:\s*ends NORMALLY\s*$', log_setdbs),
            sn.assert_found(r'^.*Task\s+SetSrc\s*:\s*ends NORMALLY\s*$', log_setsrc),
            sn.assert_found(r'^  Number of warnings\s*:\s*0\s*$', log_fall3d),
            sn.assert_found(r'^  Number of errors\s*:\s*0\s*$', log_fall3d),
            sn.assert_found(r'^.*Task\s+FALL3D\s*:\s*ends NORMALLY\s*$', log_fall3d),
            sn.assert_found(r'^<LOG>\s+The program has been run successfully\s*$', self.stdout),
            sn.assert_eq(self.job.exitcode, 0)
        ]
        return sn.all(conditions)

@rfm.simple_test
class fall3d_raikoke_test(fall3d_base_test):
    descr = 'Fall3d Raikoke-2019 test'
    data_dir = 'raikoke-2019/Input'
    test_prefix = 'Raikoke-2019'
    read_only_files = [
        f'{test_prefix}.inp',
        f'{test_prefix}.sat.nc',
        'raikoke-2019.gfs.nc',
        'GFS.tbl',
        'Sat.tbl'
    ]
    executable_opts = ['All', 'Raikoke-2019.inp']
    prerun_cmds = [
        # There is a typo in the name of the file. We use test_prefix to rename the file.
        f'[ -f raikoke-2019.gfs.nc ] && mv raikoke-2019.gfs.nc Raikoke-2019.gfs.nc'
    ]  
    log_files = [
        f'{test_prefix}.SetSrc.log', 
        f'{test_prefix}.SetTgsd.log',
        f'{test_prefix}.SetDbs.log',
        f'{test_prefix}.Fall3d.log'
    ]
    
    # SIF image
    image = variable(str, value="fall3d.sif") 
    launcher = "srun-pmix"
    num_gpus = 2
    time_limit = '600'
    
    
@rfm.simple_test
class fall3d_raikoke_large_test(fall3d_base_test):
    descr = 'Fall3d Raikoke-2019 large test'
    data_dir = 'raikoke-2019-large'
    test_prefix = 'Raikoke-2019'
    #sourcesdir = 'raikoke-2019-large'
    read_only_files = [
        f'{test_prefix}.inp',
        'Raikoke-2019.gfs.nc',
    ]
    executable_opts = ['All', 'Raikoke-2019.inp']
    log_files = [
        f'{test_prefix}.SetSrc.log', 
        f'{test_prefix}.SetTgsd.log',
        f'{test_prefix}.SetDbs.log',
        f'{test_prefix}.Fall3d.log'
    ]
    
    # SIF image
    image = variable(str, value="fall3d.sif") 
    launcher = "srun-pmix"
    num_gpus = parameter([4, 8])
    time_limit = '1800'