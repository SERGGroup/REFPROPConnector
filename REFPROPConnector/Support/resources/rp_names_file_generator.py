import os

__CURR_DIR = os.path.dirname(__file__)
__RP_NAMES_TXT = """<?xml version="1.0" encoding="UTF-8" ?>
<data>

    <names>

        <refprop_name name = "P">

            <std_names>

                <std_name name="Pressure"/>
                <std_name name="Pres"/>
                <std_name name="Press"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "kPa" />
                <unit name = "MOLE SI"          unit = "MPa" />
                <unit name = "MASS SI"          unit = "MPa" />
                <unit name = "SI WITH C"        unit = "MPa" />

                <unit name = "MOLAR BASE SI"    unit = "Pa"  />
                <unit name = "MASS BASE SI"     unit = "Pa"  />
                <unit name = "ENGLISH"          unit = "psia"/>
                <unit name = "MOLAR ENGLISH"    unit = "psia"/>

                <unit name = "MKS"              unit = "kPa" />
                <unit name = "CGS"              unit = "MPa" />
                <unit name = "MIXED"            unit = "psia"/>
                <unit name = "MEUNITS"          unit = "bar" />

            </units>

        </refprop_name>
        <refprop_name name = "T">

            <std_names>

                <std_name name="Temperature"/>
                <std_name name="Temp"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "K" />
                <unit name = "MOLE SI"          unit = "K" />
                <unit name = "MASS SI"          unit = "K" />
                <unit name = "SI WITH C"        unit = "C" />

                <unit name = "MOLAR BASE SI"    unit = "K" />
                <unit name = "MASS BASE SI"     unit = "K" />
                <unit name = "ENGLISH"          unit = "F" />
                <unit name = "MOLAR ENGLISH"    unit = "F" />

                <unit name = "MKS"              unit = "K" />
                <unit name = "CGS"              unit = "K" />
                <unit name = "MIXED"            unit = "K" />
                <unit name = "MEUNITS"          unit = "C" />

            </units>

        </refprop_name>
        <refprop_name name = "D">

            <std_names>

                <std_name name="rho"/>
                <std_name name="density"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "mol/dm^3" />
                <unit name = "MOLE SI"          unit = "mol/dm^3" />
                <unit name = "MASS SI"          unit = "kg/m^3" />
                <unit name = "SI WITH C"        unit = "kg/m^3" />

                <unit name = "MOLAR BASE SI"    unit = "mol/m^3" />
                <unit name = "MASS BASE SI"     unit = "kg/m^3" />
                <unit name = "ENGLISH"          unit = "lbm/ft^3" />
                <unit name = "MOLAR ENGLISH"    unit = "lbmol/ft^3" />

                <unit name = "MKS"              unit = "kg/m^3" />
                <unit name = "CGS"              unit = "g/cm^3" />
                <unit name = "MIXED"            unit = "g/cm^3" />
                <unit name = "MEUNITS"          unit = "g/cm^3" />

            </units>

        </refprop_name>
        <refprop_name name = "E">

            <std_names>

                <std_name name="u"/>
                <std_name name="internal_energy"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "J/mol" />
                <unit name = "MOLE SI"          unit = "J/mol" />
                <unit name = "MASS SI"          unit = "J/g" />
                <unit name = "SI WITH C"        unit = "J/g" />

                <unit name = "MOLAR BASE SI"    unit = "J/mol" />
                <unit name = "MASS BASE SI"     unit = "J/kg" />
                <unit name = "ENGLISH"          unit = "BTU/lbm" />
                <unit name = "MOLAR ENGLISH"    unit = "BTU/lbmol" />

                <unit name = "MKS"              unit = "J/g" />
                <unit name = "CGS"              unit = "J/g" />
                <unit name = "MIXED"            unit = "J/g" />
                <unit name = "MEUNITS"          unit = "J/g" />

            </units>

        </refprop_name>
        <refprop_name name = "H">

            <std_names>

                <std_name name="enthalpy"/>
                <std_name name="enth"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "J/mol" />
                <unit name = "MOLE SI"          unit = "J/mol" />
                <unit name = "MASS SI"          unit = "J/g" />
                <unit name = "SI WITH C"        unit = "J/g" />

                <unit name = "MOLAR BASE SI"    unit = "J/mol" />
                <unit name = "MASS BASE SI"     unit = "J/kg" />
                <unit name = "ENGLISH"          unit = "BTU/lbm" />
                <unit name = "MOLAR ENGLISH"    unit = "BTU/lbmol" />

                <unit name = "MKS"              unit = "J/g" />
                <unit name = "CGS"              unit = "J/g" />
                <unit name = "MIXED"            unit = "J/g" />
                <unit name = "MEUNITS"          unit = "J/g" />

            </units>

        </refprop_name>
        <refprop_name name = "S">

            <std_names>

                <std_name name="entropy"/>
                <std_name name="entr"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "J/(mol * K)" />
                <unit name = "MOLE SI"          unit = "J/(mol * K)" />
                <unit name = "MASS SI"          unit = "J/(g * K)" />
                <unit name = "SI WITH C"        unit = "J/(g * K)" />

                <unit name = "MOLAR BASE SI"    unit = "J/(mol * K)" />
                <unit name = "MASS BASE SI"     unit = "J/(kg * K)" />
                <unit name = "ENGLISH"          unit = "BTU/(lbm * R)" />
                <unit name = "MOLAR ENGLISH"    unit = "BTU/(lbmol * R)" />

                <unit name = "MKS"              unit = "J/(g * K)" />
                <unit name = "CGS"              unit = "J/(g * K)" />
                <unit name = "MIXED"            unit = "J/(g * K)" />
                <unit name = "MEUNITS"          unit = "J/(g * K)" />

            </units>

        </refprop_name>
        <refprop_name name = "Q">

            <std_names>

                <std_name name="quality"/>
                <std_name name="x"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = " - " />
                <unit name = "MOLE SI"          unit = " - " />
                <unit name = "MASS SI"          unit = " - " />
                <unit name = "SI WITH C"        unit = " - " />

                <unit name = "MOLAR BASE SI"    unit = " - " />
                <unit name = "MASS BASE SI"     unit = " - " />
                <unit name = "ENGLISH"          unit = " - " />
                <unit name = "MOLAR ENGLISH"    unit = " - " />

                <unit name = "MKS"              unit = " - " />
                <unit name = "CGS"              unit = " - " />
                <unit name = "MIXED"            unit = " - " />
                <unit name = "MEUNITS"          unit = " - " />

            </units>

        </refprop_name>
        <refprop_name name = "VIS">

            <std_names>

                <std_name name="mu"/>
                <std_name name="viscosity"/>
                <std_name name="visc"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "uPa * s" />
                <unit name = "MOLE SI"          unit = "uPa * s" />
                <unit name = "MASS SI"          unit = "uPa * s" />
                <unit name = "SI WITH C"        unit = "uPa * s" />

                <unit name = "MOLAR BASE SI"    unit = "Pa * s" />
                <unit name = "MASS BASE SI"     unit = "Pa * s" />
                <unit name = "ENGLISH"          unit = "lbm/(ft * s)" />
                <unit name = "MOLAR ENGLISH"    unit = "lbm/(ft * s)" />

                <unit name = "MKS"              unit = "uPa * s" />
                <unit name = "CGS"              unit = "uPa * s" />
                <unit name = "MIXED"            unit = "uPa * s" />
                <unit name = "MEUNITS"          unit = "cpoise" />

            </units>

        </refprop_name>
        <refprop_name name = "TCX">

            <std_names>

                <std_name name="thermal_conductivity"/>
                <std_name name="k"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "W/(m * K)" />
                <unit name = "MOLE SI"          unit = "mW/(m * K)" />
                <unit name = "MASS SI"          unit = "mW/(m * K)" />
                <unit name = "SI WITH C"        unit = "mW/(m * K)" />

                <unit name = "MOLAR BASE SI"    unit = "W/(m * K)" />
                <unit name = "MASS BASE SI"     unit = "W/(m * K)" />
                <unit name = "ENGLISH"          unit = "BTU/(h * ft * R)" />
                <unit name = "MOLAR ENGLISH"    unit = "BTU/(h * ft * R)" />

                <unit name = "MKS"              unit = "W/(m * K)" />
                <unit name = "CGS"              unit = "mW/(m * K)" />
                <unit name = "MIXED"            unit = "mW/(m * K)" />
                <unit name = "MEUNITS"          unit = "mW/(m * K)" />

            </units>

        </refprop_name>
        <refprop_name name = "CP">

            <std_names>

                <std_name name="cp"/>
                <std_name name="isochoric_heat_capacity"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "J/(mol * K)" />
                <unit name = "MOLE SI"          unit = "J/(mol * K)" />
                <unit name = "MASS SI"          unit = "J/(g * K)" />
                <unit name = "SI WITH C"        unit = "J/(g * K)" />

                <unit name = "MOLAR BASE SI"    unit = "J/(mol * K)" />
                <unit name = "MASS BASE SI"     unit = "J/(kg * K)" />
                <unit name = "ENGLISH"          unit = "BTU/(lbm * R)" />
                <unit name = "MOLAR ENGLISH"    unit = "BTU/(lbmol * R)" />

                <unit name = "MKS"              unit = "J/(g * K)" />
                <unit name = "CGS"              unit = "J/(g * K)" />
                <unit name = "MIXED"            unit = "J/(g * K)" />
                <unit name = "MEUNITS"          unit = "J/(g * K)" />

            </units>

        </refprop_name>
        <refprop_name name = "CV">

            <std_names>

                <std_name name="cv"/>
                <std_name name="isobaric_heat_capacity"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "J/(mol * K)" />
                <unit name = "MOLE SI"          unit = "J/(mol * K)" />
                <unit name = "MASS SI"          unit = "J/(g * K)" />
                <unit name = "SI WITH C"        unit = "J/(g * K)" />

                <unit name = "MOLAR BASE SI"    unit = "J/(mol * K)" />
                <unit name = "MASS BASE SI"     unit = "J/(kg * K)" />
                <unit name = "ENGLISH"          unit = "BTU/(lbm * R)" />
                <unit name = "MOLAR ENGLISH"    unit = "BTU/(lbmol * R)" />

                <unit name = "MKS"              unit = "J/(g * K)" />
                <unit name = "CGS"              unit = "J/(g * K)" />
                <unit name = "MIXED"            unit = "J/(g * K)" />
                <unit name = "MEUNITS"          unit = "J/(g * K)" />

            </units>

        </refprop_name>
        <refprop_name name = "CP/CV">

            <std_names>

                <std_name name="gamma"/>
                <std_name name="cp/cv"/>
                <std_name name="heat_capacity_ratio"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = " - " />
                <unit name = "MOLE SI"          unit = " - " />
                <unit name = "MASS SI"          unit = " - " />
                <unit name = "SI WITH C"        unit = " - " />

                <unit name = "MOLAR BASE SI"    unit = " - " />
                <unit name = "MASS BASE SI"     unit = " - " />
                <unit name = "ENGLISH"          unit = " - " />
                <unit name = "MOLAR ENGLISH"    unit = " - " />

                <unit name = "MKS"              unit = " - " />
                <unit name = "CGS"              unit = " - " />
                <unit name = "MIXED"            unit = " - " />
                <unit name = "MEUNITS"          unit = " - " />

            </units>

        </refprop_name>
        <refprop_name name = "W">

            <std_names>

                <std_name name="c"/>
                <std_name name="sos"/>
                <std_name name="speed_of_sound"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = "m/s" />
                <unit name = "MOLE SI"          unit = "m/s" />
                <unit name = "MASS SI"          unit = "m/s" />
                <unit name = "SI WITH C"        unit = "m/s" />

                <unit name = "MOLAR BASE SI"    unit = "m/s" />
                <unit name = "MASS BASE SI"     unit = "m/s" />
                <unit name = "ENGLISH"          unit = "ft/s" />
                <unit name = "MOLAR ENGLISH"    unit = "ft/s" />

                <unit name = "MKS"              unit = "m/s" />
                <unit name = "CGS"              unit = "cm/s" />
                <unit name = "MIXED"            unit = "m/s" />
                <unit name = "MEUNITS"          unit = "cm/s" />

            </units>

        </refprop_name>
        <refprop_name name = "PRANDTL">

            <std_names>

                <std_name name="Pr"/>

            </std_names>
            <units>

                <unit name = "DEFAULT"          unit = " - " />
                <unit name = "MOLE SI"          unit = " - " />
                <unit name = "MASS SI"          unit = " - " />
                <unit name = "SI WITH C"        unit = " - " />

                <unit name = "MOLAR BASE SI"    unit = " - " />
                <unit name = "MASS BASE SI"     unit = " - " />
                <unit name = "ENGLISH"          unit = " - " />
                <unit name = "MOLAR ENGLISH"    unit = " - " />

                <unit name = "MKS"              unit = " - " />
                <unit name = "CGS"              unit = " - " />
                <unit name = "MIXED"            unit = " - " />
                <unit name = "MEUNITS"          unit = " - " />

            </units>

        </refprop_name>

    </names>
    <derivatives>

        <main_derivatives_prop>

            <refprop_name name = "P"/>
            <refprop_name name = "T"/>
            <refprop_name name = "D"/>

        </main_derivatives_prop>
        <other_derivatives_prop>

            <refprop_name name = "H"/>
            <refprop_name name = "S"/>

        </other_derivatives_prop>

    </derivatives>

</data>
"""

def generate_rp_name_file():

    rp_names_path = os.path.join(__CURR_DIR, "REFPROP_names.xml")

    with open(rp_names_path, "w") as file:

        file.write(__RP_NAMES_TXT)