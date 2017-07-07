// Credits goes to https://blog.heroku.com/in_deep_with_django_channels_the_future_of_real_time_apps_in_django


 function getQueryString(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]); return null;
    }


$(function() {

    // When using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat");
    var chat_zone = $("#chat_zone");
    
    chatsock.onmessage = function(message) {
        console.log('remote message', message.data)
        var data = JSON.parse(message.data);
        chat_zone.prepend(
            $("<p class='answer'></p>").html('Bot: ' + data.message)
        );
    };

   

    $(document).on("click","#sendOption", function(event) {
        // var options= $('input[type=checkbox]:checked').each(function(ele, index){
            //     message_val
            // })
          
       var message_val =  '北京=1'   + '@userid@' + getQueryString('UserID')  
       var message = {message: message_val  };
       chatsock.send(JSON.stringify(message));
       chat_zone.prepend(
        $("<p class='question'></p>").html('You: ' + message_val)
        );      
    })

    $("#chat_form").on("submit", function(event) {

        try {
            var message_elem = $('#message');
            var message_val = message_elem.val();
            // var options= $('input[type=checkbox]:checked').each(function(ele, index){
            //     message_val
            // })

            if (message_val) {
                // Send the message
                var message = {
                    message: message_val + '@userid@' + getQueryString('UserID') 
                };
                chatsock.send(JSON.stringify(message));
                message_elem.val('').focus();

                // Add the message to the chat
                chat_zone.prepend(
                    $("<p class='question'></p>").html('You: ' + message_val)
                );
            }
        }
        catch(err) {
            console.error(err.message);
        }

        return false;
    });
});