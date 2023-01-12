
class AS:
    def __init__(self, num, protocol, prefix, routers=None, gatewayRouters=None):
        self.AS_number = num
        self.intradomain_protocol = protocol
        self.AS_prefix = prefix
        self.routers = []
        self.AS_neighbors = {}

    def add_routers(self, router):
        self.routers.append(router)
    
    def add_neighbor_AS(self, neighbor, gateways):
        for router in gateways:
            self.AS_neighbors[neighbor.AS_number] = gateways
        


class Router:
    def __init__(self, num, parentAS):
        self.router_hostname = num
        self.router_ID = str(num)+3*("."+str(num))
        self.parent_AS = parentAS
        self.interfaces = []

    def add_interfaces(self, interface, ip):
        self.interfaces[interface] = ip
    


class ASBR(Router):
    def __init__(self, num, parentAS):
        super(num, parentAS)


class Interface:
    def __init__(self, name, ip_prefix, parent_router, neighbor_router=None):
        self.name = name
        self.ip_prefix = ip_prefix
        self.parent_router = parent_router
        self.neighbor_router = neighbor_router
    
    def auto_IP(self):
        if self.neighbor_router != None:
            debut_masque = self.ip_prefix.index("/")
            masque = int(self.ip_prefix[(debut_masque+1):])
            #non fini


class LoopbackInterface(Interface):
    def __init__(self, name, ip_prefix, parent_router):
        super().__init__(name, ip_prefix, parent_router)

        debut_masque = self.ip_prefix.index("/")
        longueur_hostname = len(str(self.name))
        self.ip = self.ip_prefix[:debut_masque]+(4-longueur_hostname)*str(0)+parent_router.routeur_hostname+"/128" #NON TESTE