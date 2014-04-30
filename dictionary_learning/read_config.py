# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ ="$Apr 30, 2014 4:54:30 PM$"


# Need in order to have logging information no matter what.
import advanced_debugging


# Get the logger
logger = advanced_debugging.logging.getLogger(__name__)



@advanced_debugging.log_call(logger, print_args = True)
def read_parameters(config_filename):
    """
        Reads the contents of a json config file and returns the parameters.
        
        Args:
            config_filename:     name of the file to read.
        
        Keyword Args:
            print_args (bool):   whether to output arguments and keyword arguments passed to the function.
        
        Returns:
            dict: parameters read from the file.
    """
    
    
    # only relevant if reading parameter file.
    import json

    # gets parameters out of the file and dumps them in the dictionary. just that simple.
    parameters = {}
    with open(config_filename, 'r') as fp:
        logger.debug("Opened configure file named \"" + config_filename + "\".")
        
        # will just give a dictionary. just that simple
        parameters = json.load(fp)
        
        logger.debug("Loaded parameters from file, which are \"" + str(parameters) + "\".")

    return(parameters)
