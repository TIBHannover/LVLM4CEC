#  Verifying Cross-modal Entity Consistency in News using Vision-language Models
This repository is the official implementation of [Verifying Cross-modal Entity Consistency in News using Vision-language Models](https://arxiv.org/abs/2501.11403) published in ECIR 2025.

Please use the following citation:
```
@InProceedings{ECIR_Tahmasebi25,
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
Each experiment contains its own script to analyze the answers. To run the pipeline and evaluate on datasets, you should run the bash file specific to each experiment and dataset with following commands.:
```
<path_to_experiment>/run_<dataset_name>.sh <basepath_to_experiment> <generate_questions_flag> <generate_answers_flag>
```
for example to run the pipeline on news400_ent dataset without using the evidence images you should run:
```
LVLM4CEC/01_without_evidence_images/run_news400.sh LVLM4CEC/01_without_evidence_images/ 1 1
```

All generated output will be then saved in ./output directory. you can then print the results for specific model by running PrintResults.py
1.5. output
All generated output is saved in ./output. 

## Credit
This repository is built by [Sahar Tahmasebi](https://github.com/sahartahmasebi). 

## Contributing

Our work is licenced under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This project includes tamperedNews and news400 data that is licensed under the [CC BY 3.0] by [Eric Müller-Budack](https://data.uni-hannover.de/dataset/tamperednews-news400-ijmir21). The original data has been modified to suit the needs of this project.