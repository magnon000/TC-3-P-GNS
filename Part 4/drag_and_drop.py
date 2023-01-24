from charge_objects import *
from instruments import *
import datetime
import os


def exclamation(nombre):
    return nombre * "!\n"


# avoir dès le début les parties invariables des fichiers configs
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

def petite_ligne_interface_protocole(protocole, routeur):
    if protocole == "rip":
        return " ipv6 rip AS" + routeur.parent_AS.AS_number + "rip enable\n"
    elif protocole == "ospf":
        return " ipv6 ospf" + routeur.parent_AS.AS_number + "area 0\n"

def bloc_interfaces(protocole, routeur: object):
    resultat = "!\n"
    liste_interfaces = routeur.get_sorted_list_of_interfaces()
    if len(routeur.interfaces) == 0:
        print("Erreur config generation : le routeur " + routeur.router_hostname + " n'a pas d'interfaces")
        return "Err"
    interfaces_names = [interface.name for interface in liste_interfaces]

    #cas particulier loopback
    if "lo0" in interfaces_names:
        loopback = interfaces_names.pop(interfaces_names.index("lo0"))
        resultat += "interface Loopback0\n no ip address\n"
        resultat += " ipv6 address " + routeur.get_interface_by_name("lo0").ip + "\n ipv6 enable\n"
        resultat += petite_ligne_interface_protocole(protocole, routeur)
        resultat += exclamation(1)

    #Ethernet0/0 jamais utilisé => shutdown
    resultat += "interface Ethernet0/0\n no ip address\n shutdown\n duplex auto\n"
    resultat += exclamation(1)

    #les autres interfaces
    max_interface = max(interfaces_names)
    for i in range(0,max_interface):
        resultat += "interface GigabitEthernet0/" + i + "\n"
        if str(i) in interfaces_names:
            interface = routeur.get_interface_by_name(i)

            #cas particuler GigabitEthernet0/0 qui a beaucoup de paramètres je sais pas pourquoi
            if i == 0:
                resultat += " no ip address\n media-type gbic\n speed 1000\n"
                resultat += " duplex full\n "

            else:
                resultat += " no ip address\n"

            resultat += " negotiation auto\n ipv6 address "
            resultat += interface.ip+"\n ipv6 enable\n "
            if not interface.multi_AS:   # on active pas intradomain sur l'interface qui relie 2 as
                resultat += petite_ligne_interface_protocole(protocole, routeur)

        else:
            resultat += " no ip address\n shutdown\n negotiation auto\n"
        exclamation(1)



def total_router_configuration(router, default):
    result_file = open("i" + str(router.router_hostname) + "_startup-config.cfg", "x")
    everything = "!\n ! Configuré automatiquement le " + datetime.datetime.now() + " \n!\n"
    everything += ""

    new_file_name = "i" + str(router.router_hostname) + "_startup-config.cfg"
    with open(new_file_name, "x") as result_file:
        everything += default["BLOC 1"]
        everything += exclamation(1)
        everything += "hostname R" + str(router.router_hostname) + "\n"
        everything += exclamation(1)
        everything += default["BLOC 2"]
        everything += exclamation(1)
        everything += bloc_interfaces(intra_protocole, router)
        everything += exclamation(1)
        everything += bloc_bgp(intra_protocole, router)
        everything += exclamation(1)
        everything += default["BLOC 3"]
        everything += exclamation(1)
        everything += bloc_intradom(intra_protocole, router)
        everything += default["BLOC 4"]
        everything += exclamation(5)

    return everything


default_blocs = initialize_default_blocs()
