import socket


def send(addr, message):
    """
    Bluetooth経由でデータを送信する
    Parameters
    ----------
    addr:bluetooth address
    message: message 送信したいメッセージ
    """
    s = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTRPROTO_RFCOMM
    )
    s.connect(addr)

    s.send(message.encode())
    data = s.recv(1024).decode()
    print(f"受信したメッセージ:{data}")
