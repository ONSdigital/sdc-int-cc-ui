"""FLASK BASE CONFIG"""

JSONIFY_PRETTYPRINT_REGULAR = True

# Configure Redis for storing the session data on the server-side
SESSION_TYPE = 'redis'
SESSION_PERMANENT = True
SESSION_USE_SIGNER = True
SESSION_COOKIE_NAME = 'ons_cc'
PERMANENT_SESSION_LIFETIME = 2700
