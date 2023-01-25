from instruments import *
import drag_and_drop

# # TEST 1
# #      AS1         AS2
# # (R1 <-> R2) <-> (R3)

# astest1 = AS(1, "rip", "1::/16")
# astest2 = AS(2, "ospf", "2::/16")
#
# routeur1 = Router(1, astest1)
# routeur2 = ASBR(2, astest1)
# routeur3 = ASBR(3, astest2)
#
# interface1 = Interface(0, "1::/16", routeur1, routeur2)
# routeur1.add_existing_interfaces(interface1)
#
# routeur2.add_interface_from_neighbor_router("0", routeur1)
#
# routeur3.add_interface_from_neighbor_router("0", routeur2, "12::/16")
#
# routeur2.add_interface_from_neighbor_router("1", routeur3, "12::/16")
#
# routeur2.add_loopback_interface()
#
# astest1.description()
# astest2.description()
#
# routeur1.interfaces[0].craft_ip()
# routeur3.interfaces[0].craft_ip()
# routeur2.craft_ip_on_all_interfaces()
#
# print(astest1.AS_neighbors)
#
# print(routeur2.interfaces)
# print(routeur2.get_sorted_list_of_interfaces())



# TESTS AVEC NOTRE RESEAU

#création AS
as1 = AS(1, "rip", "1::/16")
as2 = AS(1, "ospf", "1::/16")

#création routeurs
routeur1 = Router(1, as1)
routeur2 = Router(2, as1)
routeur3 = Router(3, as1)
routeur4 = Router(4, as1)
routeur5 = Router(5, as1)
routeur6 = Router(6, as1)
routeur7 = Router(7, as1)

routeur8 = Router(8, as2)
routeur9 = Router(9, as2)
routeur10 = Router(10, as2)
routeur11 = Router(11, as2)
routeur12 = Router(12, as2)
routeur13 = Router(13, as2)
routeur14 = Router(14, as2)

#relier les routeurs
#R1
routeur1.add_interface_from_neighbor_router("0", routeur2)
routeur1.add_interface_from_neighbor_router("1", routeur3)
routeur1.craft_ip_on_all_interfaces()

#plus rapide avec dictionnaires et add_many_interfaces_from_routers
#R2
interfaces_routeur2 = {"0": routeur1, "1": routeur3, "2": routeur4}
routeur2.add_many_interfaces_from_routers(interfaces_routeur2)
routeur2.craft_ip_on_all_interfaces()

#R3
interfaces_routeur3 = {"0": routeur1, "1": routeur2, "2": routeur5}
routeur3.add_many_interfaces_from_routers(interfaces_routeur3)
routeur3.craft_ip_on_all_interfaces()

#R4
interfaces_routeur4 = {"0": routeur2, "1": routeur5, "2": routeur6, "3": routeur7}
routeur4.add_many_interfaces_from_routers(interfaces_routeur4)
routeur4.craft_ip_on_all_interfaces()

#R5
interfaces_routeur5 = {"0": routeur3, "1": routeur4, "2": routeur7, "3": routeur6}
routeur5.add_many_interfaces_from_routers(interfaces_routeur5)
routeur5.craft_ip_on_all_interfaces()

#R6
routeur6.add_interface_from_neighbor_router("0", routeur4)
routeur6.add_interface_from_neighbor_router("3", routeur5)
routeur6.craft_ip_on_all_interfaces()

#R6
routeur7.add_interface_from_neighbor_router("0", routeur5)
routeur7.add_interface_from_neighbor_router("3", routeur4)
routeur7.craft_ip_on_all_interfaces()

routeur1.description()
routeur2.description()
routeur3.description()
routeur4.description()
routeur5.description()
routeur6.description()
routeur7.description()

as1.description()

routeurs = [routeur1, routeur2, routeur3, routeur4, routeur5, routeur6, routeur7]

for routeur in routeurs:
    drag_and_drop.total_router_configuration(routeur, drag_and_drop.initialize_default_blocs())