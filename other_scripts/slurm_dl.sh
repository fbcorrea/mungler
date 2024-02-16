#!/bin/bash

################## RESOURCES REQUEST (time, memory and cores)
#SBATCH -J mixtral_dl            # the job name, just like on UGE, can be hard coded here
#SBATCH -t 1:00:00             # maximal runtime (hour:minutes:seconds)
#SBATCH --mem-per-cpu=8G       # amount of memory per core
#SBATCH --cpus-per-task=24       # number of cores

################## OUTPUT LOG FILES
#SBATCH -o /work/borimcor/logs/%x-%A-%a.out   #  here they will dumped on your /work/<your_user> folder
#SBATCH -e /work/borimcor/logs/%x-%A-%a.err

################## MODULES
# Load the necessary modules. This part seems correct.
module load GCC/12.2.0 OpenMPI/4.1.4 Python/3.10.8
module load Anaconda3/2023.03
module load CUDA/11.7.0


# Activate the specified conda environment
echo "loading environment..."
source activate ollama
#export CUDA_VISIBLE_DEVICES=0,1 # Restrict usage to the first two GPUs

# Execute the Python script. Adjust the path and parameters as necessary.
python /gpfs1/work/borimcor/MIXTRAL_TEST/dl_mixtral.py

# Mark the end of the script execution
echo 'Finishing'
date
# End of script
