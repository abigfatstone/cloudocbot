from channels import Group
from channels.sessions import channel_session
import logging
import sys
import json
import re

from .chatbotmanager import ChatbotManager


logger = logging.getLogger(__name__)


def _getClientName(client):
    """ Return the unique id for the client
    Args:
        client list<>: the client which send the message of the from [ip (str), port (int)]
    Return:
        str: the id associated with the client
    """
    return 'room-' + client[0] + '-' + str(client[1])


@channel_session
def ws_connect(message):
    """ Called when a client try to open a WebSocket
    Args:
        message (Obj): object containing the client query
    """
    if message['path'] == '/chat':  # Check we are on the right channel
        clientName = _getClientName(message['client'])
        logger.info('New client connected: {}'.format(clientName))
        Group(clientName).add(message.reply_channel)  # Answer back to the client
        message.channel_session['room'] = clientName
        message.reply_channel.send({'accept': True})
        Group(clientName).send({'text': json.dumps({'message': '欢迎使用小i，请问尊姓大名？'})})
        
@channel_session
def ws_receive(message):
    """ Called when a client send a message
    Args:
        message (Obj): object containing the client query
    """
    # Get client info
    clientName = message.channel_session['room']
    #message.channel_session['cs_callbackKey']='firstcall'
    data = json.loads(message['text'])
    # Compute the prediction
    userSaid = ''.join(data['message']).split('@userid@')
    userID=userSaid[1]
    callbackKey='firstcall'
    if userID == 'null':
        userID=clientName
    try:
        sysSaid = ChatbotManager.callBot(userID,'firstcall',userSaid[0])
        answer=sysSaid[0]
        callbackKey=sysSaid[1]
        #answer = answer + "<a href='baidu.com'>baidu</a>"
        answer += "<p><input type='checkbox' name='option' value='上海' />上海</p><p><input type='checkbox' name='option' value='北京' />北京</p><p><a href='javascript:void(0)' style='color:red' id='sendOption'> 提交</a></p>"
    except:  # Catching all possible mistakes
        logger.error('{}: Error with this question {}'.format(clientName, userSaid))
        logger.error("Unexpected error:", sys.exc_info()[0])
        answer = 'Error: Internal problem'

    # Check eventual error
    if not answer:
        answer = 'Error: Try a shorter sentence'

    logger.info('{}: {} -> {}'.format(clientName, userSaid, answer))

    # Send the prediction back
    Group(clientName).send({'text': json.dumps({'message': answer})})

@channel_session
def ws_disconnect(message):
    """ Called when a client disconnect
    Args:
        message (Obj): object containing the client query
    """
    clientName = message.channel_session['room']
    logger.info('Client disconnected: {}'.format(clientName))
    Group(clientName).discard(message.reply_channel)
