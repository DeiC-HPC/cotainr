# cotainr

![CI](https://github.com/DeiC-HPC/cotainr/actions/workflows/CI_push.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/cotainr/badge/?version=latest)](https://cotainr.readthedocs.io/en/latest/?badge=latest)

cotainr - a user space [Apptainer](https://apptainer.org/)/[Singularity](https://sylabs.io/singularity/) container builder.

cotainr makes it easy to build Singularity/Apptainer containers for certain use cases.

```shell
$ cotainr build --base-image docker://ubuntu:22.04 --conda-env <YOUR_CONDA_ENV.yml>
```

## Installation

The recommended way to install cotainr is using pip:

```bash
pip install cotainr
```

Alternatively, you may also simply download, unpack, and run cotainr directly from the `bin/` directory, which is possible since cotainr has no external dependencies other than Python and Singularity/Apptainer.

If you are using EasyBuild for managing your software stack, you may use the `cotainr-easyconfig.eb` EasyConfig as a starting point for installing cotainr via EasyBuild.

## Documentation

The documentation is hosted on [Read the Docs](https://cotainr.readthedocs.io/en/latest/).

## Licensing Information

cotainr is licensed under the European Union Public License (EUPL) 1.2. See the [LICENSE file](https://github.com/DeiC-HPC/cotainr/blob/main/LICENSE) for details.

Your use of cotainr is subject to the terms of the applicable component licenses as listed below. By using cotainr, you agree to fully comply with the terms of these component licenses. If you do not accept these license terms, do not use cotainr.

|Component|License|URL|Cotainr use|
|---------|-------|---|-----------|
|Miniforge|BSD 3-clause|[Miniforge License](https://github.com/conda-forge/miniforge/blob/main/LICENSE)|Miniforge is used to bootstrap conda environments when running `cotainr build --conda-env...`
