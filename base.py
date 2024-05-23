
import logging
from datetime import datetime
import os
from pathlib import Path


class BaseProc(object):
    def __init__(self):
        self.current_datetime = None
        self.log_filename = None

        self.environment = "prod"
        if 'VIRTUAL_ENV' in os.environ:
            self.environment = "dev"

        if self.environment == "dev":
            self.dir_home = Path(os.getcwd())
        else:
            self.dir_home = Path(os.getcwd())

        self.dir_log = self.dir_home / "logs"

    def cargar_entorno(self):
        self.current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.dir_log / f'scraper_{self.current_datetime}.log'
        # Configure logging
        logging.basicConfig(filename=self.log_file,
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        return self.log


base = BaseProc()
log = base.cargar_entorno()
