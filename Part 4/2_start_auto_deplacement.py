from charge_objects import *
import drag_and_drop
import auto_deplacement


def ask_gns3_position():
    return filedialog.askdirectory(title=u'Choose GNS3 project folder')


for routeur in routeurs:
    drag_and_drop.total_router_configuration(routeur, drag_and_drop.initialize_default_blocs())

gns3_path_empty = True  # avoid empty filename
while gns3_path_empty:
    gns3_path = ask_gns3_position()
    if gns3_path:
        gns3_path_empty = False
auto_deplacement.initialize(gns3_path)
print(auto_deplacement.correspondance_hostname_nodeid())
auto_deplacement.new_dynamips(auto_deplacement.correspondance_hostname_nodeid())
