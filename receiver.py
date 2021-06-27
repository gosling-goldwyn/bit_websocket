import socketio
import time
from datetime import datetime


class MyCustomNamespace(socketio.ClientNamespace):  # 名前空間を設定するクラス
    def __init__(self, path, sio, host) -> None:
        super().__init__()
        self.path = path
        self.sio = sio
        self.host = host

    def on_connect(self):
        print('[{}] connect'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.sio.emit('subscribe', "lightning_executions_BTC_JPY",
                      namespace=self.path)

    def on_disconnect(self):
        print('[{}] disconnect'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        time.sleep(5)

    def on_lightning_executions_BTC_JPY(self, msg):
        print('[{}] response : {}'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))


class SocketIOClient:

    def __init__(self, host, path):
        self.host = host
        self.path = path
        self.sio = socketio.Client()

    def connect(self):
        self.sio.register_namespace(MyCustomNamespace(
            self.path, self.sio, self.host))  # 名前空間を設定
        self.sio.connect(self.host, transports=['websocket'])  # サーバーに接続
        self.sio.wait()  # イベントが待ち


if __name__ == '__main__':
    # SocketIOClientクラスをインスタンス化
    sio_client = SocketIOClient('https://io.lightstream.bitflyer.com', '/')
    sio_client.connect()
