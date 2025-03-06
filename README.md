# cotainr

![CI](https://github.com/DeiC-HPC/cotainr/actions/workflows/CI_push.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/cotainr/badge/?version=latest)](https://cotainr.readthedocs.io/en/latest/?badge=latest)

cotainr - a user space [Apptainer](https://apptainer.org/)/[Singularity](https://sylabs.io/singularity/) container builder.

cotainr makes it easy to build Singularity/Apptainer containers for certain use cases.

```shell
$ cotainr build --base-image docker://ubuntu:22.04 --conda-env <YOUR_CONDA_ENV.yml>
```

## Licensing Information

cotainr is licensed under the European Union Public License (EUPL) 1.2. See the [LICENSE file](https://github.com/DeiC-HPC/cotainr/blob/main/LICENSE) for details.

Your use of cotainr is subject to the terms of the applicable component licenses as listed below. By using cotainr, you agree to fully comply with the terms of these component licenses. If you do not accept these license terms, do not use cotainr.

|Component|License|URL|Cotainr use|
|---------|-------|---|-----------|
|Miniforge|BSD 3-clause|[Miniforge License](https://github.com/conda-forge/miniforge/blob/main/LICENSE)|Miniforge is used to bootstrap conda environments when running `cotainr build --conda-env...`

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
version = '2024.10.0'
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
    "base-image": "docker://rocm/dev-ubuntu-22.04:5.5.1-complete"
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
