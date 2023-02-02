from instruments import *
from charge_objects import *
import drag_and_drop
import auto_deplacement

# print(routeurs[5].interfaces)
# print(routeurs[0].parent_AS.routers)
for routeur in routeurs:
    # routeur.add_loopback_interface()
    drag_and_drop.total_router_configuration(routeur, drag_and_drop.initialize_default_blocs())

auto_deplacement.initialize("C:/Users/longr/GNS3/projects/TC-3-P-GNS/Essai_script/test_script")

print(auto_deplacement.correspondance_hostname_nodeid())

auto_deplacement.new_dynamips(auto_deplacement.correspondance_hostname_nodeid())