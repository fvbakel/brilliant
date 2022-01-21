#/bin/sh
# start a static https server
# usage: start.sh <path>
my_dir=`dirname $0`
${my_dir}/node_modules/http-server/bin/http-server $1 -S --cert ~/.my_secrets/cert.pem  --key ~/.my_secrets/key.pem -o 