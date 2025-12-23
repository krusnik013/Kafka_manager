# infrastructure/factories/manager_factory.py

import os
from infrastructure.factories.infrastructure_factory import InfrastructureFactory
from infrastructure.interfaces.iexample_manager import IExampleManager
from infrastructure.interfaces.izmq_server_manager import IZmqServerManager
from model.managers.example_manager import ExampleManager
from infrastructure.factories.api_factory import ApiFactory


class ManagerFactory:
    _kafka_manager = None
    _zmq_server_manager = None
    _example_manager = None

    @staticmethod
    def _get_config_path() -> str:
        factories_dir = os.path.dirname(os.path.abspath(__file__))
        infra_root = os.path.dirname(factories_dir)
        return os.path.join(infra_root, "config", "configuration.xml")

    @staticmethod
    def _create_base_managers() -> IExampleManager:
        config_path = ManagerFactory._get_config_path()
        config_manager = InfrastructureFactory.create_config_manager(config_path)

        kafka_manager = InfrastructureFactory.create_kafka_manager(config_manager)
        ManagerFactory._kafka_manager = kafka_manager

        example_manager = ExampleManager(config_manager, kafka_manager)
        ManagerFactory._example_manager = example_manager
        return example_manager

    @staticmethod
    def _create_zmq_server() -> IZmqServerManager:
        kafka_manager = ManagerFactory._kafka_manager
        routers = ApiFactory.create_routers(kafka_manager)

        zmq_server_manager = InfrastructureFactory.create_zmq_server_manager(routers)
        zmq_server_manager.start()

        ManagerFactory._zmq_server_manager = zmq_server_manager
        return zmq_server_manager

    @staticmethod
    def create_producer_stack() -> None:
        example_manager = ManagerFactory._create_base_managers()
        example_manager.start_producers()

        ManagerFactory._create_zmq_server()

    @staticmethod
    def create_consumer_stack() -> None:
        example_manager = ManagerFactory._create_base_managers()
        example_manager.start_consumers()

    @staticmethod
    def create_all() -> None:
        example_manager = ManagerFactory._create_base_managers()
        example_manager.start_producers()
        example_manager.start_consumers()
        example_manager.start_zmq_test_client()
        ManagerFactory._create_zmq_server()
