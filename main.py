import asyncio
import threading
from datetime import datetime

import PySimpleGUI as sg

from src.receive import receive_loop
from src.search import run as search_run
from src.send import send

# --- グローバル状態 ---
receive_stop_event = threading.Event()
receive_thread = None
# 検索結果を保持: [{address, name}, ...]
found_devices = []

# --- ヘルパー関数 ---


def timestamp():
    return datetime.now().strftime("%H:%M:%S")


def append_chat(window, text):
    window["chat_log"].print(text)


# --- バックグラウンドスレッド関数 ---


def search_thread_func(window):
    try:
        loop = asyncio.new_event_loop()
        devices = loop.run_until_complete(search_run())
        loop.close()
        window.write_event_value("_SEARCH_DONE_", devices)
    except Exception as e:
        window.write_event_value("_SEARCH_DONE_", f"ERROR:{e}")


def send_thread_func(window, addr, channel, message):
    try:
        send((addr, int(channel)), message)
        window.write_event_value("_SEND_DONE_", message)
    except Exception as e:
        window.write_event_value("_SEND_ERROR_", str(e))


def receive_thread_func(window, addr, channel, stop_event):
    def on_received(data, remote_addr):
        window.write_event_value("_RECEIVED_", (data, remote_addr))

    try:
        receive_loop(addr, channel, on_received, stop_event)
    except Exception as e:
        window.write_event_value("_RECEIVE_ERROR_", str(e))


# --- GUI レイアウト ---

sg.theme("DarkBlue")

search_section = [
    [sg.Text("=== デバイス検索 ===", font=("", 11, "bold"))],
    [sg.Button("検索", key="search")],
    [
        sg.Listbox(
            values=[],
            size=(50, 5),
            key="device_list",
            enable_events=True,
            horizontal_scroll=True,
        )
    ],
]

chat_section = [
    [sg.Text("=== チャット ===", font=("", 11, "bold"))],
    [
        sg.Text("接続先アドレス:"),
        sg.Input("", key="addr", size=(25, 1)),
        sg.Text("チャンネル:"),
        sg.Input("1", key="channel", size=(5, 1)),
    ],
    [
        sg.Button("受信開始", key="start_receive"),
        sg.Button("受信停止", key="stop_receive", disabled=True),
        sg.Text("", key="receive_status", size=(20, 1)),
    ],
    [
        sg.Multiline(
            size=(55, 15),
            key="chat_log",
            disabled=True,
            autoscroll=True,
            font=("Courier", 10),
        )
    ],
    [
        sg.Input("", key="message", size=(45, 1), enable_events=True),
        sg.Button("送信", key="send"),
    ],
]

layout = search_section + [sg.HorizontalSeparator()] + chat_section + [[sg.Button("終了", key="exit")]]

window = sg.Window("Bluetooth チャット", layout, finalize=True)

# Enter キーで送信
window["message"].bind("<Return>", "_ENTER")

# --- イベントループ ---

while True:
    event, values = window.read(timeout=200)

    if event == sg.WIN_CLOSED or event == "exit":
        receive_stop_event.set()
        break

    # --- 検索 ---
    elif event == "search":
        window["search"].update(disabled=True)
        append_chat(window, f"[{timestamp()}] デバイスを検索中...")
        t = threading.Thread(target=search_thread_func, args=(window,), daemon=True)
        t.start()

    elif event == "_SEARCH_DONE_":
        window["search"].update(disabled=False)
        result = values[event]
        if isinstance(result, str) and result.startswith("ERROR:"):
            append_chat(window, f"[{timestamp()}] 検索エラー: {result[6:]}")
        else:
            found_devices = result
            display_list = [f"{addr} - {name}" for addr, name in found_devices]
            window["device_list"].update(values=display_list)
            append_chat(
                window,
                f"[{timestamp()}] {len(found_devices)} 台のデバイスが見つかりました",
            )

    # --- デバイス選択 ---
    elif event == "device_list":
        selected = values["device_list"]
        if selected:
            # "XX:XX:XX:XX:XX:XX - DeviceName" からアドレス部分を取得
            addr_str = selected[0].split(" - ")[0]
            window["addr"].update(addr_str)

    # --- 受信開始 ---
    elif event == "start_receive":
        addr = values["addr"].strip()
        channel = values["channel"].strip()
        if not addr or not channel:
            append_chat(window, f"[{timestamp()}] アドレスとチャンネルを入力してください")
            continue

        receive_stop_event.clear()
        receive_thread = threading.Thread(
            target=receive_thread_func,
            args=(window, addr, channel, receive_stop_event),
            daemon=True,
        )
        receive_thread.start()
        window["start_receive"].update(disabled=True)
        window["stop_receive"].update(disabled=False)
        window["receive_status"].update("受信待機中...")
        append_chat(
            window,
            f"[{timestamp()}] チャンネル{channel}で受信待機を開始しました",
        )

    # --- 受信停止 ---
    elif event == "stop_receive":
        receive_stop_event.set()
        window["start_receive"].update(disabled=False)
        window["stop_receive"].update(disabled=True)
        window["receive_status"].update("")
        append_chat(window, f"[{timestamp()}] 受信待機を停止しました")

    # --- 受信データ ---
    elif event == "_RECEIVED_":
        data, remote_addr = values[event]
        append_chat(window, f"[{timestamp()}] {remote_addr}: {data}")

    elif event == "_RECEIVE_ERROR_":
        append_chat(window, f"[{timestamp()}] 受信エラー: {values[event]}")
        window["start_receive"].update(disabled=False)
        window["stop_receive"].update(disabled=True)
        window["receive_status"].update("")

    # --- 送信 ---
    elif event == "send" or event == "message_ENTER":
        addr = values["addr"].strip()
        channel = values["channel"].strip()
        message = values["message"].strip()
        if not addr or not channel or not message:
            continue
        window["message"].update("")
        append_chat(window, f"[{timestamp()}] 自分: {message}")
        t = threading.Thread(
            target=send_thread_func,
            args=(window, addr, channel, message),
            daemon=True,
        )
        t.start()

    elif event == "_SEND_DONE_":
        pass  # チャットログへの追加は送信時に済み

    elif event == "_SEND_ERROR_":
        append_chat(window, f"[{timestamp()}] 送信エラー: {values[event]}")

window.close()
