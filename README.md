# cotainr

![CI](https://github.com/DeiC-HPC/cotainr/actions/workflows/CI_push.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/cotainr/badge/?version=latest)](https://cotainr.readthedocs.io/en/latest/?badge=latest)

cotainr - a user space [Apptainer](https://apptainer.org/)/[Singularity](https://sylabs.io/singularity/) container builder.

cotainr makes it easy to build Singularity/Apptainer containers for certain use cases.

```shell
$ cotainr build --base-image docker://ubuntu:22.04
```

## Documentation

Our documentation is hosted [here on Read the Docs](https://cotainr.readthedocs.io/en/latest/).

## Installation

cotainr has no external dependencies other than Python >= 3.8 and Singularity/Apptainer.
This means that a release can be unpacked and run directly from the `bin/` directory.

### Easybuild
If you are using easybuild, then here is an easyconfig, you can use:
```python
easyblock = 'Tarball'

name = 'cotainr'
version = '2022.12.0'
homepage = 'https://github.com/DeiC-HPC/container-builder'
description = 'cotainr is a tool that helps making Singularity/Apptainer containers.'

sources = [ {
  'filename': '%(name)s-%(version)s.tar.gz',
  'download_filename': '%(version)s.tar.gz',
  'source_urls':       ['https://github.com/DeiC-HPC/cotainr/archive/refs/tags'],
} ]

toolchain = SYSTEM

systems = """{
  "lumi-g": {
    "base-image": "docker://rocm/rocm-terminal:5.3"
  },
  "lumi-c": {
    "base-image": "docker://ubuntu:22.04"
  }
}"""

postinstallcmds = ['cd %(installdir)s/ ; cat >systems.json <<EOF\n' + systems + '\nEOF\n']

sanity_check_paths = {
    'files': ['bin/cotainr'],
    'dirs': ['cotainr'],
}

sanity_check_commands = ['cotainr']
```