
class AS:
    def __init__(self, num, protocol, prefix, routers=None, gatewayRouters=None):
        self.AS_number = num
        self.intradomain_protocol = protocol
        self.AS_prefix = prefix
        self.routers = []
        self.AS_neighbors = {}

    def add_router(self, router):
        self.routers.append(router)
    
    def add_neighbor_AS(self, neighbor, gateways):
        for router in gateways:
            self.AS_neighbors[neighbor.AS_number] = gateways

    #pas fait
    #def craft_IP_on_all_routers_interfaces(self):
        #True
        


class Router:
    def __init__(self, num, parentAS):
        self.router_hostname = num
        self.router_ID = str(num)+3*("."+str(num)) #anticipation OSPF
        self.parent_AS = parentAS
        self.interfaces = []

    def add_existing_interfaces(self, interface):
        self.interfaces.append(interface)

    #overidée dans la classe héritée ASBR (car comportement différent)
    def add_interface_from_neighbor_router(self, interface_name, neighbor_router):
        new_interface = Interface(interface_name, self.parent_AS.AS_prefix, self, neighbor_router)
        self.interfaces.append(new_interface)

    def add_loopback_interface(self):
        new_interface = LoopbackInterface(self.parent_AS.AS_prefix, self)
        self.interfaces.append(new_interface)

    def craft_IP_on_all_interfaces(self):
        if self.interfaces.len == 0:
            print("Erreur craft_IP_on_all_interfaces() : aucune interface dans le routeur",self.router_hostname)
        else:
            for interface in self.interfaces:
                interface.craft_IP()



class ASBR(Router):
    def __init__(self, num, parentAS):
        super().__init__(num, parentAS)

    #méthode retenue pour l'instant : les IP entre 2 AS ont pour préfixe FFFF::/16
    def add_interface_from_neighbor_router(self, interface_name, neighbor_router):
        if self.parent_AS.AS_number != neighbor_router.parent_AS.AS_number:
            new_interface = Interface(interface_name, "FFFF::/16", self, neighbor_router)
        else:
            new_interface = Interface(interface_name, self.parent_AS.AS_prefix, self, neighbor_router)
        self.interfaces.append(new_interface)
                

class Interface:
    def __init__(self, name, ip_prefix, parent_router, neighbor_router=None):
        self.name = name
        self.ip_prefix = ip_prefix
        self.parent_router = parent_router
        if neighbor_router != None:
            self.neighbor_router = neighbor_router
            self.multi_AS = parent_router.parent_AS.AS_number != neighbor_router.parent_AS.AS_number
            print(self.parent_router.router_hostname," est connecté à un autre AS sur l'interface",self.name,"vrai ou faux ? :",self.multi_AS)

    #construction de l'IP selon notre nomenclature un peu trop compliquée (définie dans readme)
    def craft_IP(self):
        if self.neighbor_router != None:
            debut_masque = self.ip_prefix.index("/")
            masque = int(self.ip_prefix[(debut_masque+1):])

            #premier bloc :XXXX: disponible d'après l'IP prefixe (nom des deux routeurs collés, en commençant par le + petit)
            min_hostn = str(min(int(self.parent_router.router_hostname),int(self.neighbor_router.router_hostname)))
            max_hostn = str(max(int(self.parent_router.router_hostname),int(self.neighbor_router.router_hostname)))
            bloc_prefix = min_hostn + max_hostn

            #avant dernier bloc :XXXX: (dans la partie hôte de l'IP) composé de juste l'hostname du routeur
            bloc_hostname = self.parent_router.router_hostname

            #dernier bloc :XXXX (dans la partie hôte de l'IP) composé du nom de l'interface (si interface 0, on met 10 pas 0)
            bloc_intname = self.name if self.name != "0" else "10"

            self.ip = self.ip_prefix[:debut_masque-1] + bloc_prefix + "::" + bloc_hostname + ":" + bloc_intname + "/" + str(masque+16)
            print("Craft IP : l'interface "+self.name+" du routeur "+str(self.parent_router.router_hostname)+" a l'IP "+self.ip)
        else:
            print("Erreur craft_IP : aucun routeur voisin sur l'interface",self.name+". Pour une interface loopback utiliser LoopbackInterface")


#l'ip est créée dès la création de l'interface
class LoopbackInterface(Interface):
    def __init__(self, ip_prefix, parent_router):
        super().__init__("lo0", ip_prefix, parent_router)
        debut_masque = self.ip_prefix.index("/")
        longueur_hostname = len(str(self.name))
        self.ip = self.ip_prefix[:debut_masque]+parent_router.routeur_hostname+"/128"
