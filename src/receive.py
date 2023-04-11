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
    s.connect((addr, channel))
    s_sock, address = s.accept()
    print(f"{addr}からのコネクトを許可")

    data = s_sock.recv(1024)

    s.close()
    return data
