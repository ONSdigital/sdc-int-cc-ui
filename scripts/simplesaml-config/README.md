# Local IDP ("simplesaml") configuration

This directory contains files to customise the default docker image to bring up a local IDP 
in docker for SAML login with CCUI running locally.

- **saml20-idp-hosted.php**	- customised configuration to make the _NameId_ be the _emailaddress_
- **users.php**			- customised users

See the following links for more information:

- https://hub.docker.com/r/kristophjunge/test-saml-idp/
- https://stackoverflow.com/questions/50260272/how-to-replace-a-value-of-nameid-with-attribute-in-simplesamlphp-based-idp

