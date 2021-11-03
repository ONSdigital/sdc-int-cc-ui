Placeholder for SDC Integrations Contact Center UI Readme

<h2>To run locally</h2>

<h3>Run via docker</h3>

To be implemented.

<h3>Manually</h3>
To run CCUI locally you will need a running instance of redis. This can be the same redis as is run for RHUI.

To start in development mode, clone the git repo.

CCUI runs with <strong>Python 3.9</strong>. To install the required libraries, you can run
<pre>pip install -r requirements.txt</pre>

Once this is done you can run up a virtual environment (venv), and then use the following commands to start an instance of CCUI:
<pre>
$ make run
</pre>

Depending on your local set-up, you may also need to be running CCSvc and/or the AIMS mock service.

When not run in production mode, CCUI has defaults for connecting to CCSvc, however you may need to set/modify environment variables for ‘CCSVC_URL’, ‘CCSVC_USERNAME’ and ‘CCSVC_PASSWORD’ to talk to you local CCSvc.

<h2>ONS Design System</h2>

<a href="https://ons-design-system.netlify.app/">https://ons-design-system.netlify.app/

The required version of the design system is now loaded automatically via the 'Make run' command. If you wish to load it manually, you can run scripts > load_templates.sh to pull down the appropriate version of the Design System (DS).

To run a different instance of the Design System, update the 'DESIGN_SYSTEM_VERSION' in scripts > load_templates.sh


<h2>Secret Key Generation</h2>
A secret_key must be generated for CCUI for each environment and stored in GCP as a secret. A proforma secret is available in the sdc-int-cc-terraform repo. When running locally, a dummy default key is set in the config.

A key can be generated by running the following python code
<pre>$ python -c 'import secrets; print(secrets.token_hex())'</pre>
or from a python terminal as 
<pre>import secrets; print(secrets.token_hex())</pre>

