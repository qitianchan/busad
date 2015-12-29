# from gevent.monkey import patch_all; patch_all()
from server.app.main import create_app
from gevent.pywsgi import WSGIServer
app = create_app()

if __name__ == '__main__':
    WSGIServer(('', 5000), app).serve_forever()
    # app.run(debug=True)
