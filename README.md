Placeholder for SDC Integrations Contact Center UI Readme

<h2>To run locally</h2>

<h3>Run via docker</h3>

To be implemented.

<h3>Manually</h3>

To run CCUI locally you will need a running instance of redis. This can be the same redis as is run for RHUI.

To start in development mode, first clone the git repo, then run scripts > load_templates.sh to pull down the appropriate version of the Design System (DS). You should do this each time that you pull a code update.

Once this is done you can run up a virtual environment (venv), and then use the following commands to start an instance of CCUI:
<pre>
$ export FLASK_APP=app
$ export FLASK_ENV=development
$ flask run
</pre>

When run in development mode, CCUI has defaults for connecting to CCSvc, however you may need to set environment variables for ‘CCSVC_URL’, ‘CCSVC_USERNAME’ and ‘CCSVC_PASSWORD’ to talk to you local CCSvc.

<h2>Secret Key Generation</h2>
A secret_key must be generated for each instance of CCUI and stored in GCP as a secret. A proforma secret is available in the sdc-int-cc-terraform repo. When running locally, a dummy default key is set in the config.

A key can be generated by running the following python code
<pre>$ python -c 'import secrets; print(secrets.token_hex())'</pre>
or from a python terminal as 
<pre>import secrets; print(secrets.token_hex())</pre>

