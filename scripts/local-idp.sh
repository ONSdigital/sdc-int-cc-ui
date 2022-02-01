#!/bin/bash
#
# start a local IDP for running CCUI SAML locally.
#
# See https://hub.docker.com/r/kristophjunge/test-saml-idp/ for more information
#

AUTHORITY="localhost:5001"
URL_PREFIX="http://${AUTHORITY}/saml"

docker run --name=testsamlidp_idp \
    -p 8080:8080 \
    -p 8443:8443 \
    -e SIMPLESAMLPHP_SP_ENTITY_ID=${URL_PREFIX}/metadata/ \
    -e SIMPLESAMLPHP_SP_ASSERTION_CONSUMER_SERVICE=${URL_PREFIX}/acs \
    -e SIMPLESAMLPHP_SP_SINGLE_LOGOUT_SERVICE=${URL_PREFIX}/sls \
    -d kristophjunge/test-saml-idp

# EOF
