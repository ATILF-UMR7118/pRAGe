import pandas as pd

import argparse
import evaluate
from evaluate import load
import numpy as np
from tqdm import tqdm

from pathlib import Path
HOMEDIR = str(Path.home())

if 'root' in HOMEDIR:
    HOMEDIR = '/kaggle/working'

parser = argparse.ArgumentParser()

parser.add_argument("--filepath",default='./hirtz22KB-2.csv', help="Path to a tab-separated csv file of generated response")
parser.add_argument("--readall", action=argparse.BooleanOptionalAction, default=False,help="Flag to load entire generation csv")
#parser.add_argument("--split", required=True,help="Pick train or val")
#parser.add_argument("--expname", default='testing',help="Name to save the generated answer file")
args = parser.parse_args()


filename = args.filepath
if 'test' in filename:
    args.split = 'test'
else:
    args.split = 'val'

print(args)
# ==================  Reading the file ===========================
t10df = pd.read_csv(filename, sep='\t')
if not args.readall:
    t10df = t10df[:30]
    print(f"=====================Loaded {len(t10df)} generated samples===========================")
else:
    print(f"=====================Loaded {len(t10df)} generated samples===========================")

# ================== Preprocessing ================================
if 'generation' not in args.filepath:
    t10df["preprocessed_zsa"] = [l for l in t10df.raga]
else:
    t10df["preprocessed_zsa"] = [l for l in t10df.zsa]
if 'biom_generation' in args.filepath:
    t10df["preprocessed_zsa"] = [l.split('[/INST]')[-1] for l in t10df.zsa]
if 'final_gptq' in args.filepath:
    t10df["preprocessed_zsa"] = [l.split('[/INST]')[-1] for l in t10df.raga]
# ================== Load reference file ==========================

print("preprocessed samples:", t10df.preprocessed_zsa.values[:10])
print("*"*50,"\n")

if '' in t10df["preprocessed_zsa"].values:
    print("WARNING, EMPTY PARAPHRASE GENERATED!...................................................................S")
    #print([len(aa) for aa in t10df["preprocessed_zsa"].values])

split = args.split
refpath = HOMEDIR + '/RAG-fr-medical/finetuning/'

refdevdf = pd.read_csv(f'{refpath}refomed_{split}.csv', sep='\t')
refdevdf = refdevdf.iloc[:len(t10df),:]


"""
Prepare reference list 
"""

gold_reponse = {}
for k,v in zip(refdevdf.term, refdevdf.paraphrase):
    if k not in gold_reponse:
        gold_reponse[k] = [v]
    else:
        gold_reponse[k].append(v)

references = []
for i, kk in enumerate(refdevdf.term):
    references.append(gold_reponse[kk])


# ======================  evaluation metrics ======================================
rouge_scorer = evaluate.load('rouge')
bleu_scorer = evaluate.load('bleu')
bert_scorer = load("bertscore")
bleurt_scorer = load("bleurt", module_type="metric", config_name='BLEURT-20')


# =========================== running eval per sample =============================

"""
create a list of all scores for every gensent and ref pair
"""
print("evaluation started..................")
total = []
for i, (q, zsa,ref) in tqdm(enumerate(zip(refdevdf.term, t10df.preprocessed_zsa, references))):
    if len(zsa) == 0:
        continue
    curr = {"id": i, "generates_reponse": zsa, "score_per_ref": [], "max_score":{"rouge":-1, "bleu":-1,
                                                                                "bert":-1, "bleurt":-1}}
    for r in ref:
        rgs = rouge_scorer.compute(predictions=[zsa], references=[r])
        bls = bleu_scorer.compute(predictions=[zsa], references=[r], max_order=8)
        brt = bert_scorer.compute(predictions=[zsa], references=[r], lang='fr')
        blr = bleurt_scorer.compute(predictions=[zsa], references=[r])
        #print(rgs,bls,brt,blr)
        curr["score_per_ref"].append(
        {
            "text": zsa,
            "ref":r,
            "rouge":   rgs,
            "bleu":    bls,
            "bert":    brt,
            "bleurt":  blr
        })
        #================== rouge ====================
        if curr["max_score"]["rouge"] == -1:
            curr["max_score"]["rouge"] =  rgs
        else:
            if curr["max_score"]["rouge"]['rouge1'] < rgs['rouge1']:
                curr["max_score"]["rouge"] =  rgs
        #  =================== bleu ====================       
        if curr["max_score"]["bleu"] == -1:
            curr["max_score"]["bleu"] =  bls
        else:
            if curr["max_score"]["bleu"]['bleu'] < bls['bleu']:
                curr["max_score"]["bleu"] =  bls
        # ================== bert ======================      
        if curr["max_score"]["bert"] == -1:
            curr["max_score"]["bert"] =  brt
        else:
            if curr["max_score"]["bert"]['f1'][0] < brt['f1'][0]:
                curr["max_score"]["bert"] =  brt
        # ==================  bleurt =====================
        if curr["max_score"]["bleurt"] == -1:
            curr["max_score"]["bleurt"] =  blr
        else:
            if curr["max_score"]["bleurt"]['scores'][0] < blr['scores'][0]:
                curr["max_score"]["bleurt"] =  blr
        
    total.append(curr)
    #break
    

"""
Generate a dataframe and obtain descriptive statistics
"""
qs,gs = [],[]
ids, generate_response, bleus,berts,rouge1s,rouge2s,rouge3s,rouge4s,bleurts = [], [], [], [], [], [], [], [], []
bleup1, bleup2,bleup3, bleup4, bleup5, bleup6, bleup7, bleup8 = [], [], [], [], [], [], [], []

for q,g,t in zip(refdevdf.term, refdevdf.paraphrase, total):
    #print(t)
    qs.append(q)
    gs.append(g)
    ids.append(t['id'])
    generate_response.append(t['generates_reponse'])
    bleus.append(t['max_score']['bleu']['bleu'])
    bleup1.append(t['max_score']['bleu']['precisions'][0])
    bleup2.append(t['max_score']['bleu']['precisions'][1])
    bleup3.append(t['max_score']['bleu']['precisions'][2])
    bleup4.append(t['max_score']['bleu']['precisions'][3])
    bleup5.append(t['max_score']['bleu']['precisions'][4])
    bleup6.append(t['max_score']['bleu']['precisions'][5])
    bleup7.append(t['max_score']['bleu']['precisions'][6])
    bleup8.append(t['max_score']['bleu']['precisions'][7])
    berts.append(t['max_score']['bert']['f1'][0])
    rouge1s.append(t['max_score']['rouge']['rouge1'])
    rouge2s.append(t['max_score']['rouge']['rouge2'])
    rouge3s.append(t['max_score']['rouge']['rougeL'])
    rouge4s.append(t['max_score']['rouge']['rougeLsum'])
    bleurts.append(t['max_score']['bleurt']['scores'][0])
    #break
    
import pandas as pd
df = pd.DataFrame({'ids':ids, 'query_term':qs, 'gold_paraphrase':gs,
                   'gen_response': generate_response, 'best_bleu':bleus,
             'best_bert': berts, 'best_bleurt': bleurts,
                   'best_rouge1': rouge1s, 'best_rouge2': rouge2s,
                   'best_rougL': rouge1s,'best_rougeLsum': rouge4s,
                   'best_bleu_precision1': bleup1, 'best_bleu_precision2': bleup2, 
                   'best_bleu_precision3': bleup3, 'best_bleu_precision4': bleup4, 
                   'best_bleu_precision5': bleup5, 'best_bleu_precision6': bleup6, 
                   'best_bleu_precision7': bleup7, 'best_bleu_precision8': bleup8, 
                   })

# read before finalizing https://github.com/huggingface/datasets/issues/617 for rouge
savename = filename.split('/')[-1]
df.to_csv(HOMEDIR + f"/RAG-fr-medical/Reports/evaluation_resuls_{savename}", sep='\t', index=False)

print("Evaluation done succesfully!")

print("#"*30, "Report", "#"*30)
e = df.describe()

print(*e.columns[1:].values,sep='&')

print(*[np.round(k,4) for k in e.iloc[1,1:-4].values], sep='&')

print('#'*100)
