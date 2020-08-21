from setuptools import setup, find_packages

setup(
    name = 'bacnet_mqtt_gateway',
    packages = find_packages(),
    entry_points={
        "console_scripts": [
            "bacnet_mqtt_gateway = bacnet_mqtt_gateway.script:main",
        ],
)
