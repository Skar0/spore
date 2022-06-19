#!/bin/bash

if [ ! -f $1 ]; then
    echo "Please provide a TLSF file as argument"
    return 1
fi

# change here path to the right folders
syfcopath="."
ltl2tgbapath="."
tempfolder="automata"
name="spec"
if [[ $# -ge 2 ]]; then
    name=$2
fi
mkdir -p ${tempfolder}/${name}
file="${tempfolder}/${name}/data.txt"

inputs=$(${syfcopath}/syfco $1 --print-input-signals \
    | sed "s/,//g" \
    | tr "[:upper:]" "[:lower:]")
outputs=$(${syfcopath}/syfco $1 --print-output-signals \
    | sed "s/,//g" \
    | tr "[:upper:]" "[:lower:]")
specs=$(${syfcopath}/syfco $1 --format ltlxba-decomp --mode fully -s1)

echo ${inputs} > ${file}
echo ${outputs} >> ${file}

c=0
while read -r line; do
    c=$((c+1))
    path="${tempfolder}/${name}/${c}.hoaf"
    echo ${path} >> ${file}
    ${ltl2tgbapath}/ltl2tgba --state-based-acceptance \
        --colored-parity="max even" \
        --deterministic \
        --complete \
        -f "$line" > "${path}"
    if [ ! -s ${path} ]; then
        rm ${file}
        touch ${file}
        break
    fi
done <<< "${specs}"