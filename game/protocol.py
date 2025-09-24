class ProtocolTCP:
    class ToServer:
        requestConnection = "00"
        requestDisconnection = "01"
        renameClient = "02"
        checkConnection = "03"
        sendTextMessage = "04"
        requestChunk = "05"
        checkConnection = "08"
        answerCheckConnection = "09"
        requestStop = "10"
        requestPlayerList = "11"

        unknown = "404"
    class ToClient:
        connected = "00"
        disconnected = "01"
        executionSuccessful = "02"
        executionFailed = "03"
        renamedClient = "04"
        answerChunk = "05"
        error = "06"
        chatMessage = "07"
        checkConnection = "08"
        answerCheckConnection = "09"
        playerList = "10"
        playerAdded = "11"
        playerRemoved = "12"
        serverShutdown = "13"
        unknown = "404"
class ProtocolUDP:
    class ToServer:
        requestConnection = "00"
        requestDisconnection = "01"
        movePlayer = "02"
        unknown = "404"
    class ToClient:
        connected = "00"
        disconnected = "01"
        playerMoved = "02"
        error = "06"
        unknown = "404"
class NetworkErrors:
    """
    Inspired by http response codes
    """
    BAD_REQUEST = -400
    BAD_IDENTITY = -401
    INVALID_AUTH = -403
    NOT_FOUND = -404
    ALREADY_CONNECTED = -429