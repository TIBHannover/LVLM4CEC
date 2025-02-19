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
- The fully annotated datasets used in this work, including images, can be found in _dataset directory.
- To access the original TamperedNews and News400 datasets with their corresponding images, visit: [TamperedNews & News400 Dataset](https://data.uni-hannover.de/dataset/tamperednews-news400-ijmir21)
- To access the original MMG dataset along with its images, visit: [MMG Dataset](https://link.springer.com/chapter/10.1007/978-3-031-28238-6_14)

## Evaluation
Each experiment includes a dedicated script for analyzing the generated answers. To run the pipeline and evaluate on different datasets, execute the corresponding bash script for the specific experiment and dataset using the following command:
```
<path_to_experiment>/run_<dataset_name>.sh <basepath_to_experiment> <generate_questions_flag> <generate_answers_flag>
```
For example, to run the pipeline on the ```news400_ent``` dataset without incorporating evidence images, use:
```
LVLM4CEC/01_without_evidence_images/run_news400.sh LVLM4CEC/01_without_evidence_images/ 1 1
```

All generated outputs, including model predictions and evaluation statistics, will be saved in the ```./output``` directory. To display the results for a specific model and prompt templates, specify the model name using the ```--models argument``` and run:
```
python PrintResults.py --models <model_name>
```
## Credit
This repository is built by [Sahar Tahmasebi](https://github.com/sahartahmasebi). 

## Contributing

Our work is licenced under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). It includes tamperedNews and news400 datasets which are licensed under [CC BY 3.0] by [Eric Müller-Budack](https://data.uni-hannover.de/dataset/tamperednews-news400-ijmir21). The original datasets have been modified to align with the requirements of this project.