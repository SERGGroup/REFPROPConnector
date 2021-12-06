from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
import xml.etree.ElementTree as ETree
from tkinter import filedialog as fd
import pyrebase.pyrebase as pyrebase
from abc import ABC, abstractmethod
import os, requests
import tkinter as tk

CURRENT_DIR = os.path.dirname(__file__)
REFPROP_NAMES_FILE = 'REFPROP_names.xml'
REFPROP_EXECUTABLE_PATH_FILE = 'REFPROP_exec.dat'
__REFPROP_PATH_FILE = os.path.join(CURRENT_DIR, REFPROP_EXECUTABLE_PATH_FILE)


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

#   REFPROP NAMES TREE GENERATION

# ----------------------------------
# ----------------------------------

__FIREBASE_CONFIG = {

    "apiKey": "AIzaSyAWsQRNINNXzG87y4V9esY5NlcE9wbvdHY",
    "databaseURL": "https://serg-group-repository-default-rtdb.europe-west1.firebasedatabase.app",
    "authDomain": "serg-group-repository.firebaseapp.com",
    "projectId": "serg-group-repository",
    "storageBucket": "serg-group-repository.appspot.com",
    "messagingSenderId": "619279827614",
    "appId": "1:619279827614:web:563caa97267504b223718f",
    "measurementId": "G-007NTLM8RC"

}
__FIREBASE_TOKENS = {

    REFPROP_NAMES_FILE: "0528df42-3410-4674-b6b7-22610eb1b49d"

}


def _import_refprop_xml_files():
    for file_name in [REFPROP_NAMES_FILE]:

        file_path = os.path.join(CURRENT_DIR, file_name)

        if not os.path.isfile(file_path):

            try:

                firebase = pyrebase.initialize_app(__FIREBASE_CONFIG)
                storage = firebase.storage()
                storage.child("BHEModel/REFPROP_names.xml").download("", file_path, __FIREBASE_TOKENS[file_name])

                if not os.path.isfile(file_path):

                    url = storage.child("BHEModel/REFPROP_names.xml").get_url(__FIREBASE_TOKENS[file_name])
                    headers = {"Authorization": "Firebase " + __FIREBASE_TOKENS[file_name]}
                    r = requests.get(url, stream=True, headers=headers)

                    if r.status_code == 200:

                        return ETree.fromstring(r.content.decode("utf-8"))

                    else:

                        raise Exception("Unable to reach firebase storage, check your internet connection")

            except:

                raise Exception("Unable to reach firebase storage, check your internet connection")


def _get_refprop_name_xml(file_name) -> ETree.Element:
    _import_refprop_xml_files()

    if os.path.isfile(os.path.join(CURRENT_DIR, file_name)):
        tree = ETree.parse(os.path.join(CURRENT_DIR, file_name))
        return tree.getroot()


class __AbstractTree(ABC):

    def __init__(self):

        self.std_name = None
        self.left_tree = None
        self.right_tree = None

    def append_value(self, input_std_name, value):

        if self.is_empty:

            self.std_name = input_std_name
            self.init_value(value)

            self.left_tree = self.init_empty_self()
            self.right_tree = self.init_empty_self()

        else:

            if self.std_name < input_std_name:

                self.right_tree.append_value(input_std_name, value)

            elif self.std_name > input_std_name:

                self.left_tree.append_value(input_std_name, value)

    def find_element(self, input_std_name):

        if self.is_empty:

            return None

        else:

            if self.std_name == input_std_name:

                return self

            elif self.std_name < input_std_name:

                return self.right_tree.find_element(input_std_name)

            else:

                return self.left_tree.find_element(input_std_name)

    @property
    def is_empty(self):

        return self.std_name is None

    @abstractmethod
    def init_value(self, value):
        pass

    @classmethod
    @abstractmethod
    def init_empty_self(self):
        pass


class __RefPropNamesTree(__AbstractTree):

    def __init__(self):

        super().__init__()
        self.refprop_name = None
        self.units_dict = None

    def init_value(self, value):

        self.refprop_name = value["RP_Name"]
        self.units_dict = value["units_dict"]

    @classmethod
    def initialize_from_xml(cls):

        refprop_names_tree = cls()
        root = _get_refprop_name_xml(REFPROP_NAMES_FILE)

        for element in root.findall("refprop_name"):

            ref_prop_name = element.attrib["name"].lower()

            unit_dict = dict()

            for unit in element.find("units").findall("unit"):
                unit_dict.update({unit.attrib["name"]: unit.attrib["unit"]})

            value_dict = {"RP_Name": ref_prop_name, "units_dict": unit_dict}

            refprop_names_tree.append_value(ref_prop_name, value_dict)

            for std_name in element.find("std_names").findall("std_name"):
                refprop_names_tree.append_value(std_name.attrib["name"].lower(), value_dict)

        return refprop_names_tree

    @classmethod
    def init_empty_self(cls):

        return cls()

    def get_refprop_name(self, input_std_name):

        element_found = self.find_element(input_std_name)

        if element_found is not None:

            return element_found.refprop_name

        return None

    def get_units_dict(self, input_std_name):

        element_found = self.find_element(input_std_name)

        if element_found is not None:
            return element_found.units_dict

        return None

    def append_refprop_names(self, initial_list: list)->list:

        if self.is_empty:

            return initial_list

        else:

            new_list = self.right_tree.append_refprop_names(initial_list)
            new_list = self.left_tree.append_refprop_names(new_list)

            if self.refprop_name not in initial_list:

                new_list.append(self.refprop_name)

            return new_list


__REFPROP_NAME_TREE = __RefPropNamesTree.initialize_from_xml()


def get_refprop_name(name: str):

    return __REFPROP_NAME_TREE.get_refprop_name(name.lower())


def get_units(name: str, unit_system: str):

    unit_system = unit_system.upper()
    units_dict = __REFPROP_NAME_TREE.get_units_dict(name.lower())

    if units_dict is not None:

        if unit_system in units_dict.keys():

            return units_dict[unit_system]

        else:

            return "Unknown Unit System {}".format(unit_system)

    else:

        return "Unknown property name {}".format(name)


def get_all_refprop_names():

    return __REFPROP_NAME_TREE.append_refprop_names(list())