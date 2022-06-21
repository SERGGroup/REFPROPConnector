import os, shutil


def upload_files(activate_venv=True):

    venv_name = "venv"
    setup_cmd = "python setup.py sdist"

    if activate_venv:

        venv_script = "{VENV}\\Scripts\\python {VENV}\\Lib\\site-packages\\".format(

            VENV=venv_name

        )

    else:

        venv_script = ""

    twine_cmd = '{VENV_SCRIPT}twine upload dist/* -u {USER} -p {PSW} {OTHER}'.format(

        VENV_SCRIPT = venv_script,
        USER="__token__",
        PSW=__read_token(),
        OTHER="--verbose"

    )

    base_dir = os.path.dirname(os.path.dirname(__file__))
    os.chdir(base_dir)
    os.system(setup_cmd)
    os.system(twine_cmd)

    shutil.rmtree(os.path.join(base_dir, "dist"))
    for sub_dir in os.listdir(base_dir):
        if ".egg-info" in sub_dir:
            shutil.rmtree(os.path.join(base_dir, sub_dir))


def __read_token():

    with open("pipy_token", "r") as file:
        pypi_token = file.readline().strip("\n")

    return pypi_token


if __name__ == "__main__":
    upload_files(activate_venv=False)
