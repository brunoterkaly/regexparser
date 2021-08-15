from unittest.mock import patch
import os
import pytest
from unittest.mock import Mock, patch

from etl.src.etl_manager import EtlManager


@pytest.fixture()
def etl_manager():
    """Return main ETL Manager"""
    return EtlManager()

    
def test_etl_manager(etl_manager):
    assert etl_manager is not None



