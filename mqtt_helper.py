#!/usr/bin/env python3

import json
import ssl
import sys

import paho.mqtt.client as mqtt
from paho.mqtt.client import error_string

class MqttHelper:

    def __init__(self, serial_number=None, company_code=None, product_flavor= None, on_company_code_callback=None, on_connect_callback=None, on_disconnect_callback=None, on_subscribe_callback=None, on_publish_callback=None, on_message_callback=None):
        self.serial_number = serial_number
        self.company_code = company_code
        self.product_flavor = product_flavor.upper()
        self.on_company_code_callback = on_company_code_callback
        self.on_connect_callback = on_connect_callback
        self.on_disconnect_callback = on_disconnect_callback
        self.on_subscribe_callback = on_subscribe_callback
        self.on_publish_callback = on_publish_callback
        self.on_message_callback = on_message_callback
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_publish = self.on_publish
        self.mqtt_client.on_message = self.on_message
        print('Connecting')

        # Epay.
        if self.product_flavor == 'EPAY':
            self.mqtt_client.tls_set(ca_certs='epay/epay_intermediate_certificate_authority.cer', certfile='epay/client/epay_client_certificate.cer', keyfile='epay/client/epay_client_certificate.key', cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
            self.mqtt_client.connect('mqttbroker.sekureid.com', 8883, 60)

        # Loop indefinitely until the user presses the 'enter' button.
        try:
            self.mqtt_client.loop_start()
            input()
        finally:
            self.mqtt_client.disconnect()
            sys.exit(0)

    def on_connect(self, mqtt_client, userdata, flags, rc):
        print('Connected')
        if self.on_connect_callback:
            self.on_connect_callback(self)

        if self.serial_number != '' and self.on_company_code_callback:
            mqtt_client.subscribe(f'+/{self.serial_number}/connected', 2)
            print('Subscribed')

    def on_disconnect(self, mqtt_client, userdata, rc):
        if self.on_disconnect_callback:
            self.on_disconnect_callback()
        elif rc != mqtt.MQTT_ERR_SUCCESS:
            print(f'Disconnected with result code: {error_string(rc)}')

    def on_subscribe(self, mqtt_client, userdata, message_id, granted_qos, properties=None):
        if self.on_subscribe_callback:
            self.on_subscribe_callback(self, message_id)

    def on_publish(self, mqtt_client, userdata, message_id):
        if self.on_publish_callback:
            self.on_publish_callback(self, message_id)

    def on_message(self, mqtt_client, userdata, message):
        payload = str(message.payload, 'utf-8')
        # print(f'Received: {message.topic}: {payload}')

        split = message.topic.split('/')
        if len(split) == 3 and split[1] == self.serial_number and split[2] == 'connected':
            self.company_code = split[0]
            # print(f'Company code: {company_code}')

            if self.on_company_code_callback:
                self.on_company_code_callback(self, self.company_code, self.serial_number)
            elif self.on_message_callback:
                self.on_message_callback(self, message.topic, payload)
        elif self.on_message_callback:
            self.on_message_callback(self, message.topic, payload)
        else:
            try:
                json_object = json.loads(payload)
                print(f'Received: {message.topic}:\n{json.dumps(json_object, indent=2)}')
            except ValueError:
                print(f'Received: {message.topic}:\n{payload}')
            mqtt_client.disconnect()

    def subscribe(self, topic, quality_of_service=2):
        self.mqtt_client.subscribe(topic, quality_of_service)
        print(f'Subscribed: {topic}')

    def publish(self, topic, message, quality_of_service):
        message_info = self.mqtt_client.publish(topic, message, quality_of_service)
        if not message_info.is_published:
            message_info.wait_for_publish()
        print(f'Published: {topic}: {message}')

    def disconnect(self):
        self.mqtt_client.disconnect()

    def get_company_code(self):
        return self.company_code
