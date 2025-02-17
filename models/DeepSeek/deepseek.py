import argparse
from PIL import Image
import json
import torch
import random
from transformers import AutoModelForCausalLM
from deepseek_vl.models import VLChatProcessor, MultiModalityCausalLM
from deepseek_vl.utils.io import load_pil_images
import logging
from transformers import logging as transformers_logging

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


answerFullSet = {
    "A": {
        'index': 0,
        'token': ['A', 'a']
    },
    "B": {
        'index': 1,
        'token': ['B', 'b']
    },
    "yes": {
        'index': 0,
        'token': ['Yes', 'yes']
    },
    "no": {
        'index': 1,
        'token': ['No', 'no']
    },
}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class deepseekInstance:
    def __init__(self, args):
        self.processor = VLChatProcessor.from_pretrained(args.model_path)
        self.model: MultiModalityCausalLM = AutoModelForCausalLM.from_pretrained(args.model_path, torch_dtype=torch.float16)
        self.model = self.model.to(torch.bfloat16).cuda().eval()

    # - - - - - - - - - - - - - - - -
        
    # clean up answer file
    def cleanAnswers(self, answerFile):
        open(answerFile, "w").close()

    # set token ids for token probability
    def setTokenIDs(self, label1, label2):
        self.index2label = {
            answerFullSet[label1]['index']: label1,
            answerFullSet[label2]['index']: label2
        }
        self.answer_sets = {
            label1: answerFullSet[label1]['token'],
            label2: answerFullSet[label2]['token']
        }

        self.index2label = dict(sorted(self.index2label.items()))
        self.answer_sets = dict(sorted(self.answer_sets.items()))

        self.answer_sets_token_id = {}
        for label, answer_set in self.answer_sets.items():
            self.answer_sets_token_id[label] = []
            for answer in answer_set:
                self.answer_sets_token_id[label] += self.processor.tokenizer.encode(answer, add_special_tokens=False)

    # - - - - - - - - - - - - - - - -

    # return answer of model
    def getResponse(self, args, conversation):
        pil_images = load_pil_images(conversation)
        inputs = self.processor(
            conversations=conversation,
            images=pil_images,
            force_batchify=True
        ).to(args.device)

        inputs_embeds = self.model.prepare_inputs_embeds(**inputs)

        with torch.no_grad():
            outputs = self.model.language_model.generate(
                inputs_embeds=inputs_embeds, 
                attention_mask=inputs.attention_mask,
                pad_token_id=self.processor.tokenizer.eos_token_id,
                bos_token_id=self.processor.tokenizer.bos_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                max_new_tokens=1,
                do_sample=False,
                use_cache=True
            )
        return self.processor.tokenizer.decode(outputs[0].cpu().tolist(), skip_special_tokens=True)

    # return probability
    def getProbabilities(self, args, conversation):  
        pil_images = load_pil_images(conversation)
        inputs = self.processor(
            conversations=conversation,
            images=pil_images,
            force_batchify=True
        ).to(args.device)

        inputs_embeds = self.model.prepare_inputs_embeds(**inputs)
        with torch.no_grad():
            outputs = self.model.language_model.generate(
                inputs_embeds=inputs_embeds, 
                attention_mask=inputs.attention_mask,
                pad_token_id=self.processor.tokenizer.eos_token_id,
                bos_token_id=self.processor.tokenizer.bos_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                max_new_tokens=1,
                do_sample=False,
                use_cache=True,
                output_scores=True, 
                return_dict_in_generate=True
            )
            
        pbc_probas = outputs.scores[0][:, self.answer_sets_token_id[self.index2label.get(0)] + self.answer_sets_token_id[self.index2label.get(1)]].softmax(-1)
        yes_proba_matrix = pbc_probas[:, :len(self.answer_sets[self.index2label.get(0)])].sum(dim=1)
        no_proba_matrix = pbc_probas[:, len(self.answer_sets[self.index2label.get(0)]):].sum(dim=1)
        probas = torch.cat((yes_proba_matrix.reshape(-1, 1), no_proba_matrix.reshape(-1, 1)), -1)
        max_probas_token = torch.max(probas, dim=1)

        sequence_probas = [float(proba) for proba in max_probas_token.values]
        sequence = [self.index2label.get(int(indice)) for indice in max_probas_token.indices]
        return sequence[0], round(sequence_probas[0], 2)
    
    # - - - - - - - - - - - - - - - -

    # save answer from model
    def saveAnswer(self, answerFile, question, response, probText, prob):
        with open(answerFile, encoding="utf-8", mode="a") as outfile:
            outfile.write("""{\"question_id\": \"%s\", \"news_image\": \"%s\", \"entity_image\": \"%s\", \"question\": \"%s\", \"entity\": \"%s\", \"testlabel\": \"%s\", \"set\": \"%s\", \"entityID\": \"%s\", \"gTruth\": \"%s\", \"gWrong\": \"%s\", \"response\": \"%s\", \"probText\": \"%s\", \"prob\": \"%s\"}\n""" 
                % (str(question['question_id']), str(question['news_image']), str(question['entity_image']), str(question['question']), str(question['entity']), str(question['testlabel']), str(question['set']), str(question['entityID']), str(question['gTruth']), str(question['gWrong']), str(response), str(probText), str(prob)))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                

# run model
def run(args, answerFile):
    deepseek = deepseekInstance(args)
    deepseek.cleanAnswers(answerFile)

    questions = []
    with open(args.question_file, encoding="utf-8", mode='r') as file:
        for line in file:
            questions.append(json.loads(line))

        random.shuffle(questions)
        for question in questions:
            conversation = [
                            {
                                "role": "User",
                                "content": f"<image_placeholder> <image_placeholder> {question['question']} Answer only with yes or no.",
                                "images": [f"{question['news_image']}", f"{question['entity_image']}"]
                            },
                            {
                                "role": "Assistant",
                                "content": ""
                            }
                        ]
            deepseek.setTokenIDs(question["gTruth"], question["gWrong"])            
            response = deepseek.getResponse(args, conversation)
            probText, prob = deepseek.getProbabilities(args, conversation)
            deepseek.saveAnswer(answerFile, question, response, probText, prob)  

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    transformers_logging.set_verbosity_error()
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="./models/deepseek-vl-7b-chat/")
    parser.add_argument("--question-file", type=str, default="")
    parser.add_argument("--answer-file-path", type=str, default="")
    parser.add_argument("--answer-file-name", type=str, default="")
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    answerFile = f"{args.answer_file_path}{args.answer_file_name}.jsonl"
    run(args, answerFile)
