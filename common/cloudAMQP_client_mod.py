import pika
import logging
import json

logger_format = '%(asctime)s - %(message)s'
logging.basicConfig(format=logger_format)  # just stating the format in which log will be displayed
logger = logging.getLogger('cloud_amqp_client')  # name of the module i.e fnn for which the logger is defined
logger.setLevel(logging.DEBUG)  # level at which we want to see the message
CLOUDAMQP_URL= "amqp://hhtduhte:5P58DdmJNxV-uQ72qQx2zAFCiJPPYBB6@salamander.rmq.cloudamqp.com/hhtduhte"


class CloudAMQPClient:
    def __init__(self, cloudAMQP_url, queue_name):

        # from the other module
        self.cloudAMQP_url = cloudAMQP_url
        self.queue_name = queue_name
        # for setting up the configuration parameters
        self.params = pika.URLParameters(cloudAMQP_url)
        # to avoid connection timeout
        self.params.socket_timeout = 3
        # sets up a connection with CloudAMPQ
        self.connection = pika.BlockingConnection(self.params)
        # creates a channel
        self.channel = self.connection.channel()
        # declares a queue of name queue_name
        self.channel.queue_declare(queue=queue_name)

    def sendMessage(self, message):

        # will publlish the message to the channel and routing_key means that the message will be routed to the queue of queue_name
        # json.dumps() will serialize the obj to a json formatted stream
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(message))
        logger.debug("[x] send message to %s:%s", self.queue_name, message)

    def getMessage(self):

        # channel.basic_get() is to get a single msg from the broker
        method_frame, header_frame, body = self.channel.basic_get(self.queue_name) # I dont get the meaning behind using header_frame/body
        print(method_frame)
        if method_frame:
            logger.debug("[x] Received message from %s:%s", self.queue_name, body)
            # for getting acknowledgement
            # print(self.channel.basic_ack(method_frame.delivery_tag))
            return json.loads(body.decode('utf-8')) # json.loads() deserializes the stream
        else:
            logger.debug("No message returned")
            return None

    def sleep(self, seconds):
        self.connection.sleep(seconds)

