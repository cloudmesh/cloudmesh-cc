# ##############################################################
# pytest -v --capture=no tests/test_shell.py
# pytest -v  tests/test_shell.py
# pytest -v --capture=no  tests/shell.py::Test_Shell::<METHODNAME>
# ##############################################################


"""
This is the test for the new shell commands that we are implementing
for the purpose of making the workflow more easily synonymous with each of the
OS we have on the team.
"""
import os.path

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import path_expand
from pathlib import Path

class TestShell:

    def test_shell_head(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.head(filename=file)
        Benchmark.Stop()
        assert 'docker-compose' not in r
        assert 'cloudmesh-sys' in r
        assert '#' in r
        assert 'starlette' not in r

    def test_shell_cat(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.cat(filename=file)
        Benchmark.Stop()
        assert 'starlette' in r
        assert 'cloudmesh-sys' in r
        assert 'docker-compose' in r
        assert '#' in r

    def test_shell_ping(self):
        HEADING()
        Benchmark.Start()
        host = 'www.google.com'
        r = Shell.ping(host=host)
        Benchmark.Stop()
        assert 'packets' in r
        assert 'www.google.com' in r
        assert 'time=' in r

    def test_shell_rm(self):
        HEADING()
        Benchmark.Start()
        r = Shell.rm('psuedo-directory')
        Benchmark.Stop()
        assert not os.path.exists(path_expand('psuedo-directory'))

    def test_shell_tail(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.tail(filename=file)
        Benchmark.Stop()
        assert 'pexpect' in r
        assert 'ujson' in r

    def test_shell_dialog(self):
        """
        This method may be one of the more interactive (visual) methods for testing
        :return:
        """
        HEADING()
        Benchmark.Start()
        r = Shell.dialog()
        Benchmark.Stop()
        assert True # unless visually the dialog does not work appropriately

    def test_shell_fgrep(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.fgrep(filename=file, s='docker-compose')
        Benchmark.Stop()
        assert 'docker-compose' in r

    def test_shell_grep(self):
        HEADING()
        Benchmark.Start()

        Benchmark.Stop()

    def test_shell_which(self):
        HEADING()
        Benchmark.Start()

        Benchmark.Stop()

    def test_shell_mkdir(self):
        HEADING()
        Benchmark.Start()
        r = Shell.mkdir('shell-directory')
        print(r)
        Benchmark.Stop()
        assert os.path.exists(path_expand('shell-directory'))

    def test_shell_browser(self):
        HEADING()
        Benchmark.Start()
        r = Shell.browser("requirements.txt")
        Benchmark.Stop()

    def test_shell_copy(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.copy(file, f'{Path.cwd()}', f'{Path.cwd()}/shell-directory')
        Benchmark.Stop()

    def test_shell_sync(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.rsync(file)
        print(r)
        Benchmark.Stop()


