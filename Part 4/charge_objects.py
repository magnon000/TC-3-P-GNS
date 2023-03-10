"""
* read from Python persistent object file
* generate object with dynamic name (ex. as_1_obj, router_1_obj, asbr_6_obj(router6), inter_1_0_2_obj)
* return a list of Router objects
"""
from tkinter import filedialog
import shelve
from instruments import *
from copy import deepcopy


def ask_shelve_path() -> str:  # no file type
    return filedialog.askopenfilename(title=u'OPEN Python persistent object', filetypes=[("DAT", ".dat")])[:-4]


def charge_as(shelve_obj_dict) -> object:
    return AS(num=shelve_obj_dict['as-number'],
              protocol=shelve_obj_dict['intra-protocol'],
              prefix=shelve_obj_dict['as-prefix'])


def charge_router(shelve_obj_dict, in_as: AS) -> object:
    return Router(num=shelve_obj_dict['router-hostname'],
                  parent_as=in_as)


def charge_asbr(shelve_obj_dict, in_as: AS) -> object:
    return ASBR(num=shelve_obj_dict['router-number'],
                parent_as=in_as)


# def charge_interface(shelve_obj_dict, ip_prefix, parent_router: Router or ASBR, neighbor_router: Router or ASBR)
# -> object:
def charge_interface(interface_num, ip_prefix: str, parent_router: Router, neighbor_router: Router) -> object:
    return Interface(number=interface_num,
                     ip_prefix=ip_prefix,
                     parent_router=parent_router,
                     neighbor_router=neighbor_router)


# ---func for generating object---
def open_pobj_file() -> str:
    """return the path(str) of Python persistent object, while ensuring chosen filename is not empty"""
    shelve_path_empty = True  # avoid empty filename
    while shelve_path_empty:
        obj_path = ask_shelve_path()
        if obj_path:
            shelve_path_empty = False
    return obj_path


shelve_path = open_pobj_file()
with shelve.open(shelve_path) as obj:
    """generate all AS objects"""
    for as_num in obj['as_number_list']:  # ignore warning, obj['as_number_list'] is a list
        temp_obj = charge_as(obj['as_' + str(as_num)])  # to avoid python escape characters
        exec("as_{}_obj = temp_obj".format(as_num))
        # exec("print(as_{}_obj)".format(as_num))
    del temp_obj

    """generate all Router objects, add loopback Interface objects"""
    router_num_count = 0
    for as_num in obj['as_number_list']:
        temp_len = len(obj['routers_as_' + str(as_num)])  # ignore warning, obj['router_number_list'] is a list
        for router_index in range(temp_len):
            temp_router_dict = obj['routers_as_' + str(as_num)][router_index]  # to avoid python escape characters
            exec("router_{}_obj = charge_router(temp_router_dict, as_{}_obj)"
                 .format(obj['router_number_list'][router_num_count], as_num))
            router_num_count += 1
            # add loopback interface
            exec("router_{}_obj.add_loopback_interface()".format(router_num_count))
            # exec("print(router_{}_obj.__dict__)".format(router_num_count))
    del temp_len, temp_router_dict, router_num_count

    """generate physic Interface objects (naming scheme: inter_<No.Router>_<No.Interface>_<No.Neighbor_Router>_obj)"""
    for router_num in obj['router_number_list']:  # ex. in range(1,14)
        # ex. 1.all routers; 2.all interfaces; 3.all neighbor routers according to interfaces' order; 4. AS prefix
        exec("temp_parent_router = router_{}_obj".format(router_num))  # var: parent_router: object
        for one_neighbor_dict in obj['neighbor_router_' + str(router_num)]:
            # ex. in [{'neighbor-number': 12, 'interface': 0}, {'neighbor-number': 13, 'interface': 1}] for R14
            interface_num_temp = one_neighbor_dict['interface']  # var: number
            neighbor_num = one_neighbor_dict['neighbor-number']  # for neighbor router and ip prefix
            exec("temp_neighbor_obj = router_{}_obj".format(neighbor_num))
            as_num = temp_parent_router.parent_AS.AS_number  # ignore error
            as_num = int(as_num)  # AS_number: str in class AS
            # use method in Router class to auto generate IP
            # if router_num < neighbor_num:  # calcul subnet IP prefix
            #     ip_prefix_temp = "{}:{}{}::/32".format(as_num, router_num, neighbor_num)
            # else:
            #     ip_prefix_temp = "{}:{}{}::/32".format(as_num, neighbor_num, router_num)
            # ip_prefix_temp = "{}::/16".format(as_num)
            exec("ip_prefix_temp = as_{}_obj.AS_prefix".format(as_num))
            # if interface neighbor in self AS, use AS prefix, if not use peering-prefix
            exec("temp_as_obj = as_{}_obj".format(as_num))
            exec("temp_router_obj = router_{}_obj".format(neighbor_num))
            if temp_router_obj in temp_as_obj.routers:
                exec("inter_{}_{}_{}_obj="
                     "charge_interface(interface_num_temp, ip_prefix_temp, temp_parent_router, temp_neighbor_obj)"
                     .format(router_num, interface_num_temp, neighbor_num))
            else:
                neighbor_as_num = int(temp_router_obj.parent_AS.AS_number)  # str -> int
                as_neighbors_list_of_dicts = obj['neighbor_as_' + str(as_num)]
                as_peering_prefix = None
                for as_neighbor_dict in as_neighbors_list_of_dicts:
                    if neighbor_as_num == as_neighbor_dict['as-number']:
                        as_peering_prefix = as_neighbor_dict['peering-prefix']
                        exec("inter_{}_{}_{}_obj="
                             "charge_interface"
                             "(interface_num_temp, as_peering_prefix, temp_parent_router, temp_neighbor_obj)"
                             .format(router_num, interface_num_temp, neighbor_num))
                if not as_peering_prefix:
                    print("Error: No peering-prefix between", as_num, "and", neighbor_as_num, "!!!")
                    exit(1)
            # exec("print(inter_{}_{}_{}_obj)".format(router_num, interface_num_temp, neighbor_num))

            # add object Interface (on one router) to object Router.interfaces list (on the router)
            exec("router_{}_obj.add_existing_interfaces(inter_{}_{}_{}_obj)"
                 .format(router_num, router_num, interface_num_temp, neighbor_num))
    del temp_parent_router, interface_num_temp, neighbor_num, as_num, ip_prefix_temp, temp_as_obj, temp_router_obj
    try:
        del neighbor_as_num, as_neighbors_list_of_dicts, as_peering_prefix
    except NameError:
        pass

    """craft IP address"""
    for router_num in obj['router_number_list']:
        exec("router_{}_obj.craft_ip_on_all_interfaces()".format(router_num))

    # """add object Interface (neighbors') to object Router.interfaces list"""
    # for router_num in obj['router_number_list']:
    #     for one_neighbor_dict in obj['neighbor_router_' + str(router_num)]:
    #         interface_num_temp = one_neighbor_dict['interface']  # var: number
    #         neighbor_num = one_neighbor_dict['neighbor-number']  # for neighbor router and ip prefix
    #         exec("router_{}_obj.add_existing_interfaces(inter_{}_{}_{}_obj)"
    #              .format(neighbor_num, router_num, interface_num_temp, neighbor_num))
    # del interface_num_temp, neighbor_num
    # # for router_num in obj['router_number_list']:
    # #     exec("print(router_{}_obj.__dict__)".format(router_num))

    """generate all ASBR objects & add all interfaces"""
    for as_num in obj['as_number_list']:
        for asbr_list in obj['asbr_as_' + str(as_num)]:
            for one_dict in asbr_list:
                temp_asbr_num = one_dict['router-number']  # to avoid python escape characters
                exec(
                    "asbr_{}_obj = ASBR(int(router_{}_obj.router_hostname), as_{}_obj)"
                    .format(temp_asbr_num, temp_asbr_num, as_num))
                # copy all Router.interfaces to ASBR.interfaces
                exec("asbr_{}_obj.interfaces = deepcopy(router_{}_obj.interfaces)".format(temp_asbr_num, temp_asbr_num))
                # exec("print(asbr_{}_obj)".format(temp_asbr_num))
    del temp_asbr_num

    """
    add AS.neighbor, AS.peering_prefixs
    'AS_neighbors': {'num_neighbor_as':[ASBR objects in this AS]}
    'AS_neighbors_peering_prefixes': {'num_neighbor_as': 'peering-prefix'}
    """
    # as_neighbor_num = None  # init for if as_neighbor_num:
    for as_num in obj['as_number_list']:
        # print(obj['neighbor_as_' + str(as_num)])
        as_neighbors_list_of_dicts = obj['neighbor_as_' + str(as_num)]
        temp_neighbors_dicts = {}
        temp_peerings_prefix = {}
        neighbor_index = 0
        for as_neighbor_dict in as_neighbors_list_of_dicts:
            as_neighbor_num = as_neighbor_dict['as-number']
            asbr_list = []
            # for asbr_list_temp in obj['asbr_as_' + str(as_num)]:
            #     print(asbr_list_temp)
            #     for asbr_dict in asbr_list_temp:
            #         # print(neighbor_index, asbr_dict)
            #         temp_asbr_num = asbr_dict['router-number']
            #         exec("asbr_list.append(asbr_{}_obj)".format(temp_asbr_num))
            for asbr_dict in obj['asbr_as_' + str(as_num)][neighbor_index]:  # if 1 AS has n peering_prefix
                # print(neighbor_index, asbr_dict)
                temp_asbr_num = asbr_dict['router-number']
                exec("asbr_list.append(asbr_{}_obj)".format(temp_asbr_num))
            # print(as_num, asbr_list)
            neighbor_index += 1
            as_peering = as_neighbor_dict['peering-prefix']
            temp_neighbor_dict = {str(as_neighbor_num): asbr_list}
            temp_peering_prefix = {str(as_neighbor_num): as_peering}  # to-do: change this to list if 1 AS n peering_pre
            temp_neighbors_dicts.update(temp_neighbor_dict)
            temp_peerings_prefix.update(temp_peering_prefix)
        # write to object
        exec("as_{}_obj.AS_neighbors = temp_neighbors_dicts".format(as_num))
        exec("as_{}_obj.AS_neighbors_peering_prefixes.update(temp_peerings_prefix)".format(as_num))
        # exec("print(as_{}_obj.__dict__)".format(as_num))
    del as_neighbors_list_of_dicts, temp_neighbors_dicts, as_neighbor_num, asbr_list, temp_asbr_num, as_peering
    del temp_neighbor_dict, temp_peering_prefix, neighbor_index, temp_peerings_prefix

    """delete ASBR related Router"""
    for as_num in obj['as_number_list']:
        exec("temp_router_list = as_{}_obj.routers".format(as_num))
        for asbr_list in obj['asbr_as_' + str(as_num)]:
            for asbr_dict in asbr_list:
                temp_asbr_num = asbr_dict['router-number']
                try:
                    exec("as_{}_obj.routers.remove(router_{}_obj)".format(as_num, temp_asbr_num))
                    exec("del router_{}_obj".format(temp_asbr_num))
                except NameError:
                    pass
        exec("print(as_{}_obj.__dict__)".format(as_num))
    del temp_asbr_num

    """generate a list of Router & ASBR"""
    routeurs = []
    for as_num in obj['router_number_list']:
        try:
            # exec("print(router_{}_obj.__dict__)".format(as_num))
            exec("routeurs.append(router_{}_obj)".format(as_num))
        except NameError:
            exec("routeurs.append(asbr_{}_obj)".format(as_num))
    print(routeurs)

if __name__ == '__main__':
    pass
