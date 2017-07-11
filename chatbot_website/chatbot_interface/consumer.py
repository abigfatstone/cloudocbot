from channels import Group
from channels.sessions import channel_session
import logging
import sys
import json

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
        Group(clientName).send({'text': json.dumps({'message': '欢迎使用小i，请问您哪里不舒服？'})})
        
@channel_session
def ws_receive(message):

    clientName = message.channel_session['room']
    data = json.loads(message['text'])
    userInput = ''.join(data['message']).split('@userid@')
    userID = userInput[1]

    p_callbackKey=''
  
    if userID == 'null':
        userID = clientName

    try:
        sysSaid = ChatbotManager.callBot(userID,p_callbackKey,userInput[0])

        callbackKey=sysSaid[1]
        answer = '' 

        if sysSaid[3] == 'checkbox':
            p_output = sysSaid[2].split('@L1@')
            answer = split_line(p_output[0])
            answer = answer + split_checkbox(p_output[1])
            answer=answer + "<p align='right'><a href='javascript:void(0)' class='button button-glow button-rounded button-raised button-primary' id='sendOption'> 提交</a></p>"
       
        elif sysSaid[3] == 'table':
            p_output = sysSaid[2].split('@L1@')
            answer = '<table width = \'90%\'>'
            for table_line in p_output:
                answer = answer + '<tr>' + split_tab(table_line) + '</tr>'
            answer = answer + '</table> '   
        else:
            answer=sysSaid[2]

    except:  # Catching all possible mistakes
        logger.error('{}: Error with this question {}'.format(clientName, userInput))
        logger.error("Unexpected error:", sys.exc_info()[0])
        answer = 'Error: Internal problem'

    # Check eventual error
    if not answer:
        answer = 'Error: Try a shorter sentence'

    logger.info('{}: {} -> {}'.format(clientName, userInput, answer))

    # Send the prediction back
    Group(clientName).send({'text': json.dumps({'message': answer, 'msgtype': sysSaid[3]})})

def split_line(inputLine):
    line  = ''
    inputList =  inputLine.split('@L2@') 
    for inputOne in inputList:
        line = line + '<p>' + inputOne + '</p>'
    return line    

def split_tab(inputLine):
    line  = ''
    inputList =  inputLine.split('@L2@') 
    for inputOne in inputList:
        line = line + '<td>' + inputOne + '</td>'
    return line    

def split_checkbox(inputLine):
    line = ''
    check_list = inputLine.split('@L2@')
    for check_one in check_list:
        line = line+ "<p><input type='checkbox' name='option' value='"+check_one+"' />"+check_one+"</p>"
    return line    

@channel_session
def ws_disconnect(message):
    """ Called when a client disconnect
    Args:
        message (Obj): object containing the client query
    """
    clientName = message.channel_session['room']
    logger.info('Client disconnected: {}'.format(clientName))
    Group(clientName).discard(message.reply_channel)










