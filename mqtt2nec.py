#!/usr/bin/env python
import json
import traceback
import argparse
import csv

import serial.tools.list_ports
import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser(description='mqtt2nec')
parser.add_argument("hostname", help="broker hostname")
parser.add_argument('--port', dest="port", type=int, default=1883, help='broker port (default: %(default)s)')
parser.add_argument('--username', '-u', dest='username', help='broker username')
parser.add_argument('--password', '-p', dest='password', help='broker password')
parser.add_argument('--topic', '-t', dest='topic', default='nec/tx',
                    help='broker topic to subscribe to (default: %(default)s)')
parser.add_argument('--aliases', '-a', dest='aliases', type=argparse.FileType('r'), default=None)
args = parser.parse_args()

aliases = {}

if args.aliases:
    aliases = dict((a, b) for (a, b) in csv.reader(args.aliases))


def find_arduino():
    ports = list(serial.tools.list_ports.comports())
    port = None
    for p in ports:
        if p.manufacturer and "Arduino" in p.manufacturer:
            port = p

    if not port:
        raise Exception("Arduino not found")
    device = serial.Serial(port=port.device, baudrate=115200, timeout=.1)
    device.close()
    device.open()
    return device


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected (Code 0)")
        client.subscribe(args.topic)
        return
    elif rc == 1:
        raise Exception("Connection refused (Code 1) – incorrect protocol version")
    elif rc == 2:
        raise Exception("Connection refused (Code 2) – invalid client identifier")
    elif rc == 3:
        raise Exception("Connection refused (Code 3) – server unavailable")
    elif rc == 4:
        raise Exception("Connection refused (Code 4) – bad username or password")
    elif rc == 5:
        raise Exception("Connection refused (Code 5) – not authorised")
    raise Exception(f"Connection refused (Code {rc}) – unknown error code")


def get_codes(codes):
    for code in codes:
        if code in aliases:
            hex_code = aliases[code]
        else:
            hex_code = code
        yield str(int(hex_code, 16))


def on_message(message, arduino):
    try:
        print("message received ", str(message.payload.decode("utf-8")))
        payload = json.loads(message.payload)
        codes = payload["codes"]
        integer_codes = ";".join(get_codes(codes))
        arduino.write(bytes(integer_codes, 'utf-8'))
    except:
        traceback.print_exc()


def create_mqtt_client(arduino):
    client = mqtt.Client(client_id="mqtt2nec")
    client.on_message = lambda c, userdata, message: on_message(message, arduino)
    client.on_connect = on_connect
    if args.username or args.password:
        client.username_pw_set(username=args.username, password=args.password)
    client.connect(args.hostname, port=args.port, keepalive=60, bind_address="")
    return client


def main():
    arduino = find_arduino()
    mqtt_client = create_mqtt_client(arduino)
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        pass
    finally:
        arduino.close()


if __name__ == "__main__":
    main()
