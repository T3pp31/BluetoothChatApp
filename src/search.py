# 周囲のBluetoothデバイスを検索する

import asyncio

from bleak import discover


async def run():
    """
    Bluetoothデバイスを検索する
    Return
    ------
    devices_list: 検索したbluetoothデバイス
    """
    devices = await discover()
    return devices


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(run())
    print(devices)
