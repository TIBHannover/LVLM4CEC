#!/bin/bash

answerFilePath=./output_sahar/model_answers/
# - - - - - - - - - -

prompts=(
    "\"Does the image with red border show the same <type> as the image with blue border?\""
    "\"Does the image with red border show the same <type> as the image with blue border? answer with yes or no\""
    "\"could the image with blue border be a reference image showing the same <type> for the image with red border?\""
)
counter=3

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

  ######### BLIP2
    #answerFile=21_EV_1xN-news400-blip2-$counter
    #activeModels+=(${answerFile})
    #if [ $3 -eq 1 ]
    #then
    #    python ./model_scripts/blip2.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
    #    PID=$!
    #    wait $PID
    #fi
  ######### InstructBLIP
    answerFile=21_EV_1xN-news400-instructBlip-$counter
    activeModels+=(${answerFile})
    if [ $3 -eq 1 ]
    then
        python ./model_scripts/instructblip.py --question-file $questionFile --answer-file-path $answerFilePath --answer-file-name $answerFile &
        PID=$!
        wait $PID
    fi
  ######### LLaVa 1.5 7b
    modelPath="llava-hf/llava-1.5-7b-hf"
    answerFile=21_EV_1xN-news400-llava_15_7b-$counter
    activeModels+=(${answerFile})
    if [ $3 -eq 1 ]
    then
        python ./model_scripts/llava.py --question-file $questionFile --answer-file-path $answerFilePath --model-path $modelPath --answer-file-name $answerFile &
        PID=$!
        wait $PID
    fi
  ######## LLaVA 1.5 13b
    #modelPath=./models/llava-1.5-13b-hf/
    #answerFile=21_EV_1xN-news400-llava_15_13b-$counter
    #activeModels+=(${answerFile})
    #if [ $3 -eq 1 ]
    #then
    #    python ./model_scripts/llava-4bit.py --question-file $questionFile --answer-file-path $answerFilePath --model-path $modelPath --answer-file-name $answerFile &
    #    PID=$!
    #    wait $PID
    #fi
  ######## LLaVA 1.6-mistral
    #modelPath=./models/llava-v1.6-mistral-7b-hf/
    #answerFile=21_EV_1xN-news400-llava_16_7b-$counter
    #activeModels+=(${answerFile})
    #if [ $3 -eq 1 ]
    #then
    #    python ./model_scripts/llava-1.6.py --question-file $questionFile --answer-file-path $answerFilePath --model-path $modelPath --answer-file-name $answerFile &
    #    PID=$!
    #    wait $PID
    #fi

    python $1/scripts/news400/analyze_answers.py --models ${activeModels[@]} &
    PID=$!
    wait $PID

    #python $1/scripts/news400/printResultTable.py --models ${activeModels[@]} &
    #PID=$!
    #wait $PID

    let counter++
done


