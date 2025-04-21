import argparse
import json
from mqtt_helper import MqttHelper

# Keep track of the list of devices that have already been published to or received from.
devices_published_to = []
devices_received_from = []
devices_info = []


def on_connect(mqtt):
    """
    Callback function for MQTT connection.
    Subscribes to necessary topics.
    """
    mqtt.subscribe('6718874bc1628f9b0dcd1ee7/+/connected', qos=2)
    mqtt.subscribe('6718874bc1628f9b0dcd1ee7/+/aboutdevice/response', qos=2)


def on_message(mqtt, topic, message):
    """
    Callback function for handling incoming MQTT messages.
    Processes messages based on the topic structure.
    """
    topic_split = topic.split('/')
    if len(topic_split) < 3:
        return  # Invalid topic structure, ignore

    company_code, serial_number = topic_split[0], topic_split[1]

    if len(topic_split) == 3 and topic_split[2] == 'connected':
        handle_connected_topic(mqtt, company_code, serial_number)
    elif len(topic_split) == 4 and topic_split[2] == 'aboutdevice' and topic_split[3] == 'response':
        handle_aboutdevice_response(serial_number, message)


def handle_connected_topic(mqtt, company_code, serial_number):
    """
    Handles the 'connected' topic.
    Publishes a request to the 'aboutdevice' topic if the device is not already published to.
    """
    if serial_number not in devices_published_to:
        devices_published_to.append(serial_number)
        mqtt.publish(f'{company_code}/{serial_number}/aboutdevice/request', payload='', qos=2)


def handle_aboutdevice_response(serial_number, message):
    """
    Handles the 'aboutdevice/response' topic.
    Parses the message and updates the devices_info list.
    """
    if serial_number not in devices_received_from:
        devices_received_from.append(serial_number)
        try:
            users = json.loads(message).get("users", [])
            devices_info.append({"serial_number": serial_number, "users": users})
        except json.JSONDecodeError:
            print(f"Failed to decode JSON message: {message}")


def parse_arguments():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="MQTT Device Manager")
    parser.add_argument(
        '-pf', '--product-flavor', required=True, help='The product flavor'
    )
    return parser.parse_args()


def main():
    """
    Main entry point of the script.
    Initializes the MQTT helper with the appropriate callbacks.
    """
    args = parse_arguments()
    MqttHelper(
        on_connect_callback=on_connect,
        product_flavor=args.product_flavor,
        on_message_callback=on_message
    )


if __name__ == '__main__':
    main()