# 1. Verifying Cross-modal Entity Consistency in News using Vision-language Models
This repository is the official implementation of [Verifying Cross-modal Entity Consistency in News using Vision-language Models](https://arxiv.org/abs/2501.11403) published in ECIR 2025.

Please use the following citation:
```
@InProceedings{ECIR_Tahmasebi24,
  author    = {Sahar Tahmasebi, Eric Müller-Budack and Ralph Ewerth},
  booktitle = {European Conference on Information Retrieval, (ECIR) 2025,  Lucca, Italy, April 6-10, 2025},
  title     = {Verifying Cross-modal Entity Consistency in News using Vision-language Models},
  year      = {2025},
}
```

## Requirements

To install requirements:
```
conda create -n LVLM4CEC python=3.9.18
conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3.1 -c pytorch
pip install -r requirements.txt
```
## Datasets
- You can download the full annotated datasets of this work with images here : TODO
- To access the original dataset of TamperedNews and News400 with their images use this [link](https://data.uni-hannover.de/dataset/tamperednews-news400-ijmir21)
- To access the original MMG dataset with its images use this [link](https://link.springer.com/chapter/10.1007/978-3-031-28238-6_14).

## Evaluation
To run the pipeline and evaluate on datasets, you should run the bash file specific to each experiment and dataset.:
```
bash eval.sh
```
each experiment contains his own generate[README.md](..%2FCIKM%2FLVLM4FV%2FREADME.md)d questions from the datasets and script to analize the answers.
1. experiments without comparative images 
    1. document verification
    2. entity verification
2. with comparative images (single image input models)
    1. entity verification with single image
    2. entity verificaiton with multiple images
3. with comparative images (multi image input models)
    1. entity verification with single image
    2. entity verificaiton with multiple images

1.5. output
All generated output is saved in ./output. 

- Logs
Contains all logs from fulltest (SLURM log)
- Model Answers
    Contains all responses from each model, seperated by experiment and datatset
- statistics
    Contains a statistic for each model and mode, seperated by  experiment and datatset

## Credit
This repository is built by [Sahar Tahmasebi](https://github.com/sahartahmasebi). 

## Contributing

Our work is licenced under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This project includes tamperedNews and news400 data that is licensed under the [CC BY 3.0] by [Eric Müller-Budack](https://data.uni-hannover.de/dataset/tamperednews-news400-ijmir21). The original data has been modified to suit the needs of this project.





## 3. Reproduce Results
The experiments can be run by the following command
<path_to_experiment>/run_<dataset>.sh <basepath_to_experiment> <generate_questions> <generate_answers>

To run all all experiments with SLURM, look at ./utils/batch_fulltest.sh


## 4. streamlit Demo
Demo is created with [streamlit](https://streamlit.io/) and allows to examine results/answers of each model for each question/ data sample. It also contains the answers of the Baseline project [Link](https://github.com/TIBHannover/cross-modal_entity_consistency)
It can be run with the following command: 
- streamlit run app.py
- python -m streamlit run ./streamlitDemo/app.py
- ssh -N -f -L localhost:8501:localhost:8501 devbox5