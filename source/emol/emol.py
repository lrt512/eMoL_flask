"""Run eMoL in the Flask debug HTTP server."""
from emol.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
