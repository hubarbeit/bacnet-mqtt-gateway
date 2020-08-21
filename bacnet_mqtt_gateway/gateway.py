import time
import json

import BAC0
import paho.mqtt.client as mqtt

from helpers import get_topic, load_yaml_with_includes


class BacnetRegister:
#    register: str
#    writable: boolean

    def __init__(self, device, id, name, register, component, unit_of_measurement, device_class, writable):
        super().__init__()
        self.register = register
        self.id = id
        self.name = name
        self.component = component
        self.unit_of_measurement = unit_of_measurement
        self.writable = writable
        self.device = device
        self.device_class = device_class
        self.value_read = False
        self.previous_value = None
        if self.writable:
            self.device.mqtt.subscribe(get_topic(self, "set"))

        self.send_config()

    def read(self, only_on_change=True):
        try:
            value = self.device.device[self.register].value
        except BAC0.core.io.IOExceptions.NoResponseFromController:
            self.device.connect()

        if not only_on_change or (
            not self.value_read or self.previous_value != value
        ):
            self.value_read = True
            self.previous_value = value
            self.device.mqtt.publish(get_topic(self, "state"), value, retain=True)

        return value

    def write(self, value):
        if not self.writable:
            return False
        if self.unit_of_measurement == "boolean":
            value = str(value)
        self.device.device[self.register] = value
        self.previous_value = value
        return self.read(only_on_change=False)

    def get_name(self):
        return f"{self.device.name}: {self.name}"

    def send_config(self):
        config = {
            "name": self.get_name(),
            "state_topic": get_topic(self, "state"),
            "unique_id": f"{self.device.id}-{self.id}"
        }
        if self.component == "sensor":
            if self.device_class:
                config["device_class"] = self.device_class
            config["unit_of_measurement"] = self.unit_of_measurement
        if self.writable:
            config["command_topic"] = get_topic(self, "set")
        if self.unit_of_measurement == "boolean":
            config["payload_on"] = "active"
            config["payload_off"] = "inactive"
        self.device.mqtt.publish(get_topic(self, "config"), json.dumps(config), retain=True)



class BacnetDevice:
#    address: str
#    device_id: int
#    registers: Dict[BacnetRegister]

    def __init__(self, gateway, bacnet, mqtt_client, id, name, address, device_id, register_config):
        super().__init__()
        self.id = id
        self.name = name
        self.gateway = gateway
        self.address = address
        self.device_id = device_id
        self.mqtt = mqtt_client
        self.bacnet = bacnet
        self.connect()

        self.previous_values = {}
        self.registers = {}
        for register in register_config:
            self.registers[register["id"]] = BacnetRegister(
                self, register.get("id"),register.get("name"),register.get("register"),register.get("component"),
                register.get("unit_of_measurement"), register.get("device_class"), register.get("writable", False)
            )

    def connect(self):
        self.device = BAC0.device(self.address, self.device_id, self.bacnet)


class BacnetMqttGateway:
#    devices: Dict[BacnetDevice]
#    update_interval: int

    def __init__(self):
        super().__init__()
        self.configuration = load_yaml_with_includes("gateway.yaml")
        self.bacnet = BAC0.lite()
        self.devices = {}
        self.update_interval = 20
        self.discovery_prefix = "homeassistant"
        self.init_mqtt()
        self.init_devices()

    def send_states(self):
        for device in self.devices.values():
            for register in device.registers.values():
                register.read()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        (
            discovery_prefix,
            component,
            device_id,
            register_id,
            message_type,
        ) = msg.topic.split("/")

        if discovery_prefix == self.discovery_prefix:
            register = self.devices[device_id].registers[register_id]
            if register.writable and component == "switch" and message_type == "set":
                register.write(str(msg.payload.decode("utf-8","ignore")))
            if message_type == "state" and not msg.payload:
                register.read()
            if message_type == "config" and not msg.payload:
                register.send_config()

    def init_devices(self):
        for device_config in self.configuration["devices"]:
            profile = device_config.get("profile", {})
            device_id = device_config.get("id")
            device = BacnetDevice(
                self,
                self.bacnet,
                self.mqtt,
                device_id,
                device_config.get("name"),
                device_config.get("address"),
                device_config.get("bacnet_device"),
                profile.get("properties", []))

            self.devices[device_id] = device

    def init_mqtt(self):
        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message

        if "username" in self.configuration["mqtt"]:
            self.mqtt.username_pw_set(
                self.configuration["mqtt"]["username"],
                self.configuration["mqtt"].get("password"),
            )

        self.mqtt.connect(
            self.configuration["mqtt"].get("host"),
            self.configuration["mqtt"].get("port", 1883),
            60,
        )

    def central_loop(self):
        self.mqtt.loop_start()
        while True:
            self.send_states()
            time.sleep(self.update_interval)
