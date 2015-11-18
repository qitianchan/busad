from server.app.main import create_app
from threading import Thread
from server.app.utils.ws_listenning import wrap_listen

app = create_app()
if not app:
    try:
        # listen = Listening()
        ws_listening_thread = Thread(target=wrap_listen)
        ws_listening_thread.start()
    except Exception, e:
        print e.message
        raise e

app.run(debug=True)
