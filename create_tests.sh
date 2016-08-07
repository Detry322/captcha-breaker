# This script downloads a bunch of captchas to be used as the base of the program.
# You'll have to manually solve them, though.
#
# Usage: ./create_tests.sh (for 100 tests)
#        ./create_tests.sh 50 (for 50 tests)

NUM_TESTS=${1:-100}

for i in $(seq 1 $NUM_TESTS); do
	curl 'https://prenotaonline.esteri.it/captcha/default.aspx\?pos=2&vers=662&vers=282&vers=673&vers=517&vers=465' > tests/image$i.jpeg 2> /dev/null
	echo $i
done
