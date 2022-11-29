# My AI software environment on my laptop

```yaml
name: py39_pytorch_rocm
channels:
  - conda-forge
dependencies:
  - _libgcc_mutex=0.1=conda_forge
  - _openmp_mutex=4.5=2_gnu
  - brotlipy=0.7.0=py39hb9d737c_1005
  - bzip2=1.0.8=h7f98852_4
  - ca-certificates=2022.9.24=ha878542_0
  - certifi=2022.9.24=pyhd8ed1ab_0
  - cffi=1.15.1=py39he91dace_2
  - charset-normalizer=2.1.1=pyhd8ed1ab_0
  - cryptography=38.0.3=py39h3ccb8fc_0
  - freetype=2.12.1=hca18f0e_0
  - idna=3.4=pyhd8ed1ab_0
  - jpeg=9e=h166bdaf_2
  - lcms2=2.14=h6ed2654_0
  - ld_impl_linux-64=2.39=hcc3a1bd_1
  - lerc=4.0.0=h27087fc_0
  - libblas=3.9.0=16_linux64_openblas
  - libcblas=3.9.0=16_linux64_openblas
  - libdeflate=1.14=h166bdaf_0
  - libffi=3.4.2=h7f98852_5
  - libgcc-ng=12.2.0=h65d4601_19
  - libgfortran-ng=12.2.0=h69a702a_19
  - libgfortran5=12.2.0=h337968e_19
  - libgomp=12.2.0=h65d4601_19
  - liblapack=3.9.0=16_linux64_openblas
  - libnsl=2.0.0=h7f98852_0
  - libopenblas=0.3.21=pthreads_h78a6416_3
  - libpng=1.6.39=h753d276_0
  - libsqlite=3.40.0=h753d276_0
  - libstdcxx-ng=12.2.0=h46fd767_19
  - libtiff=4.4.0=h55922b4_4
  - libuuid=2.32.1=h7f98852_1000
  - libwebp-base=1.2.4=h166bdaf_0
  - libxcb=1.13=h7f98852_1004
  - libzlib=1.2.13=h166bdaf_4
  - ncurses=6.3=h27087fc_1
  - numpy=1.23.5=py39h3d75532_0
  - openjpeg=2.5.0=h7d73246_1
  - openssl=3.0.7=h166bdaf_0
  - pillow=9.2.0=py39hf3a2cdf_3
  - pip=22.3.1=pyhd8ed1ab_0
  - pthread-stubs=0.4=h36c2ea0_1001
  - pycparser=2.21=pyhd8ed1ab_0
  - pyopenssl=22.1.0=pyhd8ed1ab_0
  - pysocks=1.7.1=pyha2e5f31_6
  - python=3.9.14=hba424b6_0_cpython
  - python_abi=3.9=3_cp39
  - readline=8.1.2=h0f457ee_0
  - requests=2.28.1=pyhd8ed1ab_1
  - setuptools=65.5.1=pyhd8ed1ab_0
  - tk=8.6.12=h27826a3_0
  - typing-extensions=4.4.0=hd8ed1ab_0
  - typing_extensions=4.4.0=pyha770c72_0
  - tzdata=2022f=h191b570_0
  - urllib3=1.26.11=pyhd8ed1ab_0
  - wheel=0.38.4=pyhd8ed1ab_0
  - xorg-libxau=1.0.9=h7f98852_0
  - xorg-libxdmcp=1.1.3=h7f98852_0
  - xz=5.2.6=h166bdaf_0
  - zstd=1.5.2=h6239696_4
  - pip:
    - --extra-index-url https://download.pytorch.org/whl/rocm5.2
    - torch==1.13.0+rocm5.2
    - torchaudio==0.13.0+rocm5.2
    - torchvision==0.14.0+rocm5.2
```

<br />

# Moving to LUMI
I would like to transfer my Python Conda environment to LUMI. What to do?

`conda env create --file py39_pytorch_rocm.yml` on LUMI?

<br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />

## Official LUMI answer

0. DON'T ever do: `conda env create --file py39_pytorch_rocm.yml` - use a *container*!
1. You can't build containers on LUMI - get a local Linux machine
2. Compile/install Singularity on it
3. Figure out how to create an appropriate Singularity build recipe
4. Build your container locally
5. Copy your container to LUMI

<br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />


## The not so well known alternative which makes it possible to build the container on LUMI

```bash
$ singularity build --sandbox /tmp/sandbox_dir docker://rocm/dev-ubuntu-22.04:5.3.2-complete
$ cp py39_pytorch_rocm.yml /tmp/sandbox_dir/
$ wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O /tmp/sandbox_dir/conda_installer.sh
$ singularity exec --writeable --no-home /tmp/sandbox_dir bash /conda_installer.sh -b -s -p /opt/conda
$ echo "source /opt/conda/etc/profile.d/conda.sh\n" >> /tmp/sandbox_dir/environment
$ singularity exec --writeable --no-home /tmp/sandbox_dir conda update -y -n base -c conda-forge conda
$ singularity exec --writeable --no-home /tmp/sandbox_dir conda env create -f /py39_pytorch_rocm.yml -n conda_container_env
$ echo "conda activate conda_container_env\n" >> /tmp/sandbox_dir/environment
$ singularity exec --writeable --no-home /tmp/sandbox_dir conda clean -y -a
$ rm /tmp/sandbox_dir/conda_installer.sh
$ singularity build lumi_pytorch_rocm_demo.sif /tmp/sandbox_dir
$ rm -rf /tmp/sandbox_dir
```

<br /><br /><br /><br /><br /><br /><br /><br /><br />

## Ideally - and soon - a much more readable one-liner

```bash
$ cotainr build lumi_pytorch_rocm_demo.sif --system=lumi-g --conda-env py39_pytorch_rocm.yml
```

kind of similar to

```bash
$ conda env create --file py39_pytorch_rocm.yml
```

<br /><br /><br /><br /><br /><br /><br /><br /><br />

## In demo video

```bash
$ cotainr build lumi_pytorch_rocm_demo.sif --base-image docker://rocm/dev-ubuntu-22.04:5.3.2-complete --conda-env py39_pytorch_rocm.yml
```
