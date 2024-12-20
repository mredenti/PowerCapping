import reframe.utility.sanity as sn
import reframe as rfm

@rfm.simple_test
class HelloTest(rfm.RegressionTest):
    
    lang=parameter(['cpp'])
    time_limit="120"
    
    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.sourcepath = f'hello.{self.lang}'
        self.sanity_patterns = sn.assert_found(r'Hello, World\!', self.stdout)
        self.tags = {'functionality','short'}
