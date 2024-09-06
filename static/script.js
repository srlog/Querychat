(function () {
    var Message;
    Message = function (arg) {
        this.text = arg.text, this.message_side = arg.message_side;
        this.draw = function (_this) {
            return function () {
                var $message;
                $message = $($('.message_template').clone().html());
                $message.addClass(_this.message_side).find('.text').html(_this.text);
                $('.messages').append($message);
                return setTimeout(function () {
                    return $message.addClass('appeared');
                }, 0);
            };
        }(this);
        return this;
    };

    $(function () {
        var getMessageText, message_side, sendMessage, sendToBackend;
        message_side = 'right';

        getMessageText = function () {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };

        sendMessage = function (text, side) {
            var $messages, message;
            if (text.trim() === '') {
                return;
            }
            $messages = $('.messages');
            message = new Message({
                text: text,
                message_side: side
            });
            message.draw();
            return $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 900);
        };

        sendToBackend = function (text) {
            $.ajax({
                url: '/chat',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ message: text }),
                success: function (response) {
                    sendMessage(response.reply, 'left');  // Display the reply on the left side
                },
                error: function () {
                    sendMessage('Error: Could not contact the server.', 'left');
                }
            });
        };

        $('.send_message').click(function (e) {
            var messageText = getMessageText();
            sendMessage(messageText, 'right');  // Display user's message on the right side
            sendToBackend(messageText);  // Send user's message to the backend
            $('.message_input').val('');  // Clear the input field
        });

        $('.message_input').keyup(function (e) {
            if (e.which === 13) {
                var messageText = getMessageText();
                sendMessage(messageText, 'right');  // Display user's message on the right side
                sendToBackend(messageText);  // Send user's message to the backend
                $('.message_input').val('');  // Clear the input field
            }
        });
    });
}.call(this));
