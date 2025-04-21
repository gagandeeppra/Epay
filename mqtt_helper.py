#!/usr/bin/env python3

import json
import ssl
import sys
import paho.mqtt.client as mqtt
from paho.mqtt.client import error_string


class MqttHelper:
    def __init__(
        self,
        serial_number=None,
        company_code=None,
        product_flavor=None,
        on_company_code_callback=None,
        on_connect_callback=None,
        on_disconnect_callback=None,
        on_subscribe_callback=None,
        on_publish_callback=None,
        on_message_callback=None,
    ):
        self.serial_number = serial_number
        self.company_code = company_code
        self.product_flavor = product_flavor.upper() if product_flavor else None
        self.on_company_code_callback = on_company_code_callback
        self.on_connect_callback = on_connect_callback
        self.on_disconnect_callback = on_disconnect_callback
        self.on_subscribe_callback = on_subscribe_callback
        self.on_publish_callback = on_publish_callback
        self.on_message_callback = on_message_callback

        self.mqtt_client = mqtt.Client()
        self._initialize_mqtt_callbacks()

        print("Connecting")
        self._setup_tls_and_connect()
        self._start_loop()

    def _initialize_mqtt_callbacks(self):
        """Initialize MQTT client callbacks."""
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_publish = self.on_publish
        self.mqtt_client.on_message = self.on_message

    def _setup_tls_and_connect(self):
        """Set up TLS and connect to the MQTT broker."""
        if self.product_flavor == "EPAY":
            self.mqtt_client.tls_set(
                ca_certs="certificate/epay_intermediate_certificate_authority.cer",
                certfile="certificate/client/epay_client_certificate.cer",
                keyfile="certificate/client/epay_client_certificate.key",
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None,
            )
            self.mqtt_client.connect("mqttbroker.sekureid.com", 8883, 60)

    def _start_loop(self):
        """Start the MQTT client loop."""
        try:
            self.mqtt_client.loop_start()
            input("Press Enter to exit...\n")
        finally:
            self.disconnect()
            sys.exit(0)

    def on_connect(self, mqtt_client):
        """Handle MQTT connection."""
        print("Connected")
        if self.on_connect_callback:
            self.on_connect_callback(self)

        if self.serial_number and self.on_company_code_callback:
            mqtt_client.subscribe(f"+/{self.serial_number}/connected", qos=2)
            print("Subscribed to connected topic")

    def on_disconnect(self, rc):
        """Handle MQTT disconnection."""
        if self.on_disconnect_callback:
            self.on_disconnect_callback()
        elif rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"Disconnected with result code: {error_string(rc)}")

    def on_subscribe(self,  message_id):
        """Handle MQTT subscription acknowledgment."""
        if self.on_subscribe_callback:
            self.on_subscribe_callback(self, message_id)

    def on_publish(self, message_id):
        """Handle MQTT publish acknowledgment."""
        if self.on_publish_callback:
            self.on_publish_callback(self, message_id)

    def on_message(self, message):
        """Handle incoming MQTT messages."""
        payload = message.payload.decode("utf-8")
        topic_parts = message.topic.split("/")

        if len(topic_parts) == 3 and topic_parts[1] == self.serial_number and topic_parts[2] == "connected":
            self.company_code = topic_parts[0]
            if self.on_company_code_callback:
                self.on_company_code_callback(self, self.company_code, self.serial_number)
            elif self.on_message_callback:
                self.on_message_callback(self, message.topic, payload)
        elif self.on_message_callback:
            self.on_message_callback(self, message.topic, payload)
        else:
            self._handle_unexpected_message(message, payload)

    def _handle_unexpected_message(self, message, payload):
        """Handle unexpected MQTT messages."""
        try:
            json_object = json.loads(payload)
            print(f"Received: {message.topic}:\n{json.dumps(json_object, indent=2)}")
        except ValueError:
            print(f"Received: {message.topic}:\n{payload}")
        self.mqtt_client.disconnect()

    def subscribe(self, topic, quality_of_service=2):
        """Subscribe to an MQTT topic."""
        self.mqtt_client.subscribe(topic, quality_of_service)
        print(f"Subscribed to: {topic}")

    def publish(self, topic, message, quality_of_service):
        """Publish a message to an MQTT topic."""
        message_info = self.mqtt_client.publish(topic, message, quality_of_service)
        if not message_info.is_published:
            message_info.wait_for_publish()
        print(f"Published: {topic}: {message}")

    def disconnect(self):
        """Disconnect the MQTT client."""
        self.mqtt_client.disconnect()

    def get_company_code(self):
        """Get the company code."""
        return self.company_code