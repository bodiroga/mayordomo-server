import os
import logging
import importlib

logger = logging.getLogger("nlp_providers_scanner")

folder = os.path.dirname(os.path.abspath(__file__))

__all__ = {}

for file in os.listdir(folder):
    file_path = "/".join((folder, file))
    if os.path.isdir(file_path):
        folder_path = file_path
        folder_name = file
        for file_in_folder in os.listdir(folder_path):
            base_file = file_in_folder.replace('.py', '')
            if base_file == folder_name:
                module_path = "{}.{}.{}".format(__name__, folder_name, base_file)
                module_name = base_file
                try:
                    module = importlib.import_module(module_path)
                    logger.debug("'{}' module loaded".format(module_name))
                except Exception as e:
                    logger.error("Error loading plugin located at {}: \n{}".format(module_path, e))
                else:
                    __all__[module_name] = module