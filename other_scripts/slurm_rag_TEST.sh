#!/bin/bash

################## RESOURCES REQUEST (time, memory and cores)
#SBATCH -J mixtral_rag              # the job name, just like on UGE, can be hard coded here
#SBATCH -t 0:10:00             # maximal runtime (hour:minutes:seconds)
#SBATCH --mem-per-cpu 16G       # amount of memory per core
#SBATCH --cpus-per-task=4       # number of cores

################## OUTPUT LOG FILES
#SBATCH -o /work/borimcor/logs/%x-%A.out   #  here they will dumped on your /work/<your_user> folder
#SBATCH -e /work/borimcor/logs/%x-%A.err

################## MODULES
# Load the necessary modules. This part seems correct.
module load GCC/12.2.0 OpenMPI/4.1.4 Python/3.10.8
module load Anaconda3/2023.03
module load CUDA/11.7.0
#module load CUDA/12.0.0

# Activate the specified conda environment
source activate ollama
export CUDA_VISIBLE_DEVICES=0,1 # Restrict usage to the first two GPUs

# Record the start date and time
date
echo "Starting to load libs scrip"

python /gpfs1/work/borimcor/MIXTRAL_TEST/load_libs.py

# Mark the end of the script execution
echo 'Finishing'
date
# End of script
