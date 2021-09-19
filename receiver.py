import socketio
import time
from datetime import datetime
from datetime import timezone
import json
import tweepy


with open('pw.txt', mode='r') as f:
    pw = f.readlines()

Consumer_key, Consumer_secret, Access_token, Access_secret = [
    e.replace('\n', '') for e in pw]

# Twitterオブジェクトの生成
auth = tweepy.OAuthHandler(Consumer_key, Consumer_secret)
auth.set_access_token(Access_token, Access_secret)
api = tweepy.API(auth)


class MyCustomNamespace(socketio.ClientNamespace):
    def __init__(self, path, sio, host) -> None:
        super().__init__()
        self.path = path
        self.sio = sio
        self.host = host
        self.last_tweeted = datetime.now(timezone.utc)

    def on_connect(self):
        print('[{}] connect'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.sio.emit('subscribe', "lightning_executions_BTC_JPY",
                      namespace=self.path)

    def on_disconnect(self):
        print('[{}] disconnect'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def on_lightning_executions_BTC_JPY(self, msg):
        print('[{}] response : {}'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))
        # li = json.loads(msg.replace('\'','\"'))
        li = msg

        for e in li:
            rawdate = e['exec_date'].replace(
                e['exec_date'][e['exec_date'].find('.'):], '+00:00').replace(' ', '')
            gottendate = datetime.fromisoformat(rawdate)
            delta = gottendate - self.last_tweeted
            if delta.seconds >= 300:
                body = 'BTC now price: '+str(e['price'])+'JPY.'
                api.update_status(body)
                self.last_tweeted = gottendate


class SocketIOClient:

    def __init__(self, host, path):
        self.host = host
        self.path = path
        self.sio = socketio.Client()

    def connect(self):
        self.sio.register_namespace(MyCustomNamespace(
            self.path, self.sio, self.host))
        # transports設定しないとwebsocket通信にならない
        self.sio.connect(self.host, transports=['websocket'])
        self.sio.wait()


if __name__ == '__main__':
    sio_client = SocketIOClient('https://io.lightstream.bitflyer.com', '/')
    sio_client.connect()
