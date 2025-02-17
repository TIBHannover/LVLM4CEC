#!/bin/bash

activeModels=()
answerFilePath=./output/model_answers/

# - - - - - - - - - -

promptsLocationsEvents=(
    "\"Is any <type> from the image consistent with <name>?\""
    "\"Is <type> <name> visible in the image?\""
    "\"Is <type> <name> shown in the image? Answer only with yes or no.\""
)
eventPrompt="\"Is the content of the image consistent with the <type> <name>? Answer only with yes or no.\""

# - - - - - - - - - -

for (( counter=0; counter<3; counter+=1 ))
do 
    questionFile=$1/_questions/questions_tamperednews-$counter.jsonl
    if [ $2 -eq 1 ]
    then
        python $1/scripts/tamperednews/prepare_questions.py --base-path $1 --question-file $questionFile --prompt "${promptsLocationsEvents[$counter]}" --event-prompt "$eventPrompt" &
        PID=$!
        wait $PID
    fi
done

# - - - - - - - - - -

answerFile=13_EV-tamperednews-blip2-0
questionFile=$1/_questions/questions_tamperednews-0.jsonl
activeModels+=(${answerFile})
if [ $3 -eq 1 ]
then
    python ./model_scripts/blip2.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
    PID=$!
    wait $PID
fi

answerFile=13_EV-tamperednews-instructBlip-0
questionFile=$1/_questions/questions_tamperednews-1.jsonl
activeModels+=(${answerFile})
if [ $3 -eq 1 ]
then
    python ./model_scripts/instructblip.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
    PID=$!
    wait $PID
fi

modelPath=./models/llava-1.5-7b-hf/
answerFile=13_EV-tamperednews-llava_15_7b-0
questionFile=$1/_questions/questions_tamperednews-2.jsonl
activeModels+=(${answerFile})
if [ $3 -eq 1 ]
then
    python ./model_scripts/llava.py --question-file $questionFile --answer-file-path $answerFilePath --model-path $modelPath --answer-file-name $answerFile &
    PID=$!
    wait $PID
fi

modelPath=./models/llava-1.5-13b-hf/
answerFile=13_EV-tamperednews-llava_15_13b-0
questionFile=$1/_questions/questions_tamperednews-2.jsonl
activeModels+=(${answerFile})
if [ $3 -eq 1 ]
then
    python ./model_scripts/llava-4bit.py --question-file $questionFile --answer-file-path $answerFilePath --model-path $modelPath --answer-file-name $answerFile &
    PID=$!
    wait $PID
fi

modelPath=./models/llava-v1.6-mistral-7b-hf/
answerFile=13_EV-tamperednews-llava_16_7b-0
questionFile=$1/_questions/questions_tamperednews-2.jsonl
activeModels+=(${answerFile})
if [ $3 -eq 1 ]
then
    python ./model_scripts/llava-1.6.py --question-file $questionFile --answer-file-path $answerFilePath --model-path $modelPath --answer-file-name $answerFile &
    PID=$!
    wait $PID
fi

answerFile=13_EV-tamperednews-mantis-0
activeModels+=(${answerFile})
if [ $3 -eq 1 ]
then
    python ./model_scripts/mantis/mantis_solo.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
    PID=$!
    wait $PID
fi

answerFile=13_EV-tamperednews-deepseek-0
activeModels+=(${answerFile})
if [ $3 -eq 1 ]
then
    python ./model_scripts/DeepSeek/deepseek_solo.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
    PID=$!
    wait $PID
fi

# - - - - - - - - - -

python $1/scripts/tamperednews/analyze_answers.py --models ${activeModels[@]} &
PID=$!
wait $PID