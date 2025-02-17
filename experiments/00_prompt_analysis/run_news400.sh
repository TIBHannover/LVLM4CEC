#!/bin/bash

answerFilePath=./output/model_answers/

# - - - - - - - - - -

prompts=(
    "\"Is <type> <name> shown in the image?\""
    "\"Is <type> <name> visible in the image?\""
    "\"Does the image depict the <type> <name>?\""
    "\"Is <type> <name> shown in the image? Answer only with yes or no.\""
    "\"Is <type> <name> visible in the image? Answer only with yes or no.\""
    "\"Is the content of the image consistent with the <type> <name>?\""
    "\"Is any <type> from the image consistent with <name>?\""
)
counter=0

# - - - - - - - - - -

for prompt in "${prompts[@]}"; do
    activeModels=()
    questionFile=$1/_questions/questions_news400-$counter.jsonl
    
    if [ $2 -eq 1 ]
    then
        python $1/scripts/news400/prepare_questions.py --base-path $1 --question-file $questionFile --prompt "$prompt" &
        PID=$!
        wait $PID
    fi

    answerFile=00_EV-news400-instructBlip-$counter
    activeModels+=(${answerFile})
    if [ $3 -eq 1 ]
    then
        python ./model_scripts/instructblip.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
        PID=$!
        wait $PID
    fi

    answerFile=00_EV-news400-blip2-$counter
    activeModels+=(${answerFile})
    if [ $3 -eq 1 ]
    then
        python ./model_scripts/blip2.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
        PID=$!
        wait $PID
    fi

    answerFile=00_EV-news400-llava157-$counter
    activeModels+=(${answerFile})
    if [ $3 -eq 1 ]
    then
        python ./model_scripts/llava.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
        PID=$!
        wait $PID
    fi

    python $1/scripts/news400/analyze_answers.py --models ${activeModels[@]} &
    PID=$!
    wait $PID

    let counter++
done