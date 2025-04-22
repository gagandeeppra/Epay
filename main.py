import argparse
import json
import csv
from mqtt_helper import MqttHelper

# Keep track of the list of devices that have already been published to or received from.
devices_published_to = []
devices_received_from = []
devices_info = []

def write_csv():
    with open('eggs.csv', 'w', newline='') as csvfile:
        fieldnames = ['first_name', 'last_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for device_info in devices_info:
            writer.writerow({"serial_number": device_info['serial_number'], "user_count": device_info['users']})
        
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
        devices_info.append({"serial_number": serial_number, "user_count": users})


if __name__ == '__main__':
    # Parse the command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-pf', '--product-flavor', required=True, help='The product flavor')
    args = parser.parse_args()
    MqttHelper(on_connect_callback=on_connect, product_flavor=args.product_flavor, on_message_callback=on_message)
