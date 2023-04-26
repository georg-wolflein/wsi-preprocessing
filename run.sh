#!/bin/sh
set -eux
singularity run --nv --bind /data:/data mlcontext/e2e_container.sif run_wsi_norm.sh