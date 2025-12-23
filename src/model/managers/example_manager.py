import os
import time
import threading

import zmq

from infrastructure.interfaces.iexample_manager import IExampleManager
from infrastructure.interfaces.iconfig_manager import IConfigManager
from infrastructure.interfaces.ikafka_manager import IKafkaManager
from globals.consts.const_strings import ConstStrings
from globals.consts.consts import Consts
from globals.consts.logger_messages import LoggerMessages
from globals.consts.const_colors import ConstColors
from infrastructure.factories.logger_factory import LoggerFactory


class ExampleManager(IExampleManager):
    _TAG_ZMQ_CLIENT = LoggerMessages.TAG_ZMQ_CLIENT
    _TAG_ZMQ_CLIENT_COLOR = ConstColors.CYAN

    _TAG_KAFKA = LoggerMessages.TAG_KAFKA
    _TAG_KAFKA_COLOR = ConstColors.MAGENTA

    def __init__(
        self,
        config_manager: IConfigManager,
        kafka_manager: IKafkaManager,
    ) -> None:
        super().__init__()
        self._config_manager = config_manager
        self._kafka_manager = kafka_manager
        self._topic1 = ConstStrings.EXAMPLE_TOPIC
        self._topic2 = ConstStrings.ANOTHER_TOPIC

        self._logger = LoggerFactory.get_logger_manager()

    def start_producers(self) -> None:
        self._init_threading()

    def start_consumers(self) -> None:
        self._init_consumers()

    def start_zmq_test_client(self) -> None:
        self._init_zmq_test_client()

    def _format_tagged(self, tag: str, color: str, msg: str) -> str:
        return f"{color}{tag}{ConstColors.RESET} {msg}"

    def do_something(self) -> None:
        self._kafka_manager.send_message(
            self._topic1,
            "Manual do_something message",
        )

    def _init_threading(self) -> None:
        self._producer_thread_1 = threading.Thread(
            target=self._produce_topic1_messages,
        )
        self._producer_thread_1.start()

        self._producer_thread_2 = threading.Thread(
            target=self._produce_topic2_messages,
        )
        self._producer_thread_2.start()

    def _init_consumers(self) -> None:
        self._kafka_manager.start_consuming(
            self._topic1,
            self._print_consumer,
        )

        self._kafka_manager.start_consuming(
            self._topic2,
            self._print_consumer,
        )

    def _produce_topic1_messages(self) -> None:
        while True:
            time.sleep(Consts.SEND_MESSAGE_DURATION * 2)
            self._kafka_manager.send_message(
                self._topic1,
                ConstStrings.EXAMPLE_MESSAGE,
            )

    def _produce_topic2_messages(self) -> None:
        while True:
            time.sleep(Consts.SEND_MESSAGE_DURATION * 2)
            self._kafka_manager.send_message(
                self._topic2,
                ConstStrings.ANOTHER_MESSAGE,
            )

    def _print_consumer(self, topic: str, msg: str) -> None:
        TOPIC_COLORS = {
            ConstStrings.EXAMPLE_TOPIC: ConstColors.CYAN,
            ConstStrings.ANOTHER_TOPIC: ConstColors.MAGENTA,
        }

        topic_color = TOPIC_COLORS.get(topic, ConstColors.CYAN)

        colored_topic = f"{topic_color}[{topic}]{ConstColors.RESET}"
        colored_msg = (
            f"{ConstColors.BRIGHT_GREEN}"
            f"{LoggerMessages.EXAMPLE_PRINT_CONSUMER_MSG.format(msg)}"
            f"{ConstColors.RESET}"
        )

        kafka_line = f"{colored_topic} {colored_msg}"

        self._logger.log(
            ConstStrings.LOG_NAME_DEBUG,
            self._format_tagged(
                self._TAG_KAFKA,
                self._TAG_KAFKA_COLOR,
                kafka_line,
            ),
        )

    def _init_zmq_test_client(self) -> None:
        self._zmq_client_thread = threading.Thread(
            target=self._send_zmq_test_messages,
            daemon=True,
        )
        self._zmq_client_thread.start()

    def _create_zmq_socket(self, context: zmq.Context) -> zmq.Socket:
        host = os.getenv(ConstStrings.ZMQ_SERVER_HOST, "0.0.0.0")
        port = os.getenv(ConstStrings.ZMQ_SERVER_PORT, "5555")

        socket = context.socket(zmq.REQ)
        socket.connect(
            f"{ConstStrings.BASE_TCP_CONNECTION_STRINGS}{host}:{port}")
        socket.RCVTIMEO = 2000
        socket.SNDTIMEO = 2000
        return socket

    def _send_zmq_test_messages(self) -> None:
        context = zmq.Context.instance()
        socket = self._create_zmq_socket(context)

        counter = 0
        while True:
            time.sleep(10)

            message_text = f"Hello from internal ZMQ client #{counter}"
            counter += 1

            self._logger.log(
                ConstStrings.LOG_NAME_DEBUG,
                self._format_tagged(
                    self._TAG_ZMQ_CLIENT,
                    self._TAG_ZMQ_CLIENT_COLOR,
                    LoggerMessages.ZMQ_CLIENT_GENERATED_MESSAGE.format(
                        message_text),
                ),
            )

            request = {
                ConstStrings.RESOURCE_IDENTIFIER: ConstStrings.EXAMPLE_RESOURCE,
                ConstStrings.OPERATION_IDENTIFIER: ConstStrings.EXAMPLE_OPERATION,
                ConstStrings.DATA_IDENTIFIER: {
                    "topic": ConstStrings.EXAMPLE_TOPIC,
                    "message": message_text,
                },
            }

            try:
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    self._format_tagged(
                        self._TAG_ZMQ_CLIENT,
                        self._TAG_ZMQ_CLIENT_COLOR,
                        LoggerMessages.ZMQ_CLIENT_SENDING_REQUEST.format(
                            request),
                    ),
                )
                socket.send_json(request)

                try:
                    response = socket.recv_json()
                    self._logger.log(
                        ConstStrings.LOG_NAME_DEBUG,
                        self._format_tagged(
                            self._TAG_ZMQ_CLIENT,
                            self._TAG_ZMQ_CLIENT_COLOR,
                            LoggerMessages.ZMQ_CLIENT_RECEIVED_RESPONSE.format(
                                response
                            ),
                        ),
                    )
                except zmq.Again:
                    self._logger.log(
                        ConstStrings.LOG_NAME_DEBUG,
                        self._format_tagged(
                            self._TAG_ZMQ_CLIENT,
                            self._TAG_ZMQ_CLIENT_COLOR,
                            LoggerMessages.ZMQ_CLIENT_RECV_TIMEOUT,
                        ),
                    )
                    socket.close(0)
                    socket = self._create_zmq_socket(context)

            except zmq.ZMQError as e:
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    self._format_tagged(
                        self._TAG_ZMQ_CLIENT,
                        self._TAG_ZMQ_CLIENT_COLOR,
                        LoggerMessages.ZMQ_CLIENT_THREAD_ERROR.format(e),
                    ),
                )
                try:
                    socket.close(0)
                except Exception:
                    pass
                socket = self._create_zmq_socket(context)
