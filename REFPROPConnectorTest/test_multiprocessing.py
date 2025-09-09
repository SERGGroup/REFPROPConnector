from REFPROPConnector.refprop_calculator import ThermodynamicPoint
import multiprocessing
import random

def worker_function(curr_fluids):

    enthalpies = dict()
    text_return = ""
    for fluid in curr_fluids:

        tp = ThermodynamicPoint([fluid], [1])  # Make sure this is picklable!

        tp.set_variable("T", 10)
        tp.set_variable("P", 0.1)
        h_0 = tp.get_variable("H")
        enthalpies.update({fluid: tp.get_variable("H")})
        text_return += f" {fluid}: {h_0:.2f}-{tp.RPHandler.global_counter},"

    try:
        return text_return
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":

    multiprocessing.set_start_method("spawn", force=True)

    fluids = [

        "Water",
        "Air",
        "Carbon dioxide",
        "Propane",
        "Ammonia",
        "Methane",
        "Ethanol",
        "R134a",
        "Nitrogen",
        "Hydrogen"

    ]

    # Generate 10 shuffled (swapped) versions of the fluid list
    shuffled_fluid_lists = []

    for _ in range(10):
        shuffled = fluids.copy()
        random.shuffle(shuffled)
        shuffled_fluid_lists.append(shuffled)

    with multiprocessing.Pool(processes=len(fluids)) as pool:
        results = pool.map(worker_function, shuffled_fluid_lists)

    for i, result in enumerate(results):
        print(f"Process {i + 1}: {result}")
