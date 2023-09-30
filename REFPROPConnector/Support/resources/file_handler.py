from REFPROPConnector.Support.resources.rp_names_file_generator import generate_rp_name_file
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
import xml.etree.ElementTree as ETree
from tkinter import filedialog as fd
import tkinter as tk
import os

__CURRENT_DIR = os.path.dirname(__file__)
__REFPROP_NAMES_FILE = 'REFPROP_names.xml'
__REFPROP_EXECUTABLE_PATH_FILE = 'REFPROP_exec.dat'
__REFPROP_PATH_FILE = os.path.join(__CURRENT_DIR, __REFPROP_EXECUTABLE_PATH_FILE)

# ---------------------------------
# ---------------------------------

# REFPROP EXECUTABLE IDENTIFICATION

# ---------------------------------
# ---------------------------------


def retreive_RP_exec(failure_possible=True):

    try:

        __RP_PATH = os.environ['RPPREFIX']

    except:

        root = tk.Tk()
        root.withdraw()
        __RP_PATH = fd.askdirectory(

            title='select REFPROP directory'

        )
        root.destroy()

    if os.path.isdir(__RP_PATH):

        try:

            REFPROPFunctionLibrary(__RP_PATH)

        except:

            raise FileNotFoundError(

                ("\n\nthe provided REFPROP executable does not work\n\n"
                 "\tExecutable provided: {}\n\n"
                 "Execution will stop!\n\n").format(__RP_PATH)

            )

        else:

            with open(__REFPROP_PATH_FILE, "w") as f:

                f.write(__RP_PATH)

            return __RP_PATH

    if not failure_possible:

        raise FileNotFoundError(

            ("\n\nREFPROP executable path must be provided!\n\n"
             "\t{} is not a suitable path\n\n"
             "Execution will stop!\n\n").format(__RP_PATH)

        )

    return None

RP_EXEC = None

if os.path.isfile(__REFPROP_PATH_FILE):

    if os.path.isfile(__REFPROP_PATH_FILE):

        with open(__REFPROP_PATH_FILE) as f:
            lines = f.readlines()

        if os.path.isfile(str(lines[0])):
            RP_EXEC = str(lines[0])

if RP_EXEC is None:

    RP_EXEC = retreive_RP_exec(failure_possible=False)


# ----------------------------------
# ----------------------------------

#       REFPROP NAMES XML

# ----------------------------------
# ----------------------------------

def _import_refprop_xml_files():

    file_path = os.path.join(__CURRENT_DIR, __REFPROP_NAMES_FILE)

    if not os.path.isfile(file_path):

        generate_rp_name_file()

def get_refprop_name_xml(get_derivatives_xml=False, get_converter=False) -> ETree.Element:

    _import_refprop_xml_files()
    file_path = os.path.join(__CURRENT_DIR, __REFPROP_NAMES_FILE)

    if os.path.isfile(file_path):

        tree = ETree.parse(file_path)
        root = tree.getroot()

        if get_derivatives_xml:

            return root.find("derivatives")

        if get_converter:

            return root.find("unit_conversion")

        return root.find("names")
