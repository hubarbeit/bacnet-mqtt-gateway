from gateway import BacnetMqttGateway

def main():
    gateway = BacnetMqttGateway()
    print("done initialsing")
    print("starting loop")
    gateway.central_loop()

if __name__ == "__main__":
    main()
