from tkinter import filedialog
import shelve
from instruments import *
from itertools import product


# todo: if we want to generate multiple networks, after each write, del objects is needed


def ask_obj_path() -> str:  # no file type
    return filedialog.askopenfilename(title=u'Save Python persistent object', filetypes=[("DAT", ".dat")])[:-4]


def charge_as(shelve_obj_dict) -> object:
    return AS(num=shelve_obj_dict['as-number'],
              protocol=shelve_obj_dict['intra-protocol'],
              prefix=shelve_obj_dict['as-prefix'])


def charge_router(shelve_obj_dict, in_as) -> object:
    return Router(num=shelve_obj_dict['router-hostname'],
                  parent_as=in_as)


def charge_asbr(shelve_obj_dict, in_as) -> object:
    return ASBR(num=shelve_obj_dict['router-number'],
                parent_as=in_as)


def charge_interface(shelve_obj_dict, ip_prefix, parent_router: object, neighbor_router: object) -> object:
    return Interface(number=shelve_obj_dict['neighbor_number'],
                     ip_prefix=ip_prefix,
                     parent_router=parent_router,
                     neighbor_router=neighbor_router)


# dynamic naming (ex. as_1)
obj_path = ask_obj_path()
with shelve.open(obj_path) as obj:
    # generate all AS objects
    for as_num in obj['as_number_list']:  # ignore warning, obj['as_number_list'] is a list
        temp = charge_as(obj['as_' + str(as_num)])
        exec('as_{}_obj = {}'.format(as_num, temp.__dict__))
    # print(as_1_obj, '\n', as_2_obj)  # test ok

    # generate all Router objects
    for as_num in obj['as_number_list']:
        temp_len = len(obj['routers_as_' + str(as_num)])
        for router_num in range(temp_len):
            # ignore warning, obj['router_number_list'] is a list
            # temp_router_num = obj['routers_as_' + str(as_num)][(as_num - 1) * 7 + router_num - 1]
            temp_router_num = obj['routers_as_' + str(as_num)][router_num]  # ignore warning
            # print(temp_router_num)
            temp = charge_router(temp_router_num, None)  # "as_{}_obj".format(as_num))
            # exec("temp = charge_router(temp_router_num, as_{}_obj)".format(as_num))
            # exec('print(as_{}_obj, end=" ")'.format(as_num))
            print(temp.__dict__)

    # generate all ASBR objects

    # generate all Interface objects

# if __name__ == '__main__':
#     obj_path = ask_obj_path()
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
