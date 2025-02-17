#!/bin/bash

answerFilePath=./output/model_answers/

# - - - - - - - - - -

prompts=(
    "\"Is the <type> in image 1 visible in image 2?\""
    "\"Does the two images show the same <type>?\""
    "\"Is the <type> in image 2 consistent with image 1?\""
)
counter=0

# - - - - - - - - - -

for prompt in "${prompts[@]}"; do
    activeModels=()
    questionFile=$1/_questions/questions_tamperednews-$counter.jsonl

    if [ $2 -eq 1 ]
    then
        python $1/scripts/tamperednews/prepare_questions.py --base-path $1 --question-file $questionFile --prompt "$prompt" &
        PID=$!
        wait $PID
    fi

    answerFile=22_EV_1xN-tamperednews-mantis-$counter
    activeModels+=(${answerFile})
    if [ $3 -eq 1 ]
    then
        python ./model_scripts/mantis/mantis.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
        PID=$!
        wait $PID
    fi

    answerFile=22_EV_1xN-tamperednews-deepseek-$counter
    activeModels+=(${answerFile})
    if [ $3 -eq 1 ]
    then
        python ./model_scripts/DeepSeek/deepseek.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
        PID=$!
        wait $PID
    fi

    python $1/scripts/tamperednews/analyze_answers.py --models ${activeModels[@]} &
    PID=$!
    wait $PID

    python $1/scripts/tamperednews/printResultTable.py --models ${activeModels[@]} &
    PID=$!
    wait $PID

    let counter++
done