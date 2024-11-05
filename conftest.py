import pytest
import json
import os
from utils.logger import logger
from utils.xml import BalanceXML, XMLObject
from model.Balance import Balance



def pytest_addoption(parser):
    parser.addoption( # Config path
        "--config",
        action="store",
        default="config.json",
        help="Path to the config file (default: config.json)"
    )


@pytest.fixture(scope="session")
def config_path(pytestconfig):
    """Fixture to get the path to the configuration file."""
    return pytestconfig.getoption("config")


@pytest.fixture(scope="session")
def config(config_path: str):
    """Fixture to load configuration data from a JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)
        logger.info(f"Using config '{config_path}'")
    return config


@pytest.fixture(scope="session")
def balance_xml_tree(config: dict):
    """Fixture to parse balance xml and return XML tree object"""
    xml_path = config["balances_xml"]["path"]
    xml_namespace = config["balances_xml"]["namespace"]
    return BalanceXML(xml_path, namespace=xml_namespace, encoding='utf-8')


@pytest.fixture(scope="session")
def balance(config, balance_xml_tree: BalanceXML):
    """Fixture for getting 'Balance' model"""
    return Balance(config["corr_account"], balance_xml_tree)


@pytest.fixture(scope="session")
def application_balances(config):
    return config["application_amounts"]


@pytest.fixture(scope="session")
def ed807_xml_tree(config: dict):
    """Fixture to parse ed807 xml and return XML tree object"""
    xml_path = config["ed807_xml"]["path"]
    xml_namespace = config["ed807_xml"]["namespace"]
    return XMLObject(xml_path, namespace=xml_namespace, encoding='windows-1251')


@pytest.fixture(scope="session")
def epd_xml_tree(config: dict):
    """Fixture to parse epd xml and return XML tree object"""
    xml_path = config["epd_xml"]["path"]
    return XMLObject(xml_path, encoding='windows-1251')