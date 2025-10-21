"""MQTT module"""
import logging
import uuid
import paho.mqtt.client as mqtt


class MQTTHandler:
    """Handle persistent MQTT connection and publish/subscribe operations"""

    def __init__(self, ctx):
        self.ctx = ctx
        self.logger = logging.getLogger(f"{__name__}[{ctx.config.system.prog_name}]")
        self.base_topic = ctx.config.mqtt.base_topic
        self.client_id = f"python-mqtt-{ctx.config.system.prog_name}-{uuid.uuid4()}"
        self.client = mqtt.Client(client_id=self.client_id)

        if ctx.config.mqtt.user and ctx.config.mqtt.password:
            self.client.username_pw_set(ctx.config.mqtt.user, ctx.config.mqtt.password)

        try:
            self.client.will_set(
                f"{self.base_topic}/status/online",
                payload="False",
                retain=True,
                qos=1,
            )
        except Exception as e:
            self.logger.error("Failed to set Last Will message: %s", e)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.logger.debug("Initializing mqtt")

        try:
            self.client.connect_async(
                ctx.config.mqtt.broker_host,
                ctx.config.mqtt.broker_port,
                keepalive=300
            )
            self.client.loop_start()
        except KeyboardInterrupt:
            self.logger.info("MQTT connection interrupted by user")
        except Exception as e:
            self.logger.error("Failed to connect to MQTT broker: %s", e)


    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.logger.info("Connected to MQTT broker at %s:%s",
                self.ctx.config.mqtt.broker_host,
                self.ctx.config.mqtt.broker_port
            )
            self.publish("status/online", "True", retain=True)

            command_topic = f"{self.ctx.config.mqtt.base_topic}/cmd/#"
            client.subscribe(command_topic)
            self.logger.debug("Subscribed to command topic: %s", command_topic)
        else:
            self.logger.error("Failed to connect to MQTT Broker, return code: %s", rc)


    def on_message(self, client, userdata, msg):
        """Handle received MQTT messages."""
        try:
            payload = msg.payload.decode().strip()
            self.logger.debug("Received message: '%s' on topic: '%s'", payload, msg.topic)

            # handle commands on subscribed topic like 'boilr/cmd/manual_override'
            if msg.topic.startswith(f"{self.ctx.config.mqtt.base_topic}/cmd/"):
                command = msg.topic.split("/")[-1]
                self.logger.debug("Routing command: %s (payload: %s)", command, payload)

                try:
                    result = self.ctx.boilr.handle_command(command, payload)
                    ack_payload = result if isinstance(result, str) else "ok"
                    self.publish(f"ack/{command}", ack_payload)
                except Exception as e:
                    self.logger.error("Error executing command '%s': %s", command, e)
                    self.publish(f"ack/{command}", "error")

        except Exception as e:
            self.logger.error("Error processing incoming message: %s", e)


    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        if rc != 0:
            self.logger.warning("Unexpected disconnection. Attempting reconnect...")
            try:
                client.reconnect()
            except Exception as e:
                self.logger.error("Reconnect failed: %s", e)
        else:
            self.logger.info("Disconnected from MQTT broker")


    def publish(self, topic, message, retain=False, qos=0):
        """MQTT publish"""
        full_topic = f"{self.base_topic}/{topic}"
        try:
            result = self.client.publish(full_topic, message, qos=qos, retain=retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug("Published '%s' to '%s'", message, full_topic)
            else:
                self.logger.warning("Failed to publish to '%s': %s", full_topic, result.rc)
        except Exception as e:
            self.logger.error("MQTT publish error: %s", e)


    def subscribe(self, topic, qos=0):
        """MQTT subscribe"""
        full_topic = f"{self.base_topic}/{topic}"
        try:
            self.client.subscribe(full_topic, qos=qos)
            self.logger.debug("Subscribed to topic: %s", full_topic)
        except Exception as e:
            self.logger.error("Failed to subscribe to MQTT topic: %s", e)


    def disconnect(self):
        """Disconnect MQTT client"""
        try:
            self.publish("status/online", "False", retain=True)
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as e:
            self.logger.error("Failed to disconnect from MQTT broker: %s", e)
