# Contact Center UI

## Running locally

### Prerequisites

Various services are called by the CCUI and must be present for proper operation.
Many of the services will be started in your local docker desktop.

Services required:

- **local IDP** - a SAML IDP (Identity Provider) is required for login/logout by CCUI
- **redis** - this can be the same redis as is run for RHUI. Required directly by CCUI for sesssions.
- **PubSub** - this will typically be a dockerised pubsub emulator, required by CCSvc.
- **Mock Services** - this provides AIMS and RM case service emulation, required by CCUI and CCSvc.
- **Postgres** - database required by CCSvc
- **CC Service** - provides primary backend services called by CCUI
 
In addition, the PubSub will need appropriate topics and subscribers created.

See below for guidance on setting up the local IDP; for all other prerequisites,
see the help documentation and scripts in CCSvc and RHSvc code repositories.

### Starting up the local SAML IDP

An IDP (Identity Provider) is required for CCUI SAML login/logout. For running
locally it is convenient to run up a **SimpleSaml** docker instance, configured for port 8080. 

To do this run the following script:
```shell
scripts/local-idp.sh
```
This is configured with a handful of users with simple credentials, such as username="fred", password="pw".
You can see the user configuration in the _**scripts/simplesaml-config**_ directory.

To check the IDP is up and running you can navigate to http://localhost:8080/simplesaml .
If you wish to login as **admin** the password is **secret**.

By default, CCUI running locally will use the configuration in 
[saml/settings.json](saml/settings.json) which is configured to use the local IDP
started with the **local-idp.sh** script above.

For more information about the local IDP setup see the 
[IDP configuration README](scripts/simplesaml-config/README.md).


### Starting CCUI

To start in development mode, clone the git repo.

CCUI runs with <strong>Python 3.9</strong>. To install the required libraries, you can run
<pre>pip install -r requirements.txt</pre>

Once this is done you can run up a virtual environment (venv), and then use the following commands to start an instance of CCUI:
<pre>
$ make run
</pre>

When not run in production mode, CCUI has defaults for connecting to CCSvc, however you may need to set/modify environment variables for ‘CCSVC_URL’, ‘CCSVC_USERNAME’ and ‘CCSVC_PASSWORD’ to talk to you local CCSvc.

## SAML IDP configuration when running CCUI in GCP

The SAML IDP configuration is overridden in GCP environment in the following way:
- In the **cc-config** configmap, **saml-adfs** must be set to "True" for Azure IDP, or "False" otherwise
- A secret configuration **saml-settings** is used to hold the customised **settings.json**.

To view the **settings.json** run the following at the terminal:
```shell
kubectl get secret saml-settings -o json | jq -r '.data."settings.json"' | base64 -d
```

See:
https://github.com/ONSdigital/sdc-int-cc-terraform/tree/main/kubernetes/contact-centre/simple-idp/readme.txt
for the instructions for configuring and deploying a **simpleSaml IDP** in GCP for testing.


### A note about settings.json SAML configuration

The **settings.json** file configures the OneLogin SAML toolkit used by CCUI to talk to the correct IDP.
The settings file that CCUI uses will either be the local one (see above information
on running the local IDP), or the one in the **saml-settings** kubernetes secret (see above).

See https://github.com/onelogin/python3-saml for detailed information on **settings.json**.

In SAML terminology:
- SP = Service Provider (which in our case is the CCUI)
- IDP = Identity Provider (for example, our local simplesaml docker image, or Azure AD)

In the "sp" section of **settings.json** the follow items need configuring:
- **entityId** - _CCUI-base-URL_/saml/metadata
- **assertionConsumerService** "url" - _CCUI-base-URL_/saml/acs
- **singleLogoutService** "url" - _CCUI-base-URL_/saml/sls

where for the above _CCUI-base-URL_ is the base URL, for example:
- http://localhost:5001 for running locally
- https://cc-dev.int.gcp.onsdigital.uk for running in DEV environment

In the "idp" section of **settings,json** the following items need configuring:
- **entityId** - the IDP entity ID
- **singleSignOnService** "url" - the IDP sign-on URL
- **singleLogoutService** "url" - the IDP logout URL
- **x509cert** - the IDP x509 certificate - one long string with no spaces.

In order to format an x509 certifcate in one long string, it may be convenient to
use the online converter at the useful webpage: 
https://developers.onelogin.com/saml/online-tools/x509-certs/format-x509-certificate .


## ONS Design System

See https://ons-design-system.netlify.app/ .

The required version of the design system is now loaded automatically via the 'Make run' command. If you wish to load it manually, you can run scripts > load_templates.sh to pull down the appropriate version of the Design System (DS).

To run a different instance of the Design System, update the 'DESIGN_SYSTEM_VERSION' in scripts > load_templates.sh

## Secret Key Generation
A secret_key must be generated for CCUI for each environment and stored in GCP as a secret. A proforma secret is available in the sdc-int-cc-terraform repo. When running locally, a dummy default key is set in the config.

A key can be generated by running the following python code
<pre>$ python -c 'import secrets; print(secrets.token_hex())'</pre>
or from a python terminal as 
<pre>import secrets; print(secrets.token_hex())</pre>

