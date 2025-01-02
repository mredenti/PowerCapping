# Copyright 2016-2024 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn


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
        self.build_system.flags_from_environ = False
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
    valid_prog_environs = ['*'] # ['+mpi']

    #metric = variable(typ.Str[r'latency|bandwidth'])
    #execution_mode = variable(typ.Str[r'baremetal|container'])
    # maybe something about cpu and gpu
    
    num_tasks = 1
    num_tasks_per_node = 1
    exclusive_access = True
    
    @run_before('run')
    def set_extra_resources(self):
        self.extra_resources = {
            "gpu": {"num_gpus_per_node": f"{self.num_gpus_per_node}"},
        }
    
    @run_before('run')
    def load_modules(self):
        self.modules = self.fall3d_binaries.modules

    @run_before('run')
    def prepare_run(self):
        self.executable = os.path.join(
            self.fall3d_binaries.stagedir,
            self.fall3d_binaries.build_system.builddir,
            'bin', 'Fall3d.x'
        )
        #self.executable_opts += ['NPX']

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
        'Sat.tbl']
    executable_opts = ['All', 'Raikoke-2019.inp']
    num_gpus_per_node = 1
    prerun_cmds = [
        # There is a typo in the name of the file
        '[ -f raikoke-2019.gfs.nc ] && mv raikoke-2019.gfs.nc Raikoke-2019.gfs.nc'
        ]    
    # maybe we can run a prerun hook which fetches 
    keep_files = [
        'Raikoke-2019.SetSrc.log', 
        'Raikoke-2019.SetTgsd.log',
        'Raikoke-2019.SetDbs.log',
        'Raikoke-2019.Fall3d.log'
        ]
    
    @sanity_function
    def validate_test(self):
        """
        If the run was successful, you should obtain a log file Example.Fall3d.log a successful end message
        https://fall3d-suite.gitlab.io/fall3d/chapters/example.html#checking-the-results
        """
        log_fname = 'Input/Raikoke-2019.Fall3d.log'
        
        return sn.all([
            sn.assert_found(r'^  Number of warnings\s*:\s*0\s*$', log_fname),
            sn.assert_found(r'^  Number of errors\s*:\s*0\s*$', log_fname),
            sn.assert_found(r'^  Task FALL3D\s*:\s*ends NORMALLY\s*$', log_fname)
        ])

    
