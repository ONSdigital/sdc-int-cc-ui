#!/bin/bash
#
# Run CCUI application locally
#
# Note: we set the port to 5001 to avoid conflicts with EQ flask endpoint (as expected by RHUI).
#

export FLASK_APP=application
export FLASK_ENV=development
[[ -z "$FLASK_RUN_PORT" ]] && export FLASK_RUN_PORT=5001

flask run

# EOF

