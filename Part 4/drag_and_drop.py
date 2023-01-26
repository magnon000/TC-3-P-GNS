#from charge_objects import *
from instruments import *
import datetime
import os
import shutil


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
        return " ipv6 ospf " + routeur.parent_AS.AS_number + " area 0\n"


def bloc_interfaces(routeur: Router):
    protocole = routeur.parent_AS.intradomain_protocol
    resultat = "!\n"
    liste_interfaces = routeur.get_sorted_list_of_interfaces()
    if len(routeur.interfaces) == 0:
        print("Erreur config generation : le routeur " + str(routeur.router_hostname) + " n'a pas d'interfaces")
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
    max_interface = int(max(interfaces_names)) if int(max(interfaces_names)) > 1 else 2
    print(interfaces_names)
    for i in range(0, max_interface+1):
        resultat += "interface GigabitEthernet" + str(i) + "/0\n"
        if str(i) in interfaces_names:
            interface = routeur.get_interface_by_name(i)

            #cas particuler GigabitEthernet0/0 qui a beaucoup de paramètres je sais pas pourquoi
            if i == 0:
                resultat += " no ip address\n media-type gbic\n speed 1000\n"
                resultat += " duplex full\n"

            else:
                resultat += " no ip address\n"

            resultat += " negotiation auto\n ipv6 address "
            resultat += interface.ip+"\n ipv6 enable\n"
            if not interface.multi_AS:   # on active pas intradomain sur l'interface qui relie 2 as
                resultat += petite_ligne_interface_protocole(protocole, routeur)

        else:
            resultat += " no ip address\n shutdown\n negotiation auto\n"
        resultat += exclamation(1)

    return resultat


def bloc_bgp(routeur):
    # partie neighbor
    name = str(routeur.router_hostname)
    protocole = str(routeur.parent_AS.intradomain_protocol)
    as_num = str(routeur.parent_AS.AS_number)
    resultat = ""
    resultat += "router bgp "+str(as_num)+"\n bgp router-id "+routeur.router_ID+"\n bgp log-neighbor-changes\n"
    resultat += " no bgp default ipv4-unicast\n"
    for other_router in routeur.parent_AS.routers:
        if str(other_router.router_hostname) != name:
            loopback_address = other_router.get_interface_by_name("lo0").ip_no_mask
            resultat += " neighbor " + loopback_address + " remote-as " + as_num + "\n"
            resultat += " neighbor " + loopback_address + " update-source Loopback0\n"
    if routeur.is_asbr():
        for interface in routeur.interfaces:
            if (not interface.is_loopback()) and interface.multi_AS:
                neigh_address = interface.corresponding_interface().ip_no_mask
                resultat += " neighbor " + neigh_address + " remote-as " + interface.neighbor_router.parent_AS.AS_number
    resultat += "\n " + exclamation(1)

    # partie address-family
    resultat += " address-family ipv4\n exit-address-family\n"
    resultat += " " + exclamation(1)+" address-family ipv6\n"
    if routeur.is_asbr():
        if protocole == "rip":
            resultat += "  redistribute rip AS" + as_num + "rip\n"
        else:
            resultat += "  redistribute ospf " + as_num + "\n"

        for interface in routeur.interfaces:
            if interface.is_loopback():
                resultat += "  network " + interface.ip + "\n"
            elif interface.parent_router.parent_AS.AS_number == routeur.parent_AS.AS_number:
                resultat += "  network " + interface.ip_prefix + "\n"

        resultat += "  aggregate-address " + routeur.parent_AS.AS_prefix + " summary-only\n"

    for other_router in routeur.parent_AS.routers:
        if str(other_router.router_hostname) != name:
            loopback_address = other_router.get_interface_by_name("lo0").ip_no_mask
            resultat += "  neighbor " + loopback_address + " activate\n"
    if routeur.is_asbr():
        for interface in routeur.interfaces:
            if (not interface.is_loopback()) and interface.multi_AS:
                neigh_address = interface.corresponding_interface().ip_no_mask
                resultat += "  neighbor " + neigh_address + " activate\n"
    resultat += " exit-address-family\n!\n"

    return resultat


def bloc_intradom(routeur):
    name = str(routeur.router_hostname)
    protocole = str(routeur.parent_AS.intradomain_protocol)
    as_num = str(routeur.parent_AS.AS_number)
    resultat = ""
    if protocole == "rip":
        resultat += "ipv6 router rip AS"+as_num+"rip\n redistribute connected\n!\n"
    elif protocole == "ospf":
        resultat += "ipv6 router ospf "+as_num+"\n router-id "+routeur.router_ID+"\n redistribute connected\n"
    return resultat


def total_router_configuration(router, default):
    everything = "!\n! Configuré automatiquement le " + str(datetime.datetime.now()) + " \n!\n"
    everything += ""
    new_file_name = "autoconfig-result/i" + str(router.router_hostname) + "_startup-config.cfg"
    try:
        os.remove(new_file_name)
    except FileNotFoundError:
        pass
    with open(new_file_name, "x") as result_file:
        everything += default["BLOC 1"]
        everything += exclamation(1)
        everything += "hostname R" + str(router.router_hostname) + "\n"
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

        result_file.write(everything)


try:
    shutil.rmtree("./autoconfig-result")
except OSError:
    pass

os.mkdir("./autoconfig-result")

default_blocs = initialize_default_blocs()

