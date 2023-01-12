import json

json_path = '../Part 2/intent.json'
with open(json_path, 'rt') as config:
    json_raw = config.read()
    json_convert = json.loads(json_raw)
    print(json_convert)

as_list = json_convert['as']
neighbor_as_list = [key['neighbor-as'][0] for key in as_list]
print(neighbor_as_list)
gateway_routers_list = [dicti['gateway-routers'] for dicti in neighbor_as_list]
print(gateway_routers_list)
routers_list = [key['routers'] for key in as_list]
print(routers_list)
router_neighbor_list = [key['router-neighbors'] for dicti in routers_list for key in dicti]
print(router_neighbor_list)
