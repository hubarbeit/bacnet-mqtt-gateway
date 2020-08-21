from gateway import BacnetMqttGateway

def main():
    gateway = BacnetMqttGateway()
    gateway.central_loop()

if __name__ == "__main__":
    main()
