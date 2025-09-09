# REFPROP connector

__REFPROP connector__ is a tool developed by the [SERG research group](https://www.dief.unifi.it/vp-177-serg-group-english-version.html) 
of the [University of Florence](https://www.unifi.it/changelang-eng.html) for launching [REFPROP](https://www.nist.gov/srd/refprop) 
calculations and retrieving results from Python. 

To use the code, you must have both REFPROP and the [REFPROP wrappers for Python](https://github.com/usnistgov/REFPROP-wrappers) 
installed and properly working.

The purpose of this library is to make the usage of the refprop wrappers simpler.

### Download and installation 

The beta version can be downloaded using __PIP__:

```
pip install REFPROP_connector
```

### First Steps
Once the installation is complete, you can import the tool and initialize the connector itself.
```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint(["air"], [1.])

```
__Important aspects to keep in mind for initialization:__

  * A file-dialog __may__ appear the first time the connector is imported __asking the user to select the REFPROP 
    installation folder__ (usually _"C:\Program Files (x86)\REFPROP"_). 
    Once the executable path has been selected, the program will keep it in memory to avoid a new appearance 
    of the file-dialog. The stored executable can be modified by calling the following function:
    
```python
from REFPROPConnector import retreive_RP_exec

retreive_RP_exec()
```

If you have multiple or conflicting REFPROP installations, you can force the program not to use the default executable 
path by using the option: 
```python
from REFPROPConnector import retreive_RP_exec

retreive_RP_exec(ignore_default=True)
```

Alternatively, you can explicitly provide the installation folder path using
```python
from REFPROPConnector import retreive_RP_exec

retreive_RP_exec(file_path="<your path to RP installation>")
```

__IMPORTANT:__ Each time you run *"retreive_RP_exec"* open the program that is executing your python code (such as the 
Terminal, PyCharm or Spider) in *administrator mode* otherwise the call may not have any effect.
    
### Basic Usage

Each _ThermodynamicPoint_ class instance represents a thermodynamic state, so you must provide at least 
__two independent state variables__ to calculate the others.


```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint(["water"], [1.])

tp.set_variable("P", 0.101325)     # P in MPa (ambient pressure)
tp.set_variable("Q", 0.5)          # vapour quality for multiphase condition

T_sat = tp.get_variable("T")       # saturation temperature in Celsius (100 °C)
```

### Abstract Class

_AbstractThermodynamicPoint_ is a class that can be overwritten to perform some calculation once both 
independent state variables have been set. It can be useful, for example, for the evaluation of the Reynolds number 
for a fluid flowing in a pipe.

```python
from REFPROPConnector import AbstractThermodynamicPoint, RefPropHandler, init_handler
import numpy as np


class TubeSection(AbstractThermodynamicPoint):

    def __init__(self, diam, flow_rate):
        
        self.diam = diam
        self.area = np.pi * np.power(diam / 2, 2)
        self.flow_rate = flow_rate
        self.Re = 0.
        
        refprop = init_handler(

            chosen_subclass=RefPropHandler,
            fluids=["air"], composition=[1]
            
        )

        super().__init__(refprop)

    def other_calculation(self):
        
        mu = self.get_variable("mu") / (10 ** 6)  # conversion uPa*s -> Pa*s
        self.Re = self.flow_rate * self.diam / (self.area * mu)

if __name__ == "__main__":

    section = TubeSection(0.5, 1)
    
    """
    
        The following line will return 0. as the function "other_calculation" 
        is called only when 2 independent state variables are provided 
        
    """
    print(section.get_variable("Re"))   
    
    section.set_variable("P", 0.5)
    section.set_variable("T", 20)
    
    """
    
        The following line will return the actual Reynolds number
        
    """
    print(section.get_variable("Re"))
```

### Unit system and state variable list

Variables that can be calculated can be listed using the _list_properties_ method from both _ThermodynamicPoint_ and 
_AbstractThermodynamicPoint_ (the name __is not case-sensitive__). Finally, the user can also select the unit system to be 
used in the calculation; a list of possible unit systems can be retrieved by calling the method _list_unit_systems()_ 
(current unit_system will be highlighted):  

```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint(["water"], [1.], unit_system="MASS BASE SI")
tp.list_properties()
tp.list_unit_systems()
```
Default unit system is __SI with C__

### Metastable Calculation

You can force the state to represent a metastable condition as follows:  

```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint(["water"], [1.], unit_system="MASS BASE SI")
tp.metastability = "liq" # or "vap" for vapour metastable condition
```
Acceptable keywords for metastability are ["liquid", "liq", "l", ">"] for the liquid metastable state, 
or ["vap", "vapour", "vapor", "v", "<"] for the vapour state (keywords **are not** case-sensitive).


### Static and Stagnation condition evaluation

You can evaluate either the static point given the total condition and the speed or the stagnation 
condition given the static ones by using the following commands:
```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint(["water"], [1.], unit_system="MASS BASE SI")
speed = 300     # m/s
static_point = tp.get_static_point(speed=speed)
total_point = tp.get_stagnation_point(speed=speed)

```
The speed value must be given in m/s!

### Diagram Plotter
The _DiagramPlotter_ class can be used to plot a specific state diagram that can then be used to describe state 
transformations. The diagram can be customized using the _DiagramPlotterOptions_ class. 
The following is an example of how to use the class.


```python
from REFPROPConnector import (
    
    ThermodynamicPoint, 
    DiagramPlotter, 
    DiagramPlotterOptions

)

tp = ThermodynamicPoint(["Carbon Dioxide"], [1])
options = DiagramPlotterOptions(

    x_variable="T",
    x_var_range = (0, 150), x_var_log=False,
    y_var_range = (4, 15),
    isoline_ranges={

        "rho": (50, 1000, 25),
        "H": (200, 550, 25)

    }

)
plotter = DiagramPlotter(tp, options=options)
plotter.calculate()

fig, (ax_1) = plt.subplots(1, 1, dpi=200)
fig.set_size_inches(10, 5)
plotter.plot(ax_1)
plt.show()
```

### Uncertainty Calculation

The connector allows you to manage and calculate the uncertainty of thermodynamic variables through error propagation.  
You can set the relative uncertainty (as a fraction, e.g. 0.01 for 1%) on input variables and calculate the uncertainty on derived variables.

#### Setting the uncertainty

```python
from REFPROPConnector import ThermodynamicPoint

tp = ThermodynamicPoint(["water"], [1.])
tp.set_variable("P", 0.101325)
tp.set_variable("T", 100)

# Set relative uncertainty on pressure and temperature
tp.set_relative_uncertainty("P", 0.01)  # 1% on pressure
tp.set_relative_uncertainty("T", 0.005) # 0.5% on temperature
```

#### Calculating uncertainty on a derived variable

Uncertainty is calculated by error propagation considering the partial derivatives with respect to the inputs:

```python
# Calculate absolute uncertainty on density
rho_unc = tp.get_absolute_uncertainty("rho")
print("Uncertainty on density:", rho_unc)
```

You can also convert the uncertainty to another unit system:

```python
rho_unc_SI = tp.get_absolute_uncertainty("rho", other_unit_system="SI BASE")
```

The `get_uncertainty` method uses error propagation considering the uncertainties set on the input variables (typically the first two independent variables defined).

__-------------------------- !!! THIS IS A BETA VERSION !!! --------------------------__ 

please report any bug or problems in the installation to _pietro.ungar@unifi.it_<br/>

