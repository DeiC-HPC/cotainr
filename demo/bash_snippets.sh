# pygmentize -l console -f rtf -O fontsize=30 -o bash_snippets.rtf  bash_snippets.sh
# open/(copy/paste to) RTF file in MS Word, then copy MS Word content to MS PowerPoint to keep formatting and colors
$ conda env create --file my_conda_env.yml
$ cotainr build my_container.sif --system lumi-g --conda-env my_conda_env.yml

$ module load LUMI
$ module load cotainr

$ cotainr build my_container.sif --system lumi-c --conda-env my_conda_env.yml

$ singularity shell my_container.sif
$ srun --account=<YOUR_PROJECT> --partition=debug singularity exec my_container.sif python3 my_script.py