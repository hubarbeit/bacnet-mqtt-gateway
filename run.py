from bacnet_mqtt_gateway.gateway import BacnetMqttGateway

def main():
    gateway = BacnetMqttGateway
    gateway.central_loop()
