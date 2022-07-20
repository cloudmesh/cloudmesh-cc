Documentation
=============

## Install

OSX

We use fastapi as teh webserver with uvicorn.  To install it, the newest versions of FastAPI are partially implemented in rust.
Thus you will need to install rust on your machine with 

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

After it is installe, please use 

```bash
mkdir cm
cd cm
pip install cloudmesh-installer
cloudmesh-installer get cc
```

