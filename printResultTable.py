import json
import csv
import re
from pprint import pprint
import csv 
import argparse
from array import *


resultsCNN = {
    "persons": {
        "orginal"
    },
    "locations": {
        "orginal"
    },
    "events": {
        "orginal"
    }
}

def getValue(data, entity):
    for item in data:
        if item['entity'] == entity:
            return item['correct']

def getDocuments(data, entity):
    for item in data:
        if item['entity'] == entity:
            return item['documents']
        
def printResults(args):
    answertypes = ["yes", "no", "all"]
    resultsVLM = {}
    for answertype in answertypes:
        for modelname in args.models:
            # create object for model
            if modelname not in resultsVLM:
                resultsVLM[modelname] = {}

            if answertype not in resultsVLM[modelname]:
                resultsVLM[modelname][answertype] = []

            # read csv content
            if answertype != "yesno":
                with open(f"output/statistics/{modelname}-{answertype}.csv", 'r') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        resultsVLM[modelname][answertype].append(row)


    for answertype in answertypes:
        print(answertype)
        if answertype != "yesno":
            for entityType in resultsCNN:
                sentence_1 = "%s & %s & %s %s & %s & %s \\\\" % (
                    getValue(resultsVLM[args.models[0]][answertype], entityType), 
                    getValue(resultsVLM[args.models[1]][answertype], entityType), 
                    getValue(resultsVLM[args.models[2]][answertype], entityType),
                    getValue(resultsVLM[args.models[3]][answertype], entityType),
                    getValue(resultsVLM[args.models[4]][answertype], entityType),
                    getValue(resultsVLM[args.models[5]][answertype], entityType))
                print(f"        {entityType} & {getDocuments(resultsVLM[args.models[0]][answertype], entityType)} & {sentence_1}")

        else:
            for entityType in resultsCNN:
                #sentence_1 = "%s&%s & %s&%s & %s&%s & %s&%s &%s& %s \\\\" % (
                sentence_1 = "%s & %s & %s %s & %s & %s \\\\" % (
                    (float(getValue(resultsVLM[args.models[0]]['yes'], entityType)) + float(getValue(resultsVLM[args.models[0]]['no'], entityType))) / 2,
                    (float(getValue(resultsVLM[args.models[1]]['yes'], entityType)) + float(getValue(resultsVLM[args.models[1]]['no'], entityType))) / 2,
                    (float(getValue(resultsVLM[args.models[2]]['yes'], entityType)) + float(getValue(resultsVLM[args.models[2]]['no'], entityType))) / 2,
                    getValue(resultsVLM[args.models[3]]['yes'], entityType),
                    getValue(resultsVLM[args.models[3]]['no'], entityType),
                    getValue(resultsVLM[args.models[4]]['yes'], entityType),
                    getValue(resultsVLM[args.models[4]]['no'], entityType))
                print(f"        {entityType} & {getDocuments(resultsVLM[args.models[0]]['all'], entityType)} & {sentence_1}")
        print()
# - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs='*',default=['21_EV_1xN-news400-instructBlip-0',
                                                       '21_EV_1xN-news400-instructBlip-1',
                                                       '21_EV_1xN-news400-instructBlip-2',
                                                       '21_EV_1xN-news400-instructBlip-3',
                                                       '21_EV_1xN-news400-instructBlip-4',
                                                       '21_EV_1xN-news400-instructBlip-5'])
    args = parser.parse_args()
    printResults(args)