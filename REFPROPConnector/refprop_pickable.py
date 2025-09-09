from .refprop_calculator import AbstractThermodynamicPoint
from .Handlers.refprop_handler_picklable import RefPropHandler


class ThermodynamicPoint(AbstractThermodynamicPoint):

    def __init__(self, fluids: list, composition: list, rp_handler=None, other_variables="all", calculate_on_need="all",
                 unit_system="SI WITH C"):

        if rp_handler is None:
            rp_handler = RefPropHandler(fluids, composition, unit_system)

        super().__init__(rp_handler, other_variables=other_variables, calculate_on_need=calculate_on_need)

    def other_calculation(self):
        pass

    @classmethod
    def init_from_fluid(cls, fluids: list, composition: list, other_variables="all", calculate_on_need="all", unit_system="SI WITH C"):

        return ThermodynamicPoint(fluids, composition, other_variables, calculate_on_need, unit_system)

    def duplicate(self):

        tp = ThermodynamicPoint(

            self.RPHandler.fluids,
            self.RPHandler.composition,
            rp_handler=self.RPHandler,
            unit_system=self.RPHandler.unit_system,
            other_variables=self.inputs["other_variables"],
            calculate_on_need=self.inputs["calculate_on_need"]

        )

        self.copy_state_to(tp)
        return tp

    def get_alternative_unit_system(self, new_unit_system):

        rp_handler = RefPropHandler(self.RPHandler.fluids, self.RPHandler.composition, unit_system=new_unit_system)

        tp = ThermodynamicPoint(

            self.RPHandler.fluids,
            self.RPHandler.composition,
            rp_handler=rp_handler,
            unit_system=new_unit_system,
            other_variables=self.inputs["other_variables"],
            calculate_on_need=self.inputs["calculate_on_need"]

        )

        self.copy_state_to(tp)
        return tp
