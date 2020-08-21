# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

COPY bacnet_mqtt_gateway/ .

# command to run on container start
CMD [ "python", "-u", "./script.py" ]
