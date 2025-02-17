import json
import random
import argparse

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
        with open(f"./_datasets/tamperednews_ent/entities/{entityObject['name']}.jsonl", 'r') as file:
            for line in file:
                entityObject['entities'].append(json.loads(line))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def extractNameById(id, entities):
    for entity in entities:
        if id == entity['wd_id']:
            return str(entity['wd_label']).replace("\"", "'").replace("'", "").lower()

def createSingleEntityQuestions(args):
    with open(f"./_datasets/tamperednews_ent/tamperednews_ent.jsonl", 'r') as file:
        for line in file:
            # extract line
            lineObject = json.loads(line)

            # person, location, event
            for entityObject in entityObjects:
                if lineObject[entityObject['label']] == 1:

                    # text entites
                    if 'untampered' in lineObject['test_' + entityObject['name']]:
                        for entityID in lineObject['test_' + entityObject['name']]['untampered']:
                            if not extractNameById(entityID, entityObject['entities']):
                                continue

                            question = ""
                            if entityObject['name'] == "events":
                                question = args.event_prompt
                            else:
                                question = args.prompt
                            
                            question = question.replace("<type>", entityObject['name'][:-1])
                            question = question.replace("<name>", extractNameById(entityID, entityObject['entities']))
                            
                            # text entites (validated visible)
                            if 'visible' in lineObject['test_' + entityObject['name']]:
                                if entityID in lineObject['test_' + entityObject['name']]['visible']:
                                    saveQuestion(args, str(lineObject['id']), str(question), str(entityObject['name']), "orginal", "text", entityID, "yes", "no")
                                else:
                                    saveQuestion(args, str(lineObject['id']), str(question), str(entityObject['name']), "orginal", "text", entityID, "no", "yes")
                            else:
                                saveQuestion(args, str(lineObject['id']), str(question), str(entityObject['name']), "orginal", "text", entityID, "no", "yes")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
def saveQuestion(args, id, question, entity, testlabel, set, entityID, ground_truth, ground_wrong):
    with open(args.question_file, "a") as outfile:
        outfile.write("""{\"question_id\": \"%s\", \"image\": \"./_datasets/tamperednews/images/%s.jpg\", \"question\": %s, \"entity\": \"%s\", \"testlabel\": \"%s\", \"set\": \"%s\", \"entityID\": \"%s\", \"gTruth\": \"%s\", \"gWrong\": \"%s\"} \n""" 
                      % (id, id, question, entity, testlabel, set, entityID, ground_truth, ground_wrong))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    # delete questions
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-file", type=str, default="")
    parser.add_argument("--base-path", type=str, default="")
    parser.add_argument("--prompt", type=str, default="")
    parser.add_argument("--event-prompt", type=str, default="")
    args = parser.parse_args()

    open(args.question_file, 'w').close()

    # load entity datasets
    loadEntities()

    # create Questions
    createSingleEntityQuestions(args)