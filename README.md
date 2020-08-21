# bacnet-mqtt-gateway

Gateway written in Python 3 between Bacnet and MQTT. Built for connecting Flexit Nordic S5 ventilation systems to Home Assistant, probably useful for other decies as well.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Docker

### Installing

```
docker build https://github.com/hubarbeit/bacnet-mqtt-gateway
```

or if you're using docker-compose use the following in your docker-compose.yml:

```
version: "3"
services:
  bacnet_mqtt_gateway:
    build:
      context: https://github.com/hubarbeit/bacnet-mqtt-gateway
      volumes:
          - ./gateway.yaml:/gateway.yaml:ro
```

### Confirguration

* Adjust the gateway.yaml file to your needs.
* Create new device specific files containing register information.

## Built With

* [BAC0](https://bac0.readthedocs.io/) - BACØ - BACnet Test Tool
* [paho-mqtt](http://www.eclipse.org/paho/) - Eclipse Paho MQTT Python client library

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
