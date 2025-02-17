import json
import random
import argparse
import numpy as np
import glob

entityObjects = [
    {
        "name": "persons",
        "label": "annotation_persons",
        "entities": [],
    },
    {
        "name": "locations",
        "label": "annotation_locations",
        "entities": [],
    },
    {
        "name": "events",
        "label": "annotation_events",
        "entities": [],
    }
]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def loadEntities():
    for entityObject in entityObjects:
        with open(f"./_datasets/tamperednews/entities/{entityObject['name']}.jsonl", 'r') as file:
            for line in file:
                entityObject['entities'].append(json.loads(line))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def extractNameById(id, entities):
    for entity in entities:
        if id == entity['wd_id']:
            return str(entity['wd_label']).replace("\"", "'").replace("'", "").lower()

def createSingleEntityQuestions(args):
    with open(f"./_datasets/tamperednews/tamperednews.jsonl", 'r') as file:
        for line in file:
            # extract line
            lineObject = json.loads(line)

            # person, location, event
            for entityObject in entityObjects:
                if lineObject[entityObject['label']] == 1:

                    baseQuestion = "\"Does the two images show the same {} ?\""

                    # text entites
                    if 'untampered' in lineObject['test_' + entityObject['name']]:
                        for entityID in lineObject['test_' + entityObject['name']]['untampered']:
                            if entityObject['name'] == "locations":
                                entityFiles = glob.glob(f"/nfs/data/image_repurposing/BreakingNews/reference_images/wd_PLACES/{entityID}/google_*.jpg")
                            else:
                                entityFiles = glob.glob(f"/nfs/data/image_repurposing/BreakingNews/reference_images/wd_{str(entityObject['name']).upper()}/{entityID}/google_*.jpg")
                            
                            if len(entityFiles) == 0:
                                continue

                            for counter, entity_image in enumerate(entityFiles):
                                news_image = f"./_datasets/tamperednews/images/{str(lineObject['id'])}.jpg"

                                # TODO
                                #question = baseQuestion.format(entityObject['name'][:-1])
                                question = args.prompt.replace("<type>", entityObject['name'][:-1])
                                question = question.replace("<name>", extractNameById(entityID, entityObject['entities']))

                                # text entites (validated visible)
                                if 'visible' in lineObject['test_' + entityObject['name']]:
                                    if entityID in lineObject['test_' + entityObject['name']]['visible']:
                                        saveQuestion(args, str(lineObject['id']), str(entityID), str(news_image), str(entity_image), str(question), str(entityObject['name']), "orginal", "text", "yes", "no")
                                    else:
                                        saveQuestion(args, str(lineObject['id']), str(entityID), str(news_image), str(entity_image), str(question), str(entityObject['name']), "orginal", "text", "no", "yes")
                                else:
                                    saveQuestion(args, str(lineObject['id']), str(entityID), str(news_image), str(entity_image), str(question), str(entityObject['name']), "orginal", "text", "no", "yes")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
def saveQuestion(args, id, entityID, news_image, entity_image, question, entity, testlabel, set, ground_truth, ground_wrong):
    with open(args.question_file, "a") as outfile:
        outfile.write("""{\"question_id\": \"%s_%s\", \"news_image\": \"%s\", \"entity_image\": \"%s\", \"question\": %s, \"entity\": \"%s\", \"testlabel\": \"%s\", \"set\": \"%s\", \"entityID\": \"%s\", \"gTruth\": \"%s\", \"gWrong\": \"%s\"} \n""" 
                      % (id, entityID, news_image, entity_image, question, entity, testlabel, set, entityID, ground_truth, ground_wrong))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    # delete questions
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-file", type=str, default="")
    parser.add_argument("--base-path", type=str, default="")
    parser.add_argument("--prompt", type=str, default="")
    args = parser.parse_args()

    open(args.question_file, 'w').close()

    # load entity datasets
    loadEntities()

    # create Questions
    createSingleEntityQuestions(args)