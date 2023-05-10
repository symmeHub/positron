import os
import pwd
from string import Template
import json
import shutil
import hashlib

# LOCAL CONFIG
if not os.path.isfile("my_config.json"):
    shutil.copy("my_config_default.json", "my_config.json")
my_config = json.load(open("my_config.json"))
my_config_default = json.load(open("my_config_default.json"))
for k, v in my_config_default.items():
    if k not in my_config.keys():
        my_config[k] = v

# UNIQUE HASH VALUE
current_dir = os.getcwd()
# hash_value = hashlib.sha256(str.encode(current_dir)).hexdigest()
hash_value = "".join(current_dir.split("/")[-2])
user_name = os.environ.get("USER")

data = {
    "USER_NAME": user_name,
    "UID": str(pwd.getpwnam(os.environ.get("USER")).pw_uid),
    "GID": str(pwd.getpwnam(os.environ.get("USER")).pw_gid),
    "TAG": "0.0",
    "CONTAINER_NAME": f"{user_name}_{hash_value}",
    "GPU_COUNT": my_config["gpu_count"],
}

# TEMPLATE
dct = Template(open("docker-compose_template.yml").read().strip()).substitute(data)

my_volumes = my_config["volumes"]
if len(my_volumes) != 0:
    dct += "\n" + 4 * " " + "volumes:" + "\n" + 6 * " "
for volume in my_volumes:
    dct += "- {0}".format(volume)
    dct += "\n" + 6 * " "

dct = dct.strip()

open("docker-compose.yml", "w").write(dct)

# ENV FILE CREATION
open("../.env", "w").write(f"COMPOSE_PROJECT_NAME={user_name}_{hash_value}")

# # CUSTOM CONDA ENV CREATION
# if not os.path.isfile("my_environment.yml"):
#     shutil.copy("my_environment_example.yml", "my_environment.yml")
