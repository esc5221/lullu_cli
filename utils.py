import os
import importlib


def import_submodules(package_name, directory):
    if "__init__" in package_name:
        package_name = package_name.split(".__init__")[0]
        
    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("_"):
            module_name = filename[:-3]  # Remove the .py extension
            full_module_name = f"{package_name}.{module_name}"
            module = importlib.import_module(full_module_name)
            globals()[module_name] = module
