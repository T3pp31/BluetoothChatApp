import asyncio

import PySimpleGUI as sg
from bleak import discover

from src.receive import receive
from src.send import send


async def run():
    """
    Bluetoothデバイスを検索する
    Return
    ------
    devices_list: 検索したbluetoothデバイス
    """
    devices = await discover()
    return devices


# テーマの決定
sg.theme("DarkBlue")

layout = [
    [sg.Text("Bluetoothアドレスを検索します"), sg.Button("検索", key="search")],
    [
        sg.Text("送信したいアドレス"),
        sg.Input("Bluetoothアドレス", key="send_addr"),
        sg.Input("message", key="message"),
        sg.Button("送信", key="send"),
    ],
    [
        sg.Text("受信したいアドレス"),
        sg.Input("Bluetoothアドレス", key="receive_addr"),
        sg.Input("Bluetoothチャンネル", key="channel"),
        sg.Button("受信", key="receive"),
    ],
    [sg.Output(size=(40, 20))],
    [sg.Button("終了", key="exit")],
]

window = sg.Window("Bluetoothファイル送受信", layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "exit":
        break

    elif event == "search":
        loop = asyncio.get_event_loop()
        devices = loop.run_until_complete(run())
        print(devices)

    elif event == "send":
        data = send(values["send_addr"], values["message"])
        print(data)

    elif event == "receive":
        data = receive(values["receive_addr"], values["chanel"])
        print(data)

window.close()
