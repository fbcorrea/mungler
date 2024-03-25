# MunGLER - Metadata UNtanGLER

MunGLER utilizes Large Language Models (LLMs) to unravel sample metadata from DNA sequencing data within the Sequence Read Archive.

## Table of Contents

- [Visual Concept](#visual-concept)
- [Installation](#installation)
- [Hardware requirements](#hardware-requirements)
- [Usage](#usage)
- [Rationale](#rationale)
- [Contributing](#contributing)
- [License](#license)

## Visual Concept


## Installation

First clone this repository
```bash
git clone https://github.com/fbcorrea/mungler.git
```

Create a conda environment. I recommend using Mamba.
```bash
mamba create -n mungler
```

Install python packages using pip
```bash
pip install -r requirements.txt
```

## Hardware requirements

To effectively run this pipeline, it is strongly recommended to utilize a High-Performance Computing (HPC) system, ideally equipped with at least one recent high-end GPU card, such as the NVIDIA A100. This ensures optimal performance and reliability of the results.

Hardware requirements will be associated with the model used. Roughly, the larger the model, more memory it will require. If you chose to run Llama2 models from Meta, smaller models require 8GB vRAM while bigger up to 64GB vRAM. Other large models like Mixtral87b will require around 100GB vRAM.

Alternatively, some services allow users to pay per hour of process execution such as Amazon SageMaker (Amazon Web Services), Google Cloud AI Platform (Google Cloud Platform) and Azure Machine Learning (Microsoft Azure).

## Usage

### Activate Conda environment

If you followed the installation instructions, you must activate your Conda environment to run the mungler main script.

```bash
conda activate mungler
```
### Test run

In the first run, we recommend to run a test run with a toy dataset and tiny models.

```bash
mungler --acc-id SAMN06512631
```

If everything went well, you should get the following message:

```bash
Starting mungler test
Creating output
PASSED
```

### Actual workflow

#### Example 1.

Running mungler on a list of accession numbers.
Any SRA, ENA, Biosample, Bioproject are valid.
Invalid ids will be saved on a text file.

```bash
mungler 
    --acc-list list-of-ids.txt
    --output results.txt
    --invdir invalid-ids.txt
```

## Rationale

**mungler** takes as input accession numbers from SRA, access its metadata and tries to fill metadata fields 

Before:

After:


## Contributing

Guidelines on how to contribute to the project.

## License

Information about the project's license.
