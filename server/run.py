from server.app.main import create_app
from threading import Thread
from server.app.utils.ws_listenning import wrap_listen
from gevent.pywsgi import WSGIServer
app = create_app()
if not app:
    try:
        # listen = Listening()
        ws_listening_thread = Thread(target=wrap_listen)
        ws_listening_thread.start()
    except Exception, e:
        print e.message
        raise e

if __name__ == '__main__':
    WSGIServer(('', 5000), app.wsgi_app).serve_forever()
    # app.run(debug=True)
