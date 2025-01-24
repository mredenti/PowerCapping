import os
import reframe as rfm
import reframe.utility.udeps as udeps
from reframe.core.backends import getlauncher

@rfm.simple_test
class fall3d_stage(rfm.RunOnlyRegressionTest):
    """ 
    This fixture is responsible for staging the FALL3D input data, container,
    creating a unique workdir, and setting up symlinks.
    """
    descr = 'Create stage files'
    
    valid_systems = ['thea:ggcompile'] 
    valid_prog_environs = ['default']
    
    local = False 

    # No actual execution needed
    executable = "true"
    
    # di...
    base_dir = os.path.join("$SCRATCH_FAST", "FALL3D")

    @run_after('setup')
    def prepare_workdir_and_symlinks(self):
        """Create a unique working directory and set up symlinks."""
        self.prerun_cmds = [
            f'mkdir {os.path.join(self.base_dir)}',
            'cd raikoke-large-gpu-2',
            f'ln -s {self.base_dir}/raikoke-2019/Input/Raikoke-2019.inp Raikoke-2019.inp', # perhaps a for loop over the input files 
            f'ln -s {self.base_dir}/raikoke-2019/Input/raikoke-2019.gfs.nc Raikoke-2019.gfs.nc',
            f'ln -s {self.base_dir}/raikoke-2019/Input/Raikoke-2019.sat.nc Raikoke-2019.sat.nc',
            f'ln -s {self.base_dir}/raikoke-2019/Input/Sat.tbl Sat.tbl',
            f'ln -s {self.base_dir}/raikoke-2019/Input/GFS.tbl GFS.tbl',
            # Create symlinks in the workdir
            f'{os.path.join(self.base_dir, "data")}'
        ]
        # Create a unique working directory for this session
        self.base_dir = os.path.join(self.base_dir, f'workdir_{self.current_partition.name}')
        self.workdir = self.base_dir 
        
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)
    
    #@run_after('setup')
     #def check_files_exist(self):
     #   """Ensure input data and container exist."""
     #   if not os.path.exists(self.input_data_dir):
     #       raise FileNotFoundError(f"Input data directory {self.input_data_dir} not found")
     #   if not os.path.isfile(self.container_image):
     #       raise FileNotFoundError(f"Container image {self.container_image} not found")


# =================================================================
# Fall3d Base Test Class: 
#   The actual simulation test that depends on the staged environment.
# =================================================================
class fall3d_base_test(rfm.RunOnlyRegressionTest):
    '''Base class of Fall3d runtime tests'''
    
    valid_systems = ['thea:gh']  # Adjust for your cluster
    valid_prog_environs = ['default']
    
    #container_platform = 'Singularity'

    # Fixture to stage the input data and container
    # could also consider an explicit dependency so that i create the files and then just run...?
    #stage_files = fixture(fall3d_stage, scope='session')
    
    exclusive_access = True
    
    @run_after('init')
    def configure_dependencies(self):
        '''Conditionally add dependencies based on the programming environment.'''
        #if self.execution_mode == 'baremetal': PUT A CONDITION ON WHEN YOU WANT TO RUN WITHOUT THE STAGING OR NOT
        self.depends_on('fall3d_stage', udeps.fully)
            
    @require_deps
    def get_dependencies(self, build_fall3d):
        self.stage_files = fall3d_stage()
        
    @run_after('setup')
    def set_resources(self): # find a better name
        accelerator = self.current_partition.devices
        self.num_tasks = self.num_gpus
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = self.current_partition.processor.num_cpus

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
        
        self.container_platform.image = os.path.join(self.stage_files.base_dir, self.image)
        # adds --nv flag to singularity exec
        self.container_platform.with_cuda = True 
        # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.containers.ContainerPlatform.mount_points
        
        # MAYBE THERE IS A WAY TO EXTRACT DIRECTLY THE PATH SYMLINKED
        input_dir = os.path.join(self.stage_files.base_dir, self.data_dir) # handle symlinks of read only input files
        self.container_platform.mount_points = [
            (input_dir, input_dir),
            (self.data_dir, self.data_dir) 
        ]
        self.container_platform.workdir = self.data_dir
        
        # Additional options to be passed to the container runtime when executed
        # self.container_platform.options = ['--no-home'] only for leo
        # command issued by singularity exec
        self.container_platform.command = f"Fall3d.x {' '.join(map(str, self.executable_opts))}"
        # workdir: The working directory of ReFrame inside the container. Default is rfm_workdir

    @run_before("run")
    def replace_launcher(self):
        launcher_cls = getlauncher("srun-pmix") 
        self.job.launcher = launcher_cls()

@rfm.simple_test
class fall3d_raikoke_test(fall3d_base_test):
    descr = 'Fall3d Raikoke-2019 test'
    # This should also match Fall3d's tasks log prefix
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
    # maybe we can run a prerun hook which fetches the lfs
    # show define an test case name variable and make keep files the default in the base
    keep_files_2 = [
        f'{test_prefix}.SetSrc.log', 
        f'{test_prefix}.SetTgsd.log',
        f'{test_prefix}.SetDbs.log',
        f'{test_prefix}.Fall3d.log'
    ]
    
    # SIF image
    image = variable(str, value="fall3d.sif") 
    num_gpus = 2
    time_limit = '600'
    # post run , cleanup commands: rsync files to home stage directory!!