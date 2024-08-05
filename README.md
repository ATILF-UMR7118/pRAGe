# pRAGe

📄 Code repository for [Retrieve, Generate, Evaluate: A Case Study for Medical Paraphrases Generation with Small Language Models](https://arxiv.org/abs/2407.16565)

🎉 Paper accepted at [KnowledgeableLMs](https://knowledgeable-lm.github.io/), a [ACL 2024](https://2024.aclweb.org/) Workshop.

# Setup environment

Create a virtual environment (e.g. *ragenv*) and install the *requirements* file.

```
python3 -m venv ~/ragenv
source ~/ragenv/bin/activate
pip3 install -r requirements.txt
```

# Files description

🗂️```data``` contains: 

  - ```Refomed-KB.zip```: a 1.7M tokens knowledge base automatically extracted from Wikipedia articles for 1,253 medical terms from RefoMED (the *test* list). 

  **Format**

  For every term, for example, ```asthma```, the Refomed-KB contains top-3 wiki extracts namely, ```asthma-0.txt, asthma-1.txt, asthma-2.txt```.

  - ```RefoMED dataset (Buhnila, 2023)```: an [open-source dataset](https://github.com/ibuhnila/refomed) of 6,297 pairs of unique medical terms and their corresponding sub-sentential paraphrases in French.

  **Format**

  - ```refomed_test.csv```: list used for test and evaluation
  - ```refomed_train.csv```: list used for finetuning BioMistral and BARTHEZ
  - ```refomed_val.csv```: list used for validation

💻```notebooks``` contains: Python codes used for **inference generation, finetuning, pRAGe settings and data visualization**.

📊```plots``` contains **data visualization** plots

💻```scripts``` contains the Python codes for **evaluation** of the experiments and report generation.

# Citations
Please cite our work:

## pRAGe paper
```bibtex
@article{buhnila2024retrieve,
  title={Retrieve, Generate, Evaluate: A Case Study for Medical Paraphrases Generation with Small Language Models},
  author={Buhnila, Ioana and Sinha, Aman and Constant, Mathieu},
  journal={arXiv preprint arXiv:2407.16565},
  year={2024}
}
```
## RefoMED dataset
```bibtex
@phdthesis{buhnila2023methode,
  title={Une m{\'e}thode automatique de construction de corpus de reformulation},
  author={Buhnila, Ioana},
  year={2023},
  school={Universit{\'e} de Strasbourg}
}
```
