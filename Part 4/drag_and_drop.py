from charge_objects import *
import datetime
import os


def exclamation(nombre):
    return nombre*"!\n"


#avoir dès le début les parties invariables des fichiers configs
def initialize_default_blocs():
    result_dict = {}
    with open("ressource_default_config.txt", "r") as default_parts_file:
        default_parts_list = default_parts_file.readlines()
        debut_bloc1 = default_parts_list.index("! DEBUT BLOC 1\n")
        fin_bloc1 = default_parts_list.index("! FIN BLOC 1\n")
        debut_bloc2 = default_parts_list.index("! DEBUT BLOC 2\n")
        fin_bloc2 = default_parts_list.index("! FIN BLOC 2\n")
        debut_bloc3 = default_parts_list.index("! DEBUT BLOC 3\n")
        fin_bloc3 = default_parts_list.index("! FIN BLOC 3\n")
        debut_bloc4 = default_parts_list.index("! DEBUT BLOC 4\n")
        fin_bloc4 = default_parts_list.index("! FIN BLOC 4\n")

        result_dict["BLOC 1"] = "".join(line for line in default_parts_list[(debut_bloc1 + 1):fin_bloc1])
        result_dict["BLOC 2"] = "".join(line for line in default_parts_list[(debut_bloc2 + 1):fin_bloc2])
        result_dict["BLOC 3"] = "".join(line for line in default_parts_list[(debut_bloc3 + 1):fin_bloc3])
        result_dict["BLOC 4"] = "".join(line for line in default_parts_list[(debut_bloc4 + 1):fin_bloc4])

    return result_dict

def bloc_interfaces(router):
    if len(router.interfaces)==0:
        print("Erreur config generation : le routeur "+router.router_hostname+" n'a pas d'interfaces")
    else:




def total_router_configuration(router, default):
    result_file = open("i"+str(router.router_hostname)+"_startup-config.cfg", "x")
    everything = "!\n ! Configuré automatiquement le "+datetime.datetime.now()+" \n!\n""
    everything += ""

    new_file_name = "i"+str(router.router_hostname)+"_startup-config.cfg"
    with open(new_file_name, "x") as result_file:
        everything += default["BLOC 1"]
        everything += exclamation(1)
        everything += "hostname R"+str(router.router_hostname)+"\n"
        everything += exclamation(1)
        everything += default["BLOC 2"]
        everything += exclamation(1)
        everything += bloc_interfaces(router)
        everything += exclamation(1)
        everything += bloc_bgp(router)
        everything += exclamation(1)
        everything += default["BLOC 3"]
        everything += exclamation(1)
        everything += bloc_intradom(router)
        everything += default["BLOC 4"]
        everything += exclamation(5)

    return everything


default_blocs = initialize_default_blocs()

