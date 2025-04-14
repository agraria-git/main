/**
 * Descripcción de la clase
 */
class MqttService {
    constructor(robotUUID) {
        var wsbroker = "10.8.0.1";
        var wsport = 8881;

        this.mqttBattery='/mqttBattery';
        this.mqttLogs='/mqttLogs';
        this.mqttMagicppp='/mqttMagicppp';
        this.mqttRobotCommand='/mqttRobotCommand';
        this.mqttParams='/mqttParams';
        this.mqttImageLogs='/mqttImageLogs';
        this.mqttCamera='/panTilt';

        this.mqttClient = this.#getClient(wsbroker,wsport);
        this.robotUUID=robotUUID;
        var mqttOptions = this.#getMqttOptions(this.mqttClient,this.robotUUID,this.mqttBattery,this.mqttLogs,this.mqttMagicppp,this.mqttRobotCommand,this.mqttParams, this.mqttImageLogs,this.mqttCamera);
        this.mqttClient.onConnectionLost=this.#mqttConnectionLost;
        this.mqttClient.onMessageArrived = this.#mqttMessageArrived;
        this.mqttClient.connect(mqttOptions); 
        
    }
    
    publishMessage(topic,message) {
        var mqttMessage = new Paho.MQTT.Message(message);
        mqttMessage.destinationName = topic;
        this.mqttClient.send(mqttMessage);
    }
    
    #getClient(broker,port){
        return new Paho.MQTT.Client(broker, port, "magicppp_" + parseInt(Math.random() * 100, 10));
    }

    #getMqttOptions(mqttClient,robotUUID,mqttBattery,mqttLogs,mqttMagicppp,mqttRobotCommand,mqttParams, mqttImageLogs,mqttCamera){
        return {
            timeout: 3,
            onSuccess: function () {
                console.log("MQTTService: Conection Success");
                document.getElementById("mqttStateImage").src = "mqttConnected2.png";
                mqttClient.subscribe(mqttMagicppp, { qos: 1 });
                mqttClient.subscribe(mqttLogs);
                mqttClient.subscribe(mqttImageLogs);
                mqttClient.subscribe(mqttBattery);
                mqttClient.subscribe(mqttParams);
                mqttClient.subscribe(mqttCamera);
                var mqttMessage = new Paho.MQTT.Message('{"UUID":'+robotUUID+',"command": "mqttConnected"}');
                mqttMessage.destinationName = mqttRobotCommand;
                mqttClient.send(mqttMessage);
            },
            onFailure: function (message) {
                document.getElementById("mqttStateImage").src = "mqttDisconnected2.png";
                console.error("MQTTService: Connection failed: " + message.errorMessage);
            },
        };
        
    }

    #mqttMessageArrived(message){
        // console.log("MQTTService: Message Arrived to "+message.destinationName+" : "+message.payloadString);
        var mqttBattery='/mqttBattery';
        var mqttLogs='/mqttLogs';
        var mqttMagicppp='/mqttMagicppp';
        var mqttRobotCommand='/mqttRobotCommand';
        var mqttParams='/mqttParams';
        var mqttImageLogs='/mqttImageLogs';
        var mqttCamera='/panTilt';

        if (message.destinationName === mqttLogs) {
            logsMqttTopic(message.payloadString);
        }
        else if(message.destinationName === mqttMagicppp){
            magicpppMqttTopic(message);
        }
        else if(message.destinationName === mqttImageLogs){
            imageLogTopic(message.payloadString);
        }
        else if(message.destinationName === mqttBattery){
            batteryLevelTopic(message.payloadString);
        }
        else if(message.destinationName ===  mqttParams){
            paramsTopic(message.payloadString);
        }
        else if(message.destinationName ===  mqttCamera){
            cameraTopic(message.payloadString);
        }
    }

    #mqttConnectionLost(message){
        document.getElementById("mqttStateImage").src = "mqttDisconnected2.png";
        console.error("MQTTService: Connection lost: " + message.errorMessage);
    }


}



