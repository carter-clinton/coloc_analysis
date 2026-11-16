#!/bin/sh
# properties = {properties}
# Placement audit in the job's .err log: CPU model here, and OpenBLAS prints "Core: <kernel>" at every library load.
echo "r4_placement host=$(hostname) cpu=$(grep -m1 'model name' /proc/cpuinfo | sed 's/^[^:]*: //')" >&2
export OPENBLAS_VERBOSE=2
{exec_job}
