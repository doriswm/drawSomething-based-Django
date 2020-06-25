const canvas = document.querySelector("#canvas");
const ctx = canvas.getContext("2d");
const div = document.querySelector("#canvas_plus_player");
const wsUrl = 'ws://'+window.location.host+'/socket'
var ws;
createWebSocket(wsUrl);   //connect to ws
//Resizing
// canvas.height = window.innerHeight;
// canvas.width = window.innerWidth;
// canvas.height = 500;
// canvas.width = 1000;
canvas.height = document.documentElement.clientHeight * 0.65;
canvas.width = document.documentElement.clientWidth * 0.75;  
var ratio = canvas.height / canvas.width;
function render() {
    canvas.height = document.documentElement.clientHeight * 0.65;
    canvas.width = document.documentElement.clientWidth * 0.75; 

}


//variables
var press_down = false
var real_close = false
var roomid = document.getElementById("id_quit_room").value;
var currentuser = document.getElementById("id_current_username").innerText;

function startPosition() {
    press_down = true;
    draw(e);
}
function endPosition() {
    press_down = false;
    ctx.beginPath();
    ws.send('stop.'+roomid);
} 


function draw(e) {

    if (!press_down) return;
    console.info("drawing...")
    ctx.lineWidth = 5;
    ctx.lineCap = "round";
    console.info(div.offsetTop);
    console.info(div.offsetLeft);
    console.info(this.offsetLeft);
    console.info(this.offsetTop);
    /*console.info(e.x);
    console.info(e.y);*/
    ws.send(e.x+'.'+e.y+'.'+roomid);
    // ctx.strokeStyle = "red";
    ctx.lineTo(e.x-this.offsetLeft/2, e.y-div.offsetTop-this.offsetTop);
    // ctx.lineTo(e.clientX-this.offsetLeft, e.clientY-this.offsetTop);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.x-this.offsetLeft/2, e.y-div.offsetTop-this.offsetTop);
    // ctx.moveTo(e.clientX-this.offsetLeft, e.clientY-this.offsetTop);
}
var roomid = document.getElementById("id_quit_room").value;
var currentuser = document.getElementById("id_current_username").innerText;
// console.info("currentusername", currentuser);

function getCanvasStat() {
    $.ajax({
        url: "/refresh-draw-stat",
        dataType : "json",
        data: "roomid="+ roomid + "&currentuser="+currentuser,
        success: painter
    })
}

var gameStartFlag = false;
function painter(response) {
    console.info("response", response)
    if (response.flag && !gameStartFlag) {
        
        window.alert("Game Start!");
        gameStartFlag = true;
        if (response.painter == currentuser) {
            console.info("current user is drawing!")
            canvas.addEventListener("mousedown", startPosition);
            canvas.addEventListener("mouseup", endPosition);
            canvas.addEventListener("mousemove", draw); 
            if(document.getElementById("hintword")==null){
                if(document.getElementById("hintplayer")!=null){
                    document.getElementById("hintplayer").remove();
                }
                $("#hints").append(
                    '<p id="hintword">You are the painter. The word is ' + response.word + '</p>'
                )
            }
            
        }else{
            if(document.getElementById("hintplayer")!=null){
                document.getElementById("hintplayer").remove();
            }
            if(document.getElementById("hintpainter")==null){
                $("#hints").append(
                    '<p id="hintpainter">The painter is ' + response.painter + '. Please type your guess in the chatting area</p>'
                )
            }
            
        }
    }
    if (!response.flag) {
        if(document.getElementById("hintplayer")==null){
            $("#hints").append(
                '<p id="hintplayer">Waiting for other players...</p>'
            )
        }
        gameStartFlag = false
        canvas.removeEventListener("mousedown", startPosition);
        canvas.removeEventListener("mouseup", endPosition);
        canvas.removeEventListener("mousemove", draw); 
    }
    //EventListeners

}

function addPost() {
    var itemTextElement = $("#id_post_input_text");
    var itemTextValue   = itemTextElement.val();
    // Clear input box and old error message (if any)
    itemTextElement.val('');
    var postUser = $("#user_name");
    var postUserValue   = postUser.val();
    let dateTime = new Date().toLocaleString();
    msg = 'post&' + escape(itemTextValue) + '&' + dateTime + '&' + postUserValue + '&' + roomid;
    // console.log(msg);
    ws.send(msg);
}

function createWebSocket(url) {
    try{
        if('WebSocket' in window){
            ws = new WebSocket(url);
        } else{
              console.log("Exployer fail to use websocket!"); 
        }
        initEventHandle();
    }catch(e){
        reconnect(url);
        console.log(e);
    }     
}

// close ws when close window.
window.onbeforeunload = function() {
    real_close = true;
    ws.close();
}  

function reconnect(url) {
    setTimeout(function () {
        createWebSocket(url);
    }, 2000);
}



function initEventHandle() {
    ws.onclose = function () {
        //reconnect(wsUrl);
        console.log("ws has backup"+new Date().toUTCString());
    };
    ws.onerror = function () {
        reconnect(wsUrl);
        console.log("connect error");
    };
    ws.onopen = function () {    
        ws.send('handshake.'+roomid)
        console.log("websocket connect "+new Date().toUTCString());
    };
    ws.onmessage = function (event) {    
        console.log('message is');
        if (event.data == 'stop') {
            press_down = false;
             ctx.beginPath();
        } else if (event.data == 'win') {
            window.location.href="http://"+window.location.host+'/win/'+roomid;  
        } else {
            let pathObj = event.data.split('&')
            if (pathObj[0] == 'post') {
                 console.log("posting")
                 $("#post-list").append(
                    '<li class="d-flex justify-content-between mt-3 shadow p-3 bg-white rounded"><div class="chat-body white p-3 ml-2 z-depth-1">'
                    +'<div class="header"><strong class="primary-font">'
                    + pathObj[3]
                    +'</strong><small class="pull-right text-muted"><i class="far fa-clock"></i>' 
                    + pathObj[2]
                    +'</small></div><hr class="w-100"><p class="mb-0">'
                    + unescape(pathObj[1])
                    +'</p></div></li>'
                )
            } else {
            console.info("showing...")
            ctx.lineWidth = 5;
            ctx.lineCap = "round";
            console.info(div.offsetTop);
            console.info(div.offsetLeft);
            console.info(this.offsetLeft);
            console.info(this.offsetTop);
            console.info(pathObj[0]);
            console.info(pathObj[1]);
            // ctx.strokeStyle = "red";
            ctx.lineTo(pathObj[0]-canvas.offsetLeft/2, pathObj[1]-div.offsetTop-16);
            // ctx.lineTo(e.clientX-this.offsetLeft, e.clientY-this.offsetTop);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(pathObj[0]-16, pathObj[1]-div.offsetTop-16);
            // ctx.moveTo(e.clientX-this.offsetLeft, e.clientY-this.offsetTop);
        }
        }
    };
}

window.addEventListener("resize", render);
// causes state to be re-fetched every 5 seconds
if (!gameStartFlag) {
    window.setInterval(getCanvasStat, 5000);    
}
