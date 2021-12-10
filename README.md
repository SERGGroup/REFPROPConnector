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

tp = ThermodynamicPoint(["air"], [1.])

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

tp = ThermodynamicPoint(["water"], [1.])

tp.set_variable("P", 0.101325)     # P in MPa (ambient pressure)
tp.set_variable("Q", 0.5)          # vapour quality for multiphase condition

T_sat = tp.get_variable("T")       # saturation temperature in celsius (100 °C)
```

_AbstractThermodynamicPoint_ is a class that can be overwritten in order to perform some calculation once both 
independent state variable have been set. It can be useful for example for the evaluation of the reynolds number 
for a fluid flowing in a pipe.

```python
from REFPROPConnector import AbstractThermodynamicPoint, RefPropHandler
import numpy as np


class TubeSection(AbstractThermodynamicPoint):

    def __init__(self, diam, flow_rate):
        
        self.diam = diam
        self.area = np.pi * np.power(diam / 2, 2)
        self.flow_rate = flow_rate
        self.Re = 0.
        
        refprop = RefPropHandler(["air"], [1])

        super().__init__(refprop)

    def other_calculation(self):
        
        mu = self.get_variable("mu") / (10 ** 6)  # conversion uPa*s -> Pa*s
        self.Re = self.flow_rate * self.diam / (self.area * mu)

if __name__ == "__main__":

    section = TubeSection(0.5, 1)
    
    """
    
        The following line will return 0. as the function "other_calculation" 
        is called only when 2 independent state variable is provided 
        
    """
    print(section.get_variable("Re"))   
    
    section.set_variable("P", 0.5)
    section.set_variable("T", 20)
    
    """
    
        The following line will return the actual Reynolds number
        
    """
    print(section.get_variable("Re"))
```

Variable that can be calculated can be listed using _list_properties_ method from both _ThermodynamicPoint_ and 
_AbstractThermodynamicPoint_ (the name __is not case-sensitive__). Finally, user can also select the unit system to be 
used in the calculation, a list of possible unit system can be revived calling the method _list_unit_systems()_ 
(current unit_system will be highlighted):  

```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint(["water"], [1.], unit_system="MASS BASE SI")
tp.list_properties()
tp.list_unit_systems()
```
Defaul unit system is __SI with C__

For other information please contact: _pietro.ungar@unifi.it_

__-------------------------- !!! THIS IS A BETA VERSION !!! --------------------------__ 

please report any bug or problems in the installation to _pietro.ungar@unifi.it_<br/>
for further information visit: https://tinyurl.com/SERG-3ETool
