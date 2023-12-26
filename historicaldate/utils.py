import sys

def add_submodules_to_path():
    """  
    Allows code here to be written so that it works whether these packages
    are attached as submodules, or if they exist as packages in the environment
    """
    def add_submodule(path):
        if f"./{path}" not in sys.path:
            sys.path.insert(0,f"../{path}") # -- Needed for Sphinx builds, usually run in the docs subdirectory
            sys.path.insert(0,f"./{path}")  # -- For normall running. Add second so it will go first in the search order

    add_submodule("historicaldate")
