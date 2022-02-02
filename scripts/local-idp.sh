#!/bin/bash
#
# start a local IDP for running CCUI SAML locally.
#
# See https://hub.docker.com/r/kristophjunge/test-saml-idp/ for more information
#

NAME=testsamlidp_idp

docker ps | grep "$NAME" >/dev/null 2>&1
if [[ "$?" = "0" ]]
then
	echo "Stopping existing $NAME ..."
	docker stop $NAME
	docker rm $NAME
fi

DIR=$(dirname $(realpath $0))
CONF_DIR=${DIR}/simplesaml-config

AUTHORITY="localhost:5001"
URL_PREFIX="http://${AUTHORITY}/saml"

echo "Starting $NAME ..."

docker run --name=$NAME \
    -p 8080:8080 \
    -p 8443:8443 \
    -e SIMPLESAMLPHP_SP_ENTITY_ID=${URL_PREFIX}/metadata/ \
    -e SIMPLESAMLPHP_SP_ASSERTION_CONSUMER_SERVICE=${URL_PREFIX}/acs \
    -e SIMPLESAMLPHP_SP_SINGLE_LOGOUT_SERVICE=${URL_PREFIX}/sls \
    -v ${CONF_DIR}/users.php:/var/www/simplesamlphp/config/authsources.php \
    -v ${CONF_DIR}/saml20-idp-hosted.php:/var/www/simplesamlphp/metadata/saml20-idp-hosted.php \
    -d kristophjunge/test-saml-idp

# EOF
