"""Run eMoL in the Flask debug HTTP server."""
from emol.app import create_app

create_app().run(debug=True, host='0.0.0.0', threaded=True)
