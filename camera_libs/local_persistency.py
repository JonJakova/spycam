import sys
import time
import os;
from os import path;
from decouple import config


class Persistency:

    def __init__(self) -> None:
        self.persistence_path = config('PERSISTENCE_PATH', default='./persistence')
        self.persistence_interval = int(config('PERSISTENCE_INTERVAL', default='1'))
        self.last_epoch_persistency = 0
        self._create_base_bir()


    def _create_base_bir(self):
        if not path.exists(self.persistence_path):
            os.makedirs(self.persistence_path)

        
    def save_image(self, image_name, image_data):
        try:
            if (time.time() - self.last_epoch_persistency) > self.persistence_interval:
                self.last_epoch_persistency = time.time()
                image_path = path.join(self.persistence_path, image_name)
                with open(image_path, 'wb') as f:
                    f.write(image_data)
        except:
            print("Error saving image: "), sys.exc_info()[0]
