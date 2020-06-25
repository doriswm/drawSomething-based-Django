var roomid = document.getElementById("id_quit_room").value;

// Sends a new request to update the global
function getPlayers() {

    $.ajax({
        url: "/refresh-room",
        dataType : "json",
        data: "roomid="+ roomid,
        success: updatePlayers
    });
}

function updatePlayers(response) {
    players = response.players
    // Remove
    $(".player").each(function() {
        my_id = parseInt(this.id.substring("id_player_".length))

        var id_in_players = false
        $(players).each(function() {
            if (this.id == my_id){
                id_in_players = true                
            } 

        })
        if (!id_in_players) this.remove()
    })

    //Add players
    $(players).each(function() {
        id = "id_player_" + this.id
        if (document.getElementById(id) == null) {
            $("#room_players").append(
                '<div class="col-md-2 player" id="id_player_'+ this.id +'">' +
                '<div><img class="w-50 h-50 shadow-lg"' +
                'src="/photo/' + this.id + '" class="round" alt="profilephoto"></div>' + 
                '<div>'+this.username +'</div>'+  
                '</div>'
            )
        }

    }
    )

}

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        c = cookies[i].trim();
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length);
        }
    }
    return "unknown";
}

window.onload = getPlayers;

// causes list to be re-fetched every 5 seconds
window.setInterval(getPlayers, 5000);
