"""
Read BLE data to InfluxDB
-------------

"""

import asyncio
import sys
import time

from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# All BLE devices have MTU of at least 23. Subtracting 3 bytes overhead, we can
# safely send 20 bytes at a time to any device supporting this service.
UART_SAFE_SIZE = 20

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "tqt7SJtMFLrTqETqc3ko1Yszj7cWkYYvLaHx-_xkLYqF1jUwsqednuEzvGUJRNUQN7edhA6Mx_Goo0zVrYS_cA=="
org = "Aplicaciones en Informática Avanzada"
bucket = "samva"

client = InfluxDBClient(url="http://localhost:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

# flush table
delete_api = client.delete_api()
delete_api.delete('1970-01-01T00:00:00Z', '2022-04-27T00:00:00Z', '_measurement="mem"', bucket=bucket, org=org)


def process(data):
    ms = time.time_ns() // 1_000_000
    dd = data[:-1].decode('utf-8').split()
    dd.append(str(ms))
    sequence = ["mem,host=host1 " + dd[0] + str(i) + "=" + dd[i + 1] for i in range(4)]
    print(dd)
    write_api.write(bucket, org, sequence)


async def uart_terminal():
    """This is a simple "terminal" program that uses the Nordic Semiconductor
    (nRF) UART service. It reads from stdin and sends each line of data to the
    remote device. Any data received from the device is printed to stdout.
    """

    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the UART service UUID in the
        # advertising data. This test may need to be adjusted depending on the
        # actual advertising data supplied by the device.
        if UART_SERVICE_UUID.lower() in adv.service_uuids:
            return True

        return False

    device = await BleakScanner.find_device_by_filter(match_nus_uuid)
    print(device)

    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(_: int, data: bytearray):
        process(data)

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)

        print("Connected, sending data to InfluxDB...")

        loop = asyncio.get_running_loop()

        while True:
            # This waits until you type a line and press ENTER.
            # A real terminal program might put stdin in raw mode so that things
            # like CTRL+C get passed to the remote device.
            # data = await loop.run_in_executor(None, sys.stdin.buffer.readline)

            # print(data)
            data = b'a'
            # sleep(1)

            # data will be empty on EOF (e.g. CTRL+D on *nix)
            if not data:
                break

            # some devices, like devices running MicroPython, expect Windows
            # line endings (uncomment line below if needed)
            # data = data.replace(b"\n", b"\r\n")

            await client.write_gatt_char(UART_RX_CHAR_UUID, data)
            # print("sent:", data)


if __name__ == "__main__":
    try:
        asyncio.run(uart_terminal())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass
