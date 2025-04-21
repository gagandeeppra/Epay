import argparse
import json

from mqtt_helper import MqttHelper

# Keep track of the list of devices that have already been published to or received from.
devices_published_to = []
devices_received_from = []


def on_connect(mqtt):
    mqtt.subscribe('6718874bc1628f9b0dcd1ee7/+/connected', 2)
    mqtt.subscribe('6718874bc1628f9b0dcd1ee7/+/aboutdevice/response', 2)


def on_message(mqtt, topic, message):
    # Split the topic into its components
    topic_split = topic.split('/')
    company_code = topic_split[0]
    serial_number = topic_split[1]

    if len(topic_split) == 3 and topic_split[2] == 'connected' and serial_number not in devices_published_to:
        devices_published_to.append(serial_number)
        mqtt.publish(f'{company_code}/{serial_number}/aboutdevice/request', '', 2)

    elif len(topic_split) == 4 and topic_split[2] == 'aboutdevice' and topic_split[3] == 'response' and serial_number not in devices_received_from:
        devices_received_from.append(serial_number)
        users = json.loads(message).get("users")
        print(f'{serial_number}: {users}')


if __name__ == '__main__':
    # Parse the command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-pf', '--product-flavor', required=True, help='The product flavor')
    args = parser.parse_args()
    MqttHelper(on_connect_callback=on_connect, product_flavor=args.product_flavor, on_message_callback=on_message)
