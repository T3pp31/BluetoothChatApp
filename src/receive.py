import socket


def receive(addr, channel):
    """
    Bluetooth経由でデータを受信する
    Parameters
    ----------
    addr: bluetooth address
    channel: channnel チャンネル番号

    return
    ------
    data: 受信データ
    """
    s = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
    )
    s.bind((addr, int(channel)))
    s.listen(1)
    print(f"チャンネル{channel}で受信待機中...")

    s_sock, address = s.accept()
    print(f"{address[0]}からのコネクトを許可")

    data = s_sock.recv(1024)

    s_sock.close()
    s.close()
    return data
