"""MQTT module"""
import logging
import paho.mqtt.client as mqtt

import boilr.config as config

logger = logging.getLogger(__name__)
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        logger.debug("Connected to MQTT Broker successfully.")
    else:
        logger.error("Failed to connect to MQTT Broker, return code: %s", rc)

client.on_connect = on_connect

def on_message(client, userdata, msg):
    """Handling received MQTT messages - DEV"""
    logger.debug("Received message: %s on topic: %s", msg.payload.decode(), msg.topic)

client.on_message = on_message

def publish_mqtt(topic, message):
    """MQTT publish"""
    try:
        client.connect(config.MqttConfig.broker_ip, config.MqttConfig.broker_port, 60)
        client.publish(config.MqttConfig.topic + '/' + topic, message)
        client.disconnect()
        logger.debug("Message: '%s' published to topic: '%s'", message, topic)
    except Exception as e:
        logger.error("Failed to publish MQTT message: %s", e)

def subscribe_mqtt(topic):
    """MQTT subscribe - DEV"""
    try:
        client.connect(config.MqttConfig.broker_ip, config.MqttConfig.broker_port, 60)
        client.subscribe(config.MqttConfig.topic + '/' + topic)
        client.loop_start() # start MQTT loop in the background to process messages
        logger.debug("Subscribed to topic: %s", topic)
    except Exception as e:
        logger.error("Failed to subscribe to MQTT topic: %s", e)
