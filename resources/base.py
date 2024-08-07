"""Base class for configuration."""
from RPA.Robocorp.WorkItems import WorkItems
import logging
from datetime import datetime
import os
from pathlib import Path
import configparser


class BaseProc(object):
    def __init__(self,
                 config_filename="config.ini",
                 config_context="DEFAULT"):
        self.config = None
        self.config_filename = config_filename
        self.config_context = config_context
        self.search_phrase = None
        self.topic = None
        self.number_of_months = None

        self.current_datetime = None
        self.log_filename = None
        self.url = None

        self.environment = "dev"
        if 'VIRTUAL_ENV' in os.environ:
            self.environment = "dev"

        if self.environment == "dev":
            self.dir_home = Path(os.getcwd())
        else:
            self.dir_home = Path(os.getcwd())

        self.dir_config = self.dir_home / "config"
        self.dir_output = self.dir_home / "output"

    def cargar_entorno(self):
        try:
            wi = WorkItems()
            wi.get_input_work_item()
            self.search_phrase = wi.get_work_item_variable("search_phrase")
            self.topic = wi.get_work_item_variable("topic")
            self.number_of_months = wi.get_work_item_variable(
                "number_of_months")
        except Exception:
            self.search_phrase = "climate change"
            self.topic = "California"
            self.number_of_months = 1
        self.current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = (
            self.dir_output / f'scraper_{self.current_datetime}.log')

        if not os.path.exists(self.dir_output):
            os.makedirs(self.dir_output)
        # Configure logging
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler(self.log_file),
                                logging.StreamHandler()
                            ])
        self.log = logging.getLogger(__name__)

        file_config = self.dir_config / self.config_filename
        config = configparser.ConfigParser()
        config.read(str(file_config))
        self.config_default = config[self.config_context]

        return self.log, self.config_default


base = BaseProc()
log, config = base.cargar_entorno()
