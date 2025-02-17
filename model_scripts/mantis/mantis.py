import argparse
from PIL import Image
import json
import torch
import random
from transformers import AutoProcessor, AutoModelForPreTraining
import PIL
import torch
from transformers import LlavaForConditionalGeneration, AutoProcessor
from conversation import conv_mllava_v1 as default_conv
from conversation import conv_mllava_v1_mmtag as default_conv_mmtag
from preprocess_util import preprocess_interleaved_images_and_text
from typing import List, Tuple, Union, Tuple
from PIL import Image
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

class mantisInstance:
    def __init__(self, args):
        self.processor = AutoProcessor.from_pretrained(args.model_path)
        self.model = AutoModelForPreTraining.from_pretrained(args.model_path, device_map="auto", torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2")
        self.model.to(args.device)

    # - - - - - - - - - - - - - - - -

    def chat_mllava(
        self,
        text:str, 
        images: List[Union[PIL.Image.Image, str]], 
        model:LlavaForConditionalGeneration, 
        processor, 
        max_input_length:int=None, 
        history:List[dict]=None, 
        **kwargs) -> Tuple[str, List[dict]]:

        conv = default_conv.copy()
        conv.messages = []
        if history is not None:
            for message in history:
                message["role"] = message["role"].upper()
                assert message["role"] in conv.roles
                conv.append_message(message["role"], message["text"])
        else:
            history = []
        conv.append_message(conv.roles[0], text)
        conv.append_message(conv.roles[1], "")
        
        prompt = conv.get_prompt()
        if images:
            for i in range(len(images)):
                if isinstance(images[i], str):
                    images[i] = PIL.Image.open(images[i])
        
        prompt, images = preprocess_interleaved_images_and_text(prompt, images)
        inputs = processor(images=images, text=prompt, return_tensors="pt", truncation=isinstance(max_input_length, int), max_length=max_input_length)
        for k, v in inputs.items():
            if v is not None:
                if isinstance(v, torch.Tensor):
                    inputs[k] = v.to(model.device)
                elif isinstance(v, list):
                    inputs[k] = [x.to(model.device) for x in v]
                else:
                    raise ValueError(f"Invalid input type: {type(v)}")

        if not "max_length" in kwargs and not "max_new_tokens" in kwargs:
            kwargs["max_length"] = 4096 
        output_ids = model.generate(**inputs, **kwargs)
        output_ids = output_ids[0]
        
        # remove the input tokens
        generated_ids = output_ids[inputs["input_ids"].shape[-1]:]
        generated_text = processor.decode(generated_ids, skip_special_tokens=True)

        history.append({"role": conv.roles[0], "text": text})
        history.append({"role": conv.roles[1], "text": generated_text})
        
        return generated_text, history

    # - - - - - - - - - - - - - - - -

    def chat_mllava_with(
        self,
        text:str, 
        images: List[Union[PIL.Image.Image, str]], 
        model:LlavaForConditionalGeneration, 
        processor, 
        max_input_length:int=None, 
        history:List[dict]=None, 
        **kwargs) -> Tuple[str, List[dict]]:

        conv = default_conv.copy()
        conv.messages = []
        if history is not None:
            for message in history:
                message["role"] = message["role"].upper()
                assert message["role"] in conv.roles
                conv.append_message(message["role"], message["text"])
        else:
            history = []
        conv.append_message(conv.roles[0], text)
        conv.append_message(conv.roles[1], "")
        
        prompt = conv.get_prompt()
        if images:
            for i in range(len(images)):
                if isinstance(images[i], str):
                    images[i] = PIL.Image.open(images[i])
        
        prompt, images = preprocess_interleaved_images_and_text(prompt, images)
        inputs = processor(images=images, text=prompt, return_tensors="pt", truncation=isinstance(max_input_length, int), max_length=max_input_length)
        for k, v in inputs.items():
            if v is not None:
                if isinstance(v, torch.Tensor):
                    inputs[k] = v.to(model.device)
                elif isinstance(v, list):
                    inputs[k] = [x.to(model.device) for x in v]
                else:
                    raise ValueError(f"Invalid input type: {type(v)}")

        if not "max_length" in kwargs and not "max_new_tokens" in kwargs:
            kwargs["max_length"] = 4096 

        kwargs["output_scores"] = True 
        kwargs["return_dict_in_generate"] = True

        output_ids = model.generate(**inputs, **kwargs)
            
        pbc_probas = output_ids.scores[0][:, self.answer_sets_token_id[self.index2label.get(0)] + self.answer_sets_token_id[self.index2label.get(1)]].softmax(-1)
        yes_proba_matrix = pbc_probas[:, :len(self.answer_sets[self.index2label.get(0)])].sum(dim=1)
        no_proba_matrix = pbc_probas[:, len(self.answer_sets[self.index2label.get(0)]):].sum(dim=1)
        probas = torch.cat((yes_proba_matrix.reshape(-1, 1), no_proba_matrix.reshape(-1, 1)), -1)
        max_probas_token = torch.max(probas, dim=1)
        
        
        sequence_probas = [float(proba) for proba in max_probas_token.values]
        sequence = [self.index2label.get(int(indice)) for indice in max_probas_token.indices]
        return sequence[0], round(sequence_probas[0], 2)
        

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
    def getResponse(self, args, prompt, images):
        with torch.no_grad():
            response, history = self.chat_mllava(prompt, images, self.model, self.processor)
        return response

    def getProbabilities(self, args, prompt, images):
        with torch.no_grad():
            return self.chat_mllava_with(prompt, images, self.model, self.processor)
    
    # - - - - - - - - - - - - - - - -

    # save answer from model
    def saveAnswer(self, answerFile, question, response, probText, prob):
        with open(answerFile, encoding="utf-8", mode="a") as outfile:
            outfile.write("""{\"question_id\": \"%s\", \"news_image\": \"%s\", \"entity_image\": \"%s\", \"question\": \"%s\", \"entity\": \"%s\", \"testlabel\": \"%s\", \"set\": \"%s\", \"entityID\": \"%s\", \"gTruth\": \"%s\", \"gWrong\": \"%s\", \"response\": \"%s\", \"probText\": \"%s\", \"prob\": \"%s\"}\n""" 
                % (str(question['question_id']), str(question['news_image']), str(question['entity_image']), str(question['question']), str(question['entity']), str(question['testlabel']), str(question['set']), str(question['entityID']), str(question['gTruth']), str(question['gWrong']), str(response), str(probText), str(prob)))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                

# run model
def run(args, answerFile):
    mantis = mantisInstance(args)
    mantis.cleanAnswers(answerFile)

    questions = []
    with open(args.question_file, encoding="utf-8", mode='r') as file:
        for line in file:
            questions.append(json.loads(line))

        random.shuffle(questions)
        for question in questions:
            prompt = f"<image> <image> {question['question']}"
            mantis.setTokenIDs(question["gTruth"], question["gWrong"])            
            response = mantis.getResponse(args, prompt, [Image.open(f"{question['news_image']}"), Image.open(f"{question['entity_image']}")])
            probText, prob = mantis.getProbabilities(args, prompt, [Image.open(f"{question['news_image']}"), Image.open(f"{question['entity_image']}")])
            mantis.saveAnswer(answerFile, question, response, probText, prob)  

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    transformers_logging.set_verbosity_error()
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="./models/Mantis-llava-7b/")
    parser.add_argument("--question-file", type=str, default="")
    parser.add_argument("--answer-file-path", type=str, default="")
    parser.add_argument("--answer-file-name", type=str, default="")
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    answerFile = f"{args.answer_file_path}{args.answer_file_name}.jsonl"
    run(args, answerFile)
