import threading
import time
import json
from typing import List

import zmq

from globals.enums.response_status import ResponseStatus
from globals.consts.consts import Consts
from globals.consts.const_strings import ConstStrings
from globals.consts.const_colors import ConstColors
from model.data_classes.zmq_request import Request
from model.data_classes.zmq_response import Response
from infrastructure.interfaces.izmq_server_manager import IZmqServerManager
from infrastructure.interfaces.iapi_router import IApiRouter
from infrastructure.factories.logger_factory import LoggerFactory
from globals.consts.logger_messages import LoggerMessages


class ZmqServerManager(IZmqServerManager):
    _TAG = LoggerMessages.TAG_ZMQ_SERVER
    _TAG_COLOR = ConstColors.YELLOW

    def __init__(self, host: str, port: int, routers: List[IApiRouter]):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._address = f"{ConstStrings.BASE_TCP_CONNECTION_STRINGS}{host}:{port}"
        self._is_running = False
        self._server_working_thread = None
        self._routers_dict: dict[str, IApiRouter] = {}
        self._logger = LoggerFactory.get_logger_manager()
        self._include_routers(routers)

    def _format_tagged(self, msg: str) -> str:
        return f"{self._TAG_COLOR}{self._TAG}{ConstColors.RESET} {msg}"

    def start(self) -> None:
        self._socket.bind(self._address)
        self._is_running = True
        self._server_working_thread = threading.Thread(
            target=self._server_working_handle,
            daemon=True,
        )
        self._server_working_thread.start()

        self._logger.log(
            ConstStrings.LOG_NAME_DEBUG,
            self._format_tagged(
                LoggerMessages.ZMQ_SERVER_BOUND_TO_ADDRESS.format(
                    self._address)
            ),
        )

    def stop(self) -> None:
        self._is_running = False
        if self._server_working_thread:
            self._server_working_thread.join()

        self._socket.close()
        self._context.term()

        self._logger.log(
            ConstStrings.LOG_NAME_DEBUG,
            self._format_tagged(LoggerMessages.ZMQ_SERVER_STOPPED),
        )

    def _server_working_handle(self) -> None:
        while self._is_running:
            try:
                request_json = self._socket.recv_json()
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    self._format_tagged(
                        LoggerMessages.ZMQ_SERVER_RECEIVED_RAW_REQUEST.format(
                            request_json
                        )
                    ),
                )

                try:
                    request = Request.from_json(json.dumps(request_json))
                except Exception as e:
                    self._logger.log(
                        ConstStrings.LOG_NAME_DEBUG,
                        self._format_tagged(
                            LoggerMessages.ZMQ_SERVER_PARSE_REQUEST_FAILED.format(
                                e)
                        ),
                    )
                    response = Response(
                        status=ResponseStatus.ERROR,
                        data={
                            ConstStrings.ERROR_MESSAGE: f"invalid request: {e}",
                        },
                    )
                else:
                    response = self._handle_request(request)

            except Exception as e:
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    self._format_tagged(
                        LoggerMessages.ZMQ_SERVER_SOCKET_LOOP_ERROR.format(e)
                    ),
                )
                response = Response(
                    status=ResponseStatus.ERROR,
                    data={ConstStrings.ERROR_MESSAGE: str(e)},
                )

            try:
                self._socket.send_json(response.to_json())
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    self._format_tagged(
                        LoggerMessages.ZMQ_SERVER_SENT_RESPONSE.format(
                            response.to_json()
                        )
                    ),
                )
            except Exception as e:
                self._logger.log(
                    ConstStrings.LOG_NAME_DEBUG,
                    self._format_tagged(
                        LoggerMessages.ZMQ_SERVER_SEND_ERROR.format(e)
                    ),
                )
                time.sleep(Consts.ZMQ_SERVER_LOOP_DURATION)

    def _handle_request(self, request: Request) -> Response:
        resource = request.resource
        operation = request.operation
        data = request.data

        self._logger.log(
            ConstStrings.LOG_NAME_DEBUG,
            self._format_tagged(
                LoggerMessages.ZMQ_SERVER_HANDLE_REQUEST.format(
                    resource, operation, data
                )
            ),
        )

        if resource in self._routers_dict:
            route = self._routers_dict[resource]
            return route.handle_operation(operation, data)
        else:
            return Response(
                status=ResponseStatus.ERROR,
                data={
                    ConstStrings.ERROR_MESSAGE: ConstStrings.UNKNOWN_RESOURCE_ERROR_MESSAGE
                },
            )

    def _include_routers(self, routers: List[IApiRouter]) -> None:
        for router in routers:
            self._routers_dict[router.resource] = router
