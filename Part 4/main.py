from instruments import *

# def decodeJson(json):
#     return les données





# #ipv6
# for AS in lesdonnées:
#     for routeurs in


# #RIP
# for AS in lesdonnées:
#     if protocol = rip:




#      AS1         AS2
# (R1 <-> R2) <-> (R3)

astest1 = AS(1, "rip", "1::/16")
astest2 = AS(2, "ospf", "2::/16")

routeur1 = Router("1", astest1)
routeur2 = ASBR("2", astest1)
routeur3 = ASBR("3", astest2)

interface1 = Interface("0", "1::/16", routeur1, routeur2)
routeur1.add_existing_interfaces(interface1)

routeur2.add_interface_from_neighbor_router("0", routeur1)

routeur3.add_interface_from_neighbor_router("0", routeur2)

routeur2.add_interface_from_neighbor_router("1",routeur3)

routeur1.interfaces[0].craft_IP()
routeur2.interfaces[0].craft_IP()
routeur3.interfaces[0].craft_IP()
routeur2.interfaces[1].craft_IP()