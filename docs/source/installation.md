# Installation

Installation is relatively simple. We leverage the cloudmesh-installer
to locally install the cloudmesh suite of repositories.

```bash
mkdir ~/cm
cd ~/cm
pip install cloudmesh-installer -U
cloudmesh-installer get cc
```

## Windows

Git Bash and Graphviz must be installed. The user can use Chocolatey run as
an administrator for convenience:

```bash
choco install git.install --params "/GitAndUnixToolsOnPath \
        /Editor:Nano /PseudoConsoleSupport /NoAutoCrlf" -y
choco install graphviz -y
```

## macOS

Graphviz must be installed. The user can use Homebrew for convenience:

```zsh
brew install graphviz
```

## Linux

Graphviz must be installed. The user can use apt for convenience:

```bash
sudo apt install graphviz -y
```