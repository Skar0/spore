#!/bin/bash

function get_time {
    while read -r line; do
        # User is the CPU time
        if [[ ${line} =~ "user" ]]
        then
            # We extract only the seconds
            cpu_time=$(echo ${line} | cut -d' ' -f2 | cut -d'm' -f2 | cut -d's' -f1)
        fi
    done < /tmp/time
    # Return the cpu_time
    echo ${cpu_time}
}

all_example_files="tlsf2gpg/examples/*.tlsf"

modes_gpg=(reg regPa regPaMu bdd bddPa bddPaMu)
modes_without_gpg=(fbdd fbddPa fbddPaMu)

max_minutes=10
time_limit=$((${max_minutes} * 60))

output="full-bdd-${max_minutes}m.csv"

echo \
    "FILE, " \
    "GPG BDD SIZE, " \
    "GPG SIZE, " \
    "GPG FUNC, " \
    "REG TIME, " \
    "REG PA TIME, " \
    "REG PA MU TIME, " \
    "BDD TIME, " \
    "BDD PA TIME, " \
    "BDD PA MU TIME, " \
    "FULL BDD GENERATION TIME, " \
    "FULL BDD BDD SIZE, " \
    "FULL BDD GAME SIZE, " \
    "FULL BDD FUNC, " \
    "FULL BDD TIME, " \
    "FULL BDD PA TIME, " \
    "FULL BDD PA MU TIME, " \
    > ${output}

for example in $all_example_files; do
    example_name=$(basename $example .tlsf)
    echo $example_name
    gpg_path="$example.gpg"
    echo -n "$example_name, " >> ${output}
    # First, the algorithms using the explicit construction
    if [ -s ${gpg_path} ]; then
        # The file is not empty, i.e., the game was generated in time
        # We retrieve the size of the game and the number of functions
        timeout -k 10 ${time_limit} python3 run_for_benchmark.py "gpgSizeFunc" $gpg_path
        while read -r line; do
            echo -n "${line}, " >> ${output}
        done < "/tmp/out"

        # We execute every algorithm one by one
        for mode in ${modes_gpg[@]}; do
            echo "    ${mode}"
            { time timeout -k 10 ${time_limit} python3 run_for_benchmark.py $mode $gpg_path ; } 2> /tmp/time

            timedout=$?
            if [ $timedout -eq 124 ]; then
                echo -n "TIMEOUT, " >> ${output}
            else
                cpu_time=$(get_time)
                echo -n "${cpu_time}, " >> ${output}
            fi
        done
    else
        # The file is empty, i.e., it was not possible to generate the game in time
        # We force the program to stop 10 seconds after the time limit
        echo -n "NOT GEN, NOT_GEN, NOT GEN, " >> ${output}
        for mode in ${modes_gpg[@]}; do
            echo -n "NOT GEN, " >> ${output}
        done
    fi

    # Second, the algorithms using the symbolic construction
    # We retrieve the time needed to compute the game, and the bdd size, game size and number of functions
    fbdd_example="automata/${example_name}.tlsf/data.txt"
    if [ ! -s ${fbdd_example} ]; then
        echo -n "NOT GEN, NOT GEN, NOT GEN, NOT GEN," >> ${output}
        for mode in ${modes_without_gpg[@]}; do
            echo -n "NOT GEN, " >> ${output}
        done

    else
        echo "    Constructing BDD game"
        { time timeout -k 10 ${time_limit} python3 run_for_benchmark.py "fbddSizes" $fbdd_example ; } 2> /tmp/time
        timedout=$?
        # 124 means timeout
        if [ ${timedout} -eq 124 ]; then
            echo -n "TIMEOUT, TIMEOUT, TIMEOUT, TIMEOUT, " >> ${output}
            for mode in ${modes_without_gpg[@]}; do
                echo -n "TIMEOUT, " >> ${output}
            done
        else
            # The time needed to generate the game
            cpu_time=$(get_time)
            echo -n "$cpu_time, " >> ${output}

            # We read the program answer
            while read -r line; do
                echo -n "${line}, " >> ${output}
            done < /tmp/out

            for mode in ${modes_without_gpg[@]}; do
                echo "    $mode"
                { time timeout -k 10 ${time_limit} python3 run_for_benchmark.py $mode $fbdd_example ; } 2> /tmp/time
                timedout=$?
                if [ $timedout -eq 124 ]; then
                    echo -n "TIMEOUT, " >> ${output}
                else
                    cpu_time=$(get_time)
                    echo -n "$cpu_time, " >> ${output}
                fi
            done
        fi
    fi
    echo "" >> ${output}
done
