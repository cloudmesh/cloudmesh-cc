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

# from cloudmesh.common.Shell import Shell
from cloudmesh.cc.Shell import Shell_path
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import path_expand
from pathlib import Path

import time

class TestShell:

    def test_fake_browser(self):
        browser = Shell_path.fake_browser
        HEADING()
        Benchmark.Start()
        # Shell.copy("test-graphviz.svg", '/tmp/test-graphviz.svg')
        # Shell.copy("test-graphviz.svg", "~/test-graphviz.svg")
        # r = Shell.browser("~/test-graphviz.svg")
        # Shell.copy("test-graphviz.svg", f"{Path.home()}/test-graphviz.svg")
        r = browser('http://google.com')
        print(r)
        # r = browser(f'https://google.com')
        # r = browser(
        #     f"C:/Users/abeck/cm/cloudmesh-cc/test-graphviz.svg")
        # r = browser(
        #     f"file:///C:/Users/abeck/cm/cloudmesh-cc/test-graphviz.svg")
        # r = browser(f"~/test-graphviz.svg")
        # r = browser(f'test-graphviz.svg')
        # r = browser(f'./test-graphviz.svg')
        # assert r == path_expand(f'~/test-graphviz.svg')
        # input()
        # r = Shell.browser("file://~/test-graphviz.svg")
        # r = Shell.browser("test-graphviz.svg")
        # r = Shell.browser("file://test-graphviz.svg")
        # r = Shell.browser("file://tmp/test-graphviz.svg")
        # r = Shell.browser("http://google.com")
        # r = Shell.browser("https://google.com")
        print(r)
        Benchmark.Stop()

class Rest:
    def test_shell_head(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell_path.head(file)
        Benchmark.Stop()
        assert 'docker-compose' not in r
        assert 'cloudmesh-sys' in r
        assert '#' in r
        assert 'starlette' not in r

    def test_shell_cat(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell_path.cat(file)
        Benchmark.Stop()
        assert 'starlette' in r
        assert 'cloudmesh-sys' in r
        assert 'docker-compose' in r
        assert '#' in r

    def test_shell_ping(self):
        HEADING()
        Benchmark.Start()
        host = 'www.google.com'
        r = Shell.ping(host)
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
        r = Shell.fgrep(file, 'docker-compose')
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

    def test_map_filename(self):
        HEADING()
        Benchmark.Start()
        user = os.path.basename(os.environ["HOME"])

        result = Shell.map_filename(name='wsl:~/cm/')
        assert result.user == user
        assert result.host == 'wsl'
        assert result.path == f'/mnt/c/Users/{user}/cm'

        result = Shell.map_filename(name='wsl:/mnt/c/home/')
        assert result.user == user
        assert result.host == 'wsl'
        assert result.path == f'/mnt/c/Users/{user}/cm'

        result = Shell.map_filename(name='C:~/cm')
        assert result.user == user
        assert result.host == 'localhost'
        assert result.path == f'C:\\Users\\{user}\\cm'

        result = Shell.map_filename(name='scp:user@host:~/cm')
        assert result.user == "user"
        assert result.host == 'host'
        assert result.path == f'~/cm'

        result = Shell.map_filename(name='scp:user@host:/tmp')
        assert result.user == "user"
        assert result.host == 'host'
        assert result.path == f'/tmp'

        result = Shell.map_filename(name='~/cm')
        assert result.user == user
        assert result.host == 'localhost'
        assert result.path == path_expand('~/cm')

        result = Shell.map_filename(name='/tmp')
        assert result.user == user
        assert result.host == 'localhost'
        assert result.path == '/tmp'

        result = Shell.map_filename(name='./cm')
        assert result.user == user
        assert result.host == 'localhost'
        assert result.path == path_expand('./cm')


        Benchmark.Stop()

class Rest:
    def test_shell_browser(self):
        HEADING()
        Benchmark.Start()
        # Shell.copy("test-graphviz.svg", '/tmp/test-graphviz.svg')
        # Shell.copy("test-graphviz.svg", "~/test-graphviz.svg")
        # r = Shell.browser("~/test-graphviz.svg")
        #Shell.copy("test-graphviz.svg", f"{Path.home()}/test-graphviz.svg")
        r = Shell.browser(f'http://google.com')
        print('testing unsecured')
        time.sleep(3)
        r = Shell.browser(f'https://google.com')
        print('testing secured')
        time.sleep(3)
        r = Shell.browser(f"C:/Users/abeck/cm/cloudmesh-cc/test-graphviz.svg")
        print('i just tried a fullpath')
        time.sleep(3)
        r = Shell.browser(f"file:///C:/Users/abeck/cm/cloudmesh-cc/test-graphviz.svg")
        print('i just tried with file:')
        time.sleep(3)
        r = Shell.browser(f"~/test-graphviz.svg")
        print('i just opened the home dir and the svg in there')
        time.sleep(5)
        r = Shell.browser(f'test-graphviz.svg')
        print('i just tried no slashes')
        time.sleep(5)
        r = Shell.browser(f'./test-graphviz.svg')
        print('i just tried something wacky')
        time.sleep(5)
        # assert r == path_expand(f'~/test-graphviz.svg')
        # input()
        # r = Shell.browser("file://~/test-graphviz.svg")
        # r = Shell.browser("test-graphviz.svg")
        # r = Shell.browser("file://test-graphviz.svg")
        # r = Shell.browser("file://tmp/test-graphviz.svg")
        # r = Shell.browser("http://google.com")
        # r = Shell.browser("https://google.com")
        print(r)
        Benchmark.Stop()


    def test_shell_copy(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.copy(file, f'{Path.cwd()}/shell-directory')
        Benchmark.Stop()
        assert os.path.exists(path_expand(f'shell-directory/{file}'))

    # def test_shell_sync(self):
    #     HEADING()
    #     Benchmark.Start()
    #     file = path_expand('requirements.txt')
    #     r = Shell.rsync(file)
    #     Benchmark.Stop()


