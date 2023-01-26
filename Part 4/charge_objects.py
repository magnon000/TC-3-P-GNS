from tkinter import filedialog
import shelve
from instruments import *


# todo: if we want to generate multiple networks, after each write, del objects is needed


def ask_shelve_path() -> str:  # no file type
    return filedialog.askopenfilename(title=u'Save Python persistent object', filetypes=[("DAT", ".dat")])[:-4]


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


# dynamic naming (ex. as_1_obj, router_1_obj, asbr_6_obj(router6), inter_1_0_2_obj)
shelve_path_empty = True  # avoid empty filename
while shelve_path_empty:
    obj_path = ask_shelve_path()
    if obj_path:
        shelve_path_empty = False

with shelve.open(obj_path) as obj:
    # generate all AS objects
    for as_num in obj['as_number_list']:  # ignore warning, obj['as_number_list'] is a list
        temp_obj = charge_as(obj['as_' + str(as_num)])  # to avoid python escape characters
        exec("as_{}_obj = temp_obj".format(as_num))
        # exec("print(as_{}_obj)".format(as_num))
    del temp_obj

    # generate all Router objects
    router_num_count = 0
    for as_num in obj['as_number_list']:
        temp_len = len(obj['routers_as_' + str(as_num)])  # ignore warning, obj['router_number_list'] is a list
        for router_index in range(temp_len):
            temp_router_dict = obj['routers_as_' + str(as_num)][router_index]  # to avoid python escape characters
            exec("router_{}_obj = charge_router(temp_router_dict, as_{}_obj)"
                 .format(obj['router_number_list'][router_num_count], as_num))
            router_num_count += 1
            # exec("print(router_{}_obj)".format(router_num_count))
    del router_num_count, temp_router_dict

    # generate all Interface objects (naming scheme: inter_<No.Router>_<No.Interface>_<No.Neighbor_Router>_obj)
    for router_num in obj['router_number_list']:  # ex. in range(1,14)
        """ex. 1.router 1-14; 2.interface 0-3; 3.neighbor router according to interfaces' order; 4. calcul AS prefix"""
        exec("temp_parent_router = router_{}_obj".format(router_num))  # var: parent_router: object
        # print(temp_parent_router)  # ignore error, var temp_parent_router in exec()
        for one_neighbor_dict in obj['neighbor_router_' + str(router_num)]:
            # ex. in [{'neighbor-number': 12, 'interface': 0}, {'neighbor-number': 13, 'interface': 1}] for R14
            interface_num_temp = one_neighbor_dict['interface']  # var: number
            neighbor_num = one_neighbor_dict['neighbor-number']  # for neighbor router and ip prefix
            exec("temp_neighbor_obj = router_{}_obj".format(neighbor_num))
            as_num = temp_parent_router.parent_AS.AS_number
            as_num = int(as_num)  # AS_number: str in class AS
            # if router_num < neighbor_num:  # calcul subnet IP prefix
            #     ip_prefix_temp = "{}:{}{}::/32".format(as_num, router_num, neighbor_num)
            # else:
            #     ip_prefix_temp = "{}:{}{}::/32".format(as_num, neighbor_num, router_num)
            ip_prefix_temp = "{}::/16".format(as_num)
            exec("inter_{}_{}_{}_obj="
                 "charge_interface(interface_num_temp, ip_prefix_temp, temp_parent_router, temp_neighbor_obj)"
                 .format(router_num, interface_num_temp, neighbor_num))
            # exec("print(inter_{}_{}_{}_obj)".format(router_num, interface_num_temp, neighbor_num))

            # add object Interface (on one router) to object Router.interfaces list (on the router)
            exec("router_{}_obj.add_existing_interfaces(inter_{}_{}_{}_obj)"
                 .format(router_num, router_num, interface_num_temp, neighbor_num))
    del interface_num_temp, neighbor_num, as_num, ip_prefix_temp, temp_parent_router

    # add all interfaces, craft IP address
    for router_num in obj['router_number_list']:
        exec("router_{}_obj.craft_ip_on_all_interfaces()".format(router_num))

    # add object Interface (neighbors') to object Router.interfaces list
    for router_num in obj['router_number_list']:
        for one_neighbor_dict in obj['neighbor_router_' + str(router_num)]:
            interface_num_temp = one_neighbor_dict['interface']  # var: number
            neighbor_num = one_neighbor_dict['neighbor-number']  # for neighbor router and ip prefix
            exec("router_{}_obj.add_existing_interfaces(inter_{}_{}_{}_obj)"
                 .format(neighbor_num, router_num, interface_num_temp, neighbor_num))
    del interface_num_temp, neighbor_num
    # for router_num in obj['router_number_list']:
    #     exec("print(router_{}_obj.__dict__)".format(router_num))

    # generate all ASBR objects
    for as_num in obj['as_number_list']:
        for temp_dict in obj['asbr_as_' + str(as_num)]:
            temp_asbr_num = temp_dict['router-number']  # to avoid python escape characters
            exec("asbr_{}_obj = ASBR(router_{}_obj, as_{}_obj)".format(temp_asbr_num, temp_asbr_num, as_num))
            # exec("print(asbr_{}_obj)".format(temp_asbr_num))
    del temp_asbr_num

print(as_1_obj.__dict__)
# todo: loopback
# todo: AS.neighbor, AS.peering_prefixs


# if __name__ == '__main__':
#     obj_path = ask_shelve_path()
#     with shelve.open(obj_path) as test:
#         obj_list = [ele for ele in test]
#         print(obj_list)
#         print(test['router_number_list'])
#         print(test['as_number_list'])
#         # print(test.__dict__)
#         # print(test['as_1'])
#         print(test['routers_as_1'])
#         print(test['asbr_as_1'])
#         print(test['neighbor_router_1'])
#         # print(len(test['neighbor_router_1']))
#         # as1r = test['as_1']
#         # print(type(test))
#         # as1 = AS(num=as1r['as-number'], protocol=as1r['intra-protocol'], prefix=as1r['as-prefix'])
#         # print(as1.__dict__)
