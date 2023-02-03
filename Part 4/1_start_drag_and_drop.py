from charge_objects import *
import drag_and_drop


for routeur in routeurs:
    drag_and_drop.total_router_configuration(routeur, drag_and_drop.initialize_default_blocs())
