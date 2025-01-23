import os
import reframe as rfm

# This fixture is responsible for staging the FALL3D input data, container,
# creating a unique workdir, and setting up symlinks.
@rfm.simple_test
class fall3d_stage(rfm.RunOnlyRegressionTest):
    valid_systems = ['thea:ggcompile']  # Adjust for your cluster
    valid_prog_environs = ['default']
    local = False  # Ensure this runs locally on the compute node

    # Base directory for FALL3D on the compute node
    FALL3D_BASEDIR = '$SCRATCH_FAST/FALL3D'

    def __init__(self):
        # Input data and container paths
        self.input_data_dir = f'{self.FALL3D_BASEDIR}/data'
        self.container_image = f'{self.FALL3D_BASEDIR}/fall3d.sif'

        # Placeholder for the workdir
        self.workdir = None

        # No actual execution needed
        self.executable = ''

    @run_after('setup')
    def prepare_workdir_and_symlinks(self):
        """Create a unique working directory and set up symlinks."""
        self.prerun_cmds = [
            'os.makedirs(self.workdir, exist_ok=True)',

            # Create symlinks in the workdir
            'os.symlink(self.input_data_dir, os.path.join(self.workdir, "data"))',
            'os.symlink(self.container_image, os.path.join(self.workdir, "fall3d.sif"))'
            
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
    valid_systems = ['*']  # Adjust for your cluster
    valid_prog_environs = ['*']
    container_platform = 'Singularity'

    # Fixture to stage the input data and container
    stage_files = fixture(fall3d_stage, scope='session')

    def __init__(self):
        # Number of tasks for the simulation
        self.num_tasks = 1
        self.num_tasks_per_node = 1

        # Container execution
        self.executable = 'singularity'

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
