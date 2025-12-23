from typing import Dict, Optional

from globals.consts.const_strings import ConstStrings
from globals.consts.const_colors import ConstColors
from globals.enums.response_status import ResponseStatus
from infrastructure.interfaces.iexample_controller import IExampleController
from infrastructure.interfaces.ikafka_manager import IKafkaManager
from model.data_classes.zmq_response import Response
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.logger_messages import LoggerMessages


class ExampleController(IExampleController):
    _TAG = LoggerMessages.TAG_ZMQ_CONTROLLER
    _TAG_COLOR = ConstColors.RED

    def __init__(self, kafka_manager: IKafkaManager) -> None:
        self._kafka_manager = kafka_manager
        self._logger = LoggerFactory.get_logger_manager()

    def _format_tagged(self, msg: str) -> str:
        return f"{self._TAG_COLOR}{self._TAG}{ConstColors.RESET} {msg}"

    def example_function(self, data: Optional[Dict] = None) -> Response:
        data = data or {}

        topic = data.get("topic", ConstStrings.EXAMPLE_TOPIC)
        message = data.get("message")

        if message is None:
            self._logger.log(
                ConstStrings.LOG_NAME_DEBUG,
                self._format_tagged(
                    LoggerMessages.ZMQ_CONTROLLER_MISSING_FIELD
                ),
            )

            return Response(
                status=ResponseStatus.ERROR,
                data={ConstStrings.ERROR_MESSAGE: "missing 'message' field in data"},
            )

        processed_message = f"[ZMQ] {message}"

        self._kafka_manager.send_message(topic, processed_message)

        self._logger.log(
            ConstStrings.LOG_NAME_DEBUG,
            self._format_tagged(
                LoggerMessages.ZMQ_CONTROLLER_FORWARD_MESSAGE.format(
                    topic, processed_message
                )
            ),
        )

        return Response(
            status=ResponseStatus.SUCCESS,
            data={
                "sent": True,
                "topic": topic,
                "message": processed_message,
            },
        )
