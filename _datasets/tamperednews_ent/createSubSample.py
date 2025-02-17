import numpy
import json

subsamples = ['events']

def createSubSample():
    open(f"./_datasets/tamperednews/_data/tamperednews_train.jsonl", 'w').close()

    annotated = []
    with open('./_datasets/tamperednews/tamperednews.jsonl', 'r') as f:
        for line in f:
            annotated.append(json.loads(line)["id"])

    data = []
    with open('./_datasets/tamperednews/_data/tamperednews_full.jsonl', 'r') as f:
        for line in f:
            object = json.loads(line)
            if object["id"] not in annotated:
                data.append(object)

    with open(f"./_datasets/tamperednews/_data/tamperednews_train.jsonl", 'a') as f:
        for dat in data:
            f.write(json.dumps(dat) + "\n")
                

if __name__ == "__main__":
    createSubSample()