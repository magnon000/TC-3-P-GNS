from instruments import *
import drag_and_drop
import auto_deplacement

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

# création AS
as1 = AS(1, "rip", "1::/16")
as2 = AS(2, "ospf", "2::/16")

# création routeurs
routeur1 = Router(1, as1)
routeur2 = Router(2, as1)
routeur3 = Router(3, as1)
routeur4 = Router(4, as1)
routeur5 = Router(5, as1)
routeur6 = ASBR(6, as1)
routeur7 = ASBR(7, as1)

routeur8 = ASBR(8, as2)
routeur9 = ASBR(9, as2)
routeur10 = Router(10, as2)
routeur11 = Router(11, as2)
routeur12 = Router(12, as2)
routeur13 = Router(13, as2)
routeur14 = Router(14, as2)

# Relier les routeurs
# R1
routeur1.add_interface_from_neighbor_router("0", routeur2)
routeur1.add_interface_from_neighbor_router("1", routeur3)
routeur1.craft_ip_on_all_interfaces()
routeur1.add_loopback_interface()

# plus rapide avec dictionnaires et add_many_interfaces_from_routers
# R2
interfaces_routeur2 = {"0": routeur1, "1": routeur3, "2": routeur4}
routeur2.add_many_interfaces_from_routers(interfaces_routeur2)
routeur2.craft_ip_on_all_interfaces()
routeur2.add_loopback_interface()

# R3
interfaces_routeur3 = {"0": routeur1, "1": routeur2, "2": routeur5}
routeur3.add_many_interfaces_from_routers(interfaces_routeur3)
routeur3.craft_ip_on_all_interfaces()
routeur3.add_loopback_interface()

# R4
interfaces_routeur4 = {"0": routeur2, "1": routeur5, "2": routeur6, "3": routeur7}
routeur4.add_many_interfaces_from_routers(interfaces_routeur4)
routeur4.craft_ip_on_all_interfaces()
routeur4.add_loopback_interface()

# R5
interfaces_routeur5 = {"0": routeur3, "1": routeur4, "2": routeur7, "3": routeur6}
routeur5.add_many_interfaces_from_routers(interfaces_routeur5)
routeur5.craft_ip_on_all_interfaces()
routeur5.add_loopback_interface()

# R6
routeur6.add_interface_from_neighbor_router("0", routeur4)
routeur6.add_interface_from_neighbor_router("3", routeur5)
routeur6.add_interface_from_neighbor_router("2", routeur8,"12::/16")
routeur6.craft_ip_on_all_interfaces()
routeur6.add_loopback_interface()

# R7
routeur7.add_interface_from_neighbor_router("0", routeur5)
routeur7.add_interface_from_neighbor_router("3", routeur4)
routeur7.add_interface_from_neighbor_router("2", routeur9,"12::/16")
routeur7.craft_ip_on_all_interfaces()
routeur7.add_loopback_interface()

# R8
routeur8.add_interface_from_neighbor_router("0", routeur10)
routeur8.add_interface_from_neighbor_router("3", routeur11)
routeur8.add_interface_from_neighbor_router("2", routeur6,"12::/16")
routeur8.craft_ip_on_all_interfaces()
routeur8.add_loopback_interface()

# R9
routeur9.add_interface_from_neighbor_router("0", routeur11)
routeur9.add_interface_from_neighbor_router("3", routeur10)
routeur9.add_interface_from_neighbor_router("2", routeur7,"12::/16")
routeur9.craft_ip_on_all_interfaces()
routeur9.add_loopback_interface()

# R10
interfaces_routeur10 = {"0": routeur12, "1": routeur11, "2": routeur8, "3": routeur9}
routeur10.add_many_interfaces_from_routers(interfaces_routeur10)
routeur10.craft_ip_on_all_interfaces()
routeur10.add_loopback_interface()

# R11
interfaces_routeur11 = {"0": routeur13, "1": routeur10, "2": routeur9, "3": routeur8}
routeur11.add_many_interfaces_from_routers(interfaces_routeur11)
routeur11.craft_ip_on_all_interfaces()
routeur11.add_loopback_interface()

# R12
interfaces_routeur12 = {"0": routeur14, "1": routeur13, "2": routeur10}
routeur12.add_many_interfaces_from_routers(interfaces_routeur12)
routeur12.craft_ip_on_all_interfaces()
routeur12.add_loopback_interface()

# R13
interfaces_routeur13 = {"0": routeur14, "1": routeur12, "2": routeur11}
routeur13.add_many_interfaces_from_routers(interfaces_routeur13)
routeur13.craft_ip_on_all_interfaces()
routeur13.add_loopback_interface()

# R14
routeur14.add_interface_from_neighbor_router("0", routeur12)
routeur14.add_interface_from_neighbor_router("1", routeur13)
routeur14.craft_ip_on_all_interfaces()
routeur14.add_loopback_interface()

routeur1.description()
routeur2.description()
routeur3.description()
routeur4.description()
routeur5.description()
routeur6.description()
routeur7.description()
routeur8.description()
routeur9.description()
routeur10.description()
routeur11.description()
routeur12.description()
routeur13.description()
routeur14.description()

as1.update_gateways()
as2.update_gateways()

as1.description()
as2.description()


routeurs = [routeur1, routeur2, routeur3, routeur4, routeur5, routeur6, routeur7,
            routeur8, routeur9, routeur10, routeur11, routeur12, routeur13, routeur14]

for routeur in routeurs:
    drag_and_drop.total_router_configuration(routeur, drag_and_drop.initialize_default_blocs())

auto_deplacement.initialize("/media/diego/SSD/Users/Diego/Documents/Scolaire/GNS3/TC-3-P-GNS")

print(auto_deplacement.correspondance_hostname_nodeid())

auto_deplacement.new_dynamips(auto_deplacement.correspondance_hostname_nodeid())

