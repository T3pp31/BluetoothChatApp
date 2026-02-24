# 周囲のBluetoothデバイスを検索する

import asyncio

from bleak import discover


async def run():
    """
    Bluetoothデバイスを検索する
    Return
    ------
    devices_list: [(address, name), ...] 形式のリスト
    """
    devices = await discover()
    return [(d.address, d.name or "Unknown") for d in devices]


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(run())
    for addr, name in devices:
        print(f"{addr} - {name}")
