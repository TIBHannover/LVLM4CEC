import json
import random
import argparse
import numpy
import shutil

pathFulldataset = "./_datasets/mmg_ent/subsamples/mmg_locations_ent.jsonl"

entityObject = {
        "name": "locations",
        "entities": [],
        "test_labels": ["city", "country", "continent"]
    }

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def createSubSample():
    open(pathFulldataset, 'w').close()

    with open('./_datasets/mmg_ent/test_dataset.json', 'r') as f:
        data = json.load(f)

    rng = numpy.random.default_rng()
    randomRows = rng.choice(len(list(data['city'].keys())), size=200, replace=False)

    with open(pathFulldataset, 'a') as f:
        for i in randomRows:
            keyIndex = list(data['city'].keys())[i]
            del data['city'][keyIndex]['body']
            f.write(json.dumps(data['city'][keyIndex]) + "\n")
            id = data['city'][keyIndex]['id']
            shutil.copyfile(f'/nfs/home/tahmasebzadehg/mmg_news_dataset/image_splits/test/{id}.jpg', f'./_datasets/mmg_ent/images/{id}.jpg')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def loadEntities():
    with open(f"./_datasets/news400_ent/entities/{entityObject['name']}.jsonl", 'r') as file:
        for line in file:
            entityObject['entities'].append(json.loads(line))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def extractNameById(id, entities):
    for entity in entities:
        if id == entity['wd_id']:
            return str(entity['wd_label']).replace("\"", "'").replace("'", "").lower()


def createSingleEntityQuestions(args):
    with open(pathFulldataset, 'r') as file:
        for line in file:
            # extract line
            lineObject = json.loads(line)

            # city, country, continent
            for instance in entityObject['test_labels']:

                entityID = lineObject['image_label'][instance]['id']
                if extractNameById(entityID, entityObject['entities']) == None:
                    continue

                # save untampered question 
                question = args.prompt.replace("<type>", instance)
                question = question.replace("<name>", extractNameById(entityID, entityObject['entities']))
                saveQuestion(args, str(lineObject['id']), str(question), str(entityObject['name']), str(instance), "text", entityID, "yes", "no")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def saveQuestion(args, id, question, entity, testlabel, set, entityID, ground_truth, ground_wrong):
    with open(args.question_file, "a") as outfile:
        outfile.write("""{\"question_id\": \"%s\", \"image\": \"./_datasets/mmg_ent/images/%s.jpg\", \"question\": %s, \"entity\": \"%s\", \"testlabel\": \"%s\", \"set\": \"%s\", \"entityID\": \"%s\", \"gTruth\": \"%s\", \"gWrong\": \"%s\"} \n"""
                      % (id, id, question, entity, testlabel, set, entityID, ground_truth, ground_wrong))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    # delete questions
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-file", type=str, default="")
    parser.add_argument("--base-path", type=str, default="")
    parser.add_argument("--prompt", type=str, default="")
    args = parser.parse_args()

    # create new subsample from mmg dataset
    #createSubSample()

    open(args.question_file, 'w').close()

    # load entity datasets
    loadEntities()

    # create Questions
    createSingleEntityQuestions(args)

