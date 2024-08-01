#!/bin/bash
source ~/ragenv/bin/activate
python /home/amsinha/RAG-fr-medical/run_eval.py --file /home/amsinha/RAG-fr-medical/Results/FINETUNED/barthez/final_FT_ftbarthez_generation-p3-dev-25-redo.csv --readall
