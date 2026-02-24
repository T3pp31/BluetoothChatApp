import socket


def send(addr, message):
    """
    Bluetooth経由でデータを送信する
    Parameters
    ----------
    addr: (bluetooth_address, channel) のタプル
    message: 送信したいメッセージ文字列
    """
    s = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
    )
    try:
        s.connect(addr)
        s.send(message.encode())
    finally:
        s.close()
