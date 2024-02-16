#!/bin/bash

################## RESOURCES REQUEST (time, memory and cores)
#SBATCH -J mixtral_rag              # the job name, just like on UGE, can be hard coded here
#SBATCH -t 1:00:00             # maximal runtime (hour:minutes:seconds)
#SBATCH --mem-per-cpu 64G       # amount of memory per core
##SBATCH --cpus-per-task=4       # number of cores
#SBATCH -G nvidia-a100:1
#SBATCH --constraint a100-vram-80G 

################## OUTPUT LOG FILES
#SBATCH -o /work/borimcor/logs/%x-%A.out   #  here they will dumped on your /work/<your_user> folder
#SBATCH -e /work/borimcor/logs/%x-%A.err

################## MODULES
# Load the necessary modules. This part seems correct.
module load GCC/12.2.0 OpenMPI/4.1.4 Python/3.10.8
module load Anaconda3/2023.03
#module load CUDA/11.7.0
#module load CUDA/12.0.0
module load CUDA/11.8.0

# Activate the specified conda environment
echo "loading environment ..."
source activate ollama
export CUDA_VISIBLE_DEVICES=0,1 # Restrict usage to the first two GPUs

MODEL=${1:-"mixtral:instruct"}
EMBMODEL=${2:-"Salesforce/SFR-Embedding-Mistral"}
QUERY=${3:-"What event made Alice shrink? Try to link what happened to Alice. Be specific and brief."}

# Record the start date and time
date

echo "Starting ollama singularity"
# Execute the singularity container in the background
singularity run --nv --bind /gpfs1/work/borimcor/ollama:/root/.ollama \
    /gpfs1/schlecker/home/borimcor/ollama.sif &
PID=$!

#nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits >> /work/borimcor/MIXTRAL_TEST/gpu_memory_usage.log

#nvcc --version

echo "executing main script..."
# Execute the Python script. Adjust the path and parameters as necessary.
#python /gpfs1/work/borimcor/MIXTRAL_TEST/mervin_RAG_ONLY.py \
/gpfs1/work/borimcor/MIXTRAL_TEST/mervin_RAG.py \
	--query_text="$QUERY" \
	--model_llm="$MODEL" \
	--model_embedding="$EMBMODEL"

#nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits >> /work/borimcor/MIXTRAL_TEST/gpu_memory_usage.log

# Terminate the background Singularity process
kill $PID

# Mark the end of the script execution
echo 'Finishing'
date
# End of script
