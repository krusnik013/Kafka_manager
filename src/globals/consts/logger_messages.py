class LoggerMessages:
    # --- Tags ---
    TAG_ZMQ_SERVER = "[🛰️ ZMQ_SERVER]"
    TAG_ZMQ_CLIENT = "[📡 ZMQ_CLIENT]"
    TAG_ZMQ_CONTROLLER = "[🧠 ZMQ_CONTROLLER]"
    TAG_KAFKA = "[📦 KAFKA]"
    TAG_CONFIG = "[⚙️ CONFIG]"

    # Generic
    DEFAULT_ERROR = "ERROR"

    # ZMQ server
    
    ZMQ_CONTROLLER_FORWARD_MESSAGE = "Forwarded ZMQ message to Kafka: topic={}, message={}"
    ZMQ_CONTROLLER_MISSING_FIELD = "Missing 'message' field in incoming ZMQ data"
    ZMQ_SERVER_BOUND_TO_ADDRESS = "ZMQ REP server bound to {}"
    ZMQ_SERVER_STOPPED = "ZMQ REP server stopped"
    ZMQ_SERVER_RECEIVED_RAW_REQUEST = "ZMQ server: received raw request: {}"
    ZMQ_SERVER_PARSE_REQUEST_FAILED = "ZMQ server: failed to parse Request.from_json: {}"
    ZMQ_SERVER_SOCKET_LOOP_ERROR = "ZMQ server socket loop error: {}"
    ZMQ_SERVER_SENT_RESPONSE = "ZMQ server: sent response: {}"
    ZMQ_SERVER_SEND_ERROR = "ZMQ server error while sending response: {}"
    ZMQ_SERVER_HANDLE_REQUEST = (
        "ZMQ server: handling resource='{}', operation='{}', data={}"
    )

    # ZMQ client (ExampleManager test client)
    ZMQ_CLIENT_GENERATED_MESSAGE = "Generated ZMQ test message: {}"
    ZMQ_CLIENT_SENDING_REQUEST = "Sending ZMQ request: {}"
    ZMQ_CLIENT_RECEIVED_RESPONSE = "Received ZMQ response: {}"
    ZMQ_CLIENT_RECV_TIMEOUT = "ZMQ client: recv timeout, no reply from server"
    ZMQ_CLIENT_THREAD_ERROR = "ZMQ client thread error: {}"

    # Example controller
    EXAMPLE_DATA_RECEIVED = "example data received: {}"
    EXAMPLE_FORWARD_TO_KAFKA = (
        "Forwarded ZMQ message to Kafka: topic={}, message={}"
    )

    # Config / XML
    CONFIG_KEY_NOT_FOUND = "xmlconfig: key '{}' not found."
    CONFIG_DID_YOU_MEAN = "xmlconfig: did you mean '{}'?"
    CONFIG_NO_MATCHES = "xmlconfig: no close matches found."

    # Kafka
    KAFKA_TOPIC_ALREADY_CONSUMING = "Already consuming topic: {}"
    KAFKA_TOPIC_NOT_EXIST = "Topic Not Exist"
    EXAMPLE_PRINT_CONSUMER_MSG = ", message is: {}"
