#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Please provide a shell script to run."
    exit 1
fi
    echo "Activating HPC conda environment..."
    . /opt/miniconda3/etc/profile.d/conda.sh
    conda activate hpc_cenv
    echo "Activated conda environment, running $1..."
    sh $1
