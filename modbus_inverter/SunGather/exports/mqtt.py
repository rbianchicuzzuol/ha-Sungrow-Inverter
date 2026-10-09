import logging
import json
import paho.mqtt.client as mqtt

class export_mqtt(object):
    def __init__(self):
        self.mqtt_client = None
        self.sensor_topic = None
        self.mqtt_queue = []
        self.ha_discovery_published = False
        self.last_state = {}

    # Configure MQTT
    def configure(self, config, inverter):
        model = inverter.getInverterModel(True)
        self.mqtt_config = {
            'host': config.get('host', None),
            'port': config.get('port', 1883),
            'client_id': config.get('client_id', f'SunGather-{model}'),
            'topic': config.get('topic', f"inverter/{model}/registers"),
            'username': config.get('username', None),
            'password': config.get('password',None),
            'homeassistant': config.get('homeassistant',False)
        }

        self.ha_sensors = [{}]
        self.ha_sensors.pop() # Remove null value from list

        if not self.mqtt_config['host']:
            logging.info(f"MQTT: Host config is required")
            return False
        client_id = self.mqtt_config['client_id']
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_publish = self.on_publish

        if self.mqtt_config['username'] and self.mqtt_config['password']:
            self.mqtt_client.username_pw_set(self.mqtt_config['username'], self.mqtt_config['password'])

        if self.mqtt_config['port'] == 8883:
            self.mqtt_client.tls_set()
        
        self.mqtt_client.connect_async(self.mqtt_config['host'], port=self.mqtt_config['port'], keepalive=60)
        self.mqtt_client.loop_start()

        if self.mqtt_config['homeassistant']:
            for ha_sensor in config.get('ha_sensors'):
                if not inverter.validateRegister(ha_sensor['register']):
                    logging.debug(f"MQTT: Skipping unavailable register {ha_sensor['register']}")
                    continue
                else:
                    self.ha_sensors.append(ha_sensor)
    
        return True

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            logging.error(f"MQTT: Connection refused, code: {rc}")
            return
        self.ha_discovery_published = False
        logging.info(f"MQTT: Connected to {client._host}:{client._port}")

    def on_disconnect(self, client, userdata, rc):
        logging.info(f"MQTT: Server Disconnected code: {rc}")
    
    def on_publish(self, client, userdata, mid):
        try:
            self.mqtt_queue.remove(mid)
        except Exception as err:
            pass
        logging.debug(f"MQTT: Message {mid} Published")

    def cleanName(self, name):
        return name.lower().replace(' ','_')

    def publish(self, inverter):
        # A partial scrape must not erase values read successfully before.
        self.last_state.update({
            key: value for key, value in inverter.latest_scrape.items()
            if value is not None and value != ''
        })
        if not self.last_state:
            return False
        try:
            if not self.mqtt_client.is_connected():
                logging.warning(f'MQTT: Server Disconnected; {self.mqtt_queue.__len__()} messages queued, will automatically attempt to reconnect')
                return False
        except Exception as err:
            logging.warning(f'MQTT: Server Error; Server not configured')
            return False
        payload = json.dumps(self.last_state)
        logging.debug(f"MQTT: Publishing: {self.mqtt_config['topic']} : {payload}")
        self.mqtt_queue.append(self.mqtt_client.publish(
            self.mqtt_config['topic'], payload, qos=1, retain=True
        ).mid)
        logging.info(f"MQTT: Published")

        if self.mqtt_config['homeassistant'] and not self.ha_discovery_published:
            for ha_sensor in self.ha_sensors:
                config_msg = {}
                if ha_sensor.get('name'):
                    ha_topic = 'homeassistant/' + ha_sensor.get('sensor_type', 'sensor') + '/inverter/' + self.cleanName(ha_sensor.get('name')) + '/config'
                    config_msg['name'] = "Inverter " + ha_sensor.get('name')
                    config_msg['unique_id'] = "inverter_" + self.cleanName(ha_sensor.get('name'))
                config_msg['state_topic'] = self.mqtt_config['topic']
                config_msg['value_template'] = "{{ value_json." + ha_sensor.get('register') + " }}"
                if inverter.getRegisterUnit(ha_sensor.get('register')):
                    config_msg['unit_of_measurement'] = inverter.getRegisterUnit(ha_sensor.get('register'))
                if ha_sensor.get('dev_class'):
                    config_msg['device_class'] = ha_sensor.get('dev_class')
                if ha_sensor.get('state_class'):
                    config_msg['state_class'] = ha_sensor.get('state_class')
                if ha_sensor.get('payload_on'):
                    config_msg['payload_on'] = ha_sensor.get('payload_on')
                if ha_sensor.get('payload_off'):
                    config_msg['payload_off'] = ha_sensor.get('payload_off')
                config_msg['ic'] = "mdi:solar-power"
                config_msg['device'] = { "name":"Solar Inverter", "mf":"Sungrow", "mdl":inverter.getInverterModel(), "connections":[["address", inverter.getHost() ]]}

                logging.debug(f'MQTT: Topic; {ha_topic}, Message: {config_msg}')
                self.mqtt_queue.append(self.mqtt_client.publish(ha_topic, json.dumps(config_msg), retain=True, qos=1).mid)
            self.ha_discovery_published = True
            logging.info("MQTT: Published Home Assistant Discovery messages")

        return True
