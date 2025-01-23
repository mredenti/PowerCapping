import os
import reframe as rfm

# This fixture is responsible for staging the FALL3D input data, container,
# creating a unique workdir, and setting up symlinks.
@rfm.simple_test
class fall3d_stage(rfm.RunOnlyRegressionTest):
    valid_systems = ['thea:ggcompile']  # Adjust for your cluster
    valid_prog_environs = ['default']
    local = False  # Ensure this runs locally on the compute node

    executable = "true"
    # Base directory for FALL3D on the compute node
    FALL3D_BASEDIR = '$SCRATCH_FAST/FALL3D'

    def __init__(self):
        # Input data and container paths
        self.input_data_dir = f'{self.FALL3D_BASEDIR}/data'
        self.container_image = f'{self.FALL3D_BASEDIR}/fall3d.sif'

        # Placeholder for the workdir
        self.workdir = "blue"
        # No actual execution needed

    @run_after('setup')
    def prepare_workdir_and_symlinks(self):
        """Create a unique working directory and set up symlinks."""
        self.prerun_cmds = [
            'mkdir raikoke-large-gpu-2',
            'cd raikoke-large-gpu-2',
            'ln -s $SCRATCH_FAST/FALL3D/raikoke-2019/Input/Raikoke-2019.inp Raikoke-2019.inp', # perhaps a for loop over the input files 
            'ln -s $SCRATCH_FAST/FALL3D/raikoke-2019/Input/raikoke-2019.gfs.nc Raikoke-2019.gfs.nc',
            'ln -s $SCRATCH_FAST/FALL3D/raikoke-2019/Input/Raikoke-2019.sat.nc Raikoke-2019.sat.nc',
            'ln -s $SCRATCH_FAST/FALL3D/raikoke-2019/Input/Sat.tbl Sat.tbl',
            'ln -s $SCRATCH_FAST/FALL3D/raikoke-2019/Input/GFS.tbl GFS.tbl',
            # Create symlinks in the workdir
            f'{os.path.join(self.workdir, "data")}'
        ]
        # Create a unique working directory for this session
        self.workdir = os.path.join(self.FALL3D_BASEDIR, f'workdir_{self.current_partition.name}')

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


# The actual simulation test that depends on the staged environment.
@rfm.simple_test
class fall3d_base_test(rfm.RunOnlyRegressionTest):
    '''Base class of Fall3d runtime tests'''
    
    valid_systems = ['thea:gh']  # Adjust for your cluster
    valid_prog_environs = ['default']
    
    # SIF image
    image = variable(str) 
    #container_platform = 'Singularity'

    # Fixture to stage the input data and container
    # could also consider an explicit dependency so that i create the files and then just run...?
    stage_files = fixture(fall3d_stage, scope='session')
    
    exclusive_access = True

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
        
        self.container_platform.image = self.image
        # adds --nv flag to singularity exec
        self.container_platform.with_cuda = True 
        # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.containers.ContainerPlatform.mount_points
        
        # MAYBE THERE IS A WAY TO EXTRACT DIRECTLY THE PATH SYMLINKED
        input_dir = os.path.join(os.path.dirname(__file__), "green") # handle symlinks of read only input files
        self.container_platform.mount_points = [
            (input_dir, input_dir) 
        ]
        # Additional options to be passed to the container runtime when executed
        # self.container_platform.options = ['--no-home'] only for leo
        # command issued by singularity exec
        self.container_platform.command = f"Fall3d.x {' '.join(map(str, self.executable_opts))}"
        # workdir: The working directory of ReFrame inside the container. Default is rfm_workdir

    @run_after('setup')
    def set_executable_opts(self):
        """Configure options for the containerized simulation."""
        # Use the workdir and symlinks prepared by the fixture
        workdir = self.stage_files.workdir
        self.executable_opts = [
            'exec',
            os.path.join(workdir, 'fall3d.sif'),       # Container image
            './fall3d_simulation',                    # Simulation executable
            '-i', os.path.join(workdir, 'data', 'data.inp')  # Input file
        ]

    num_gpus= 2
    # post run , cleanup commands: rsync files to home stage directory!!