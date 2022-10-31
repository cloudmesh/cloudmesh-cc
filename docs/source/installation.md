# Installation

Installation is relatively simple.

## OS-Specific Requirements

After completing the steps for your operating system, 
continue on to the `All Platforms` section.

### Windows

The user should use [Chocolatey](https://chocolatey.org/install) run as
an administrator to install Git Bash and Graphviz. We also install Visual 
C++ Build Tools as a prerequisite for necessary Python modules.

```bash
choco install git.install --params "/GitAndUnixToolsOnPath \
        /Editor:Nano /PseudoConsoleSupport /NoAutoCrlf" -y
choco install graphviz visualstudio2019buildtools \
        visualstudio2019-workload-vctools -y
```

Please also follow <https://github.com/cybertraining-dsc/reu2022/blob/main/project/git-bash-pseudo-console.md#using-git-bash-on-windows>
for proper configuration of Git Bash.

### macOS

Graphviz must be installed. The user should use 
[Homebrew](https://brew.sh/) for convenience:

```zsh
brew install graphviz
```

### Linux

Graphviz must be installed. The user should use apt:

```bash
sudo apt install graphviz -y
```

## All Platforms

We leverage the cloudmesh-installer
to locally install the cloudmesh suite of repositories. Please use
a virtual Python environment.

```bash
mkdir ~/cm
cd ~/cm
pip install cloudmesh-installer -U
cloudmesh-installer get cc
cd cloudmesh-cc
pip install -e .
```