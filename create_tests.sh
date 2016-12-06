# This script downloads a bunch of captchas to be used as the base of the program.
# You'll have to manually solve them, though.
#
# Usage: ./create_tests.sh (for 100 tests)
#        ./create_tests.sh 50 (for 50 tests)

for i in $(seq $1 $2); do
	curl -A "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5" https://prenotaonline.esteri.it/captcha/default.aspx\?pos\=2\&amp\;vers\=736\&amp\;vers\=595 > tests/image$i.jpeg 2> /dev/null
	echo $i
done
