class rosBridgeService {
    constructor() {
        var ros = new ROSLIB.Ros({
            url : 'ws://10.8.0.3:9090'
          });
        
          ros.on('connection', function() {
            console.log('rosBridgeService : Connected to websocket server.');
          });
        
          ros.on('error', function(error) {
            console.log('rosBridgeService : Error connecting to websocket server: ', error);
          });
        
          ros.on('close', function() {
            console.log('rosBridgeService : Connection to websocket server closed.');
          });
        
          
        // Crear un cliente para la acción
        this.client = new ROSLIB.ActionClient({
            ros : ros,
            serverName : '/move_base',
            actionName : 'move_base_msgs/MoveBaseAction'
        });
    }

    cancelGoal(){
        console.log("rosBridgeService: Cancel Goal sent")
        this.client.cancel();
    }
   
    


}


