# change file path if needed
files="tlsf2gpg/examples/*.tlsf"

tlsf2gpgpath="tlsf2gpg"

for f in ${files}; do
    name=$(basename $f)
    echo $name
    ./scripts/create_parity_automata.sh $f $name
done