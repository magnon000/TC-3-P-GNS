from instruments import *
from charge_objects import *
import drag_and_drop
import auto_deplacement

for routeur in routeurs:
    # routeur.add_loopback_interface()
    drag_and_drop.total_router_configuration(routeur, drag_and_drop.initialize_default_blocs())

auto_deplacement.initialize("./json_test")

print(auto_deplacement.correspondance_hostname_nodeid())

auto_deplacement.new_dynamips(auto_deplacement.correspondance_hostname_nodeid())