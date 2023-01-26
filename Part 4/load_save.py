"""
handle JSON read, Python persistent object save
"""
import json
import shelve
from tkinter import filedialog


def ask_obj_path() -> str:
    return filedialog.asksaveasfilename(title=u'Save Python persistent object', filetypes=[])


def ask_json_file() -> str:
    return filedialog.askopenfilename(title=u'Load JSON file', filetypes=[("JSON", ".json")])


def convert_json(file: str) -> dict:
    """convert JSON structure to Python structure"""
    with open(file, 'rt') as config:
        return json.loads(config.read())


def get_5_lists(convert_dict: dict) -> tuple:
    """flatten JSON structure to match class AS, class ASBR and class Router."""
    as_list = convert_dict['as']  # for get_as_num_list() and get_router_num_list().
    neighbor_as_list = [one_as['neighbor-as'] for one_as in as_list]
    asbr_list = [one_neighbor['asbr'] for neighbor_as in neighbor_as_list for one_neighbor in neighbor_as]
    routers_list = [router['routers'] for router in as_list]
    router_neighbor_list = [router['router-neighbors'] for as_routers in routers_list for router in as_routers]
    for as_routers in routers_list:
        for router in as_routers:
            del router['router-neighbors']  # flatten: -> routers_list[:]['router-hostname']
    for one_as in as_list:
        del one_as['routers']
        del one_as['neighbor-as']  # flatten: -> as_list[:]['as-number', 'intra-protocol', 'as-prefix']
    for neighbor_as in neighbor_as_list:
        for one_neighbor in neighbor_as:
            del one_neighbor['asbr']  # neighbor_as_list[:]['as-number','local-pref', 'peering-prefix']
    return as_list, neighbor_as_list, asbr_list, routers_list, router_neighbor_list


def get_as_num_list(as_list: list) -> list:
    """get a list of AS' numbers to create keys for the dicts (Class AS) in Python object persistence(shelve)."""
    return [as_dict['as-number'] for as_dict in as_list]  # list of AS numbers, ex.[1,3] for 'as1' 'as3' keys of a dict.


def get_router_num_list(routers_list: list) -> list:
    """
    get a list of routers' numbers to create keys for the dicts (Class Router) in Python object persistence(shelve).
    """
    return [one_router['router-hostname'] for routers in routers_list for one_router in routers]
    # list of router numbers, ex.[1,14] for 'router1' 'router14' keys of a dict.


def save_obj(obj_name: str, write_data: tuple, as_num_list, router_num_list) -> None:
    """use 2 lists: 'routers', 'router-neighbors' to number the keys of dict"""
    with shelve.open(obj_name) as p_obj:
        key_list = ['as_', 'neighbor_as_', 'asbr_as_', 'routers_as_', 'neighbor_router_']
        num_list = [as_num_list, as_num_list, as_num_list, as_num_list, router_num_list]
        index = 0
        for lst in write_data:
            count = 0
            for elem in lst:
                p_obj[key_list[index] + str(num_list[index][count])] = elem
                count += 1
            index += 1
        p_obj['as_number_list'] = as_num_list
        p_obj['router_number_list'] = router_num_list


if __name__ == '__main__':
    json_path = ask_json_file()
    save_path_empty = True  # avoid empty filename
    while save_path_empty:
        save_path = ask_obj_path()
        if save_path:
            save_path_empty = False
    converted_dict = convert_json(json_path)
    tuple_5_lists = get_5_lists(converted_dict)
    as_nb_list = get_as_num_list(tuple_5_lists[0])
    print("as number list:", as_nb_list)
    router_nb_list = get_router_num_list(tuple_5_lists[3])
    print("router number list:", router_nb_list)
    save_obj(save_path, tuple_5_lists, as_nb_list, router_nb_list)
    with shelve.open(save_path) as test:
        for ele in test:
            print(ele)
        print(test['asbr_as_2'])
        print(test['neighbor_router_14'])
