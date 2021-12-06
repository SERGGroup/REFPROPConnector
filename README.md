# REFPROP connector

__REFPROP connector__ is a tools developed by the [SERG research group](https://www.dief.unifi.it/vp-177-serg-group-english-version.html) 
of the [University of Florence](https://www.unifi.it/changelang-eng.html) for launching [REFPROP](https://www.nist.gov/srd/refprop) 
calculation and retrieving results from python. 

In order to use the code you must have both REFPROP and the [REFPROP wrappers for Python](https://github.com/usnistgov/REFPROP-wrappers) 
installed and properly working.

The scope of this library is to make the usage of the refprop wrappers simpler.

The beta version can be downloaded using __PIP__:

```
pip install REFPROP_connector
```
Once the installation has been completed the user can import the tool and initialize the connector itself.
```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint.init_from_fluid(["air"], [1.])

```
__An important aspects to keep in mind for the initialization:__

  * A file-dialog __could__ appear the first time that the connector is imported __asking the user to select the REFPROP 
    installation folder__ (usually it's _"C:\Program Files (x86)\REFPROP"_). 
    Once the executable path has been selected, the program will keep it in memory in order to avoid a new appearance 
    of the file-dialog. The stored executable can be modified calling the following function:
    
```python
from REFPROPConnector import retreive_RP_exec

retreive_RP_exec()
```
    

Each _ThermodynamicPoint_ class instance represent a thermodynamic state, hence you had to provide at least 
__two indipendent state variables__ in order to calculate the others.


```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint.init_from_fluid(["water"], [1.])

tp.set_variable("P", 0.101325)     # P in MPa (ambient pressure)
tp.set_variable("Q", 0.5)          # vapour quality for multiphase condition

T_sat = tp.get_variable("T")       # saturation temperature in celsius (100 °C)
```

Suitable state variables are:

  * Pressure __P__
  * Temperature __T__
  * Enthalpy __h__
  * Entropy __s__
  * Quality __Q__
  * Density __rho__
 

__-------------------------- !!! THIS IS A BETA VERSION !!! --------------------------__ 

please report any bug or problems in the installation to _pietro.ungar@unifi.it_<br/>
for further information visit: https://tinyurl.com/SERG-3ETool
