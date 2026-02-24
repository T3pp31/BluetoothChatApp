import socket


def receive_loop(addr, channel, callback, stop_event):
    """
    Bluetooth経由でデータを連続受信する（バックグラウンドスレッド用）

    Parameters
    ----------
    addr: 自分の bluetooth address
    channel: チャンネル番号
    callback: callback(data_str, remote_addr) — 受信時に呼ばれる関数
    stop_event: threading.Event — set() されたらループ終了
    """
    s = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
    )
    try:
        s.bind((addr, int(channel)))
        s.listen(1)
        s.settimeout(1.0)

        while not stop_event.is_set():
            try:
                client_sock, address = s.accept()
            except socket.timeout:
                continue

            try:
                client_sock.settimeout(1.0)
                while not stop_event.is_set():
                    try:
                        data = client_sock.recv(1024)
                        if not data:
                            break
                        callback(data.decode(errors="replace"), address[0])
                    except socket.timeout:
                        continue
            finally:
                client_sock.close()
    finally:
        s.close()
