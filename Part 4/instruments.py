class AS:
    def __init__(self, num: int, protocol: str, prefix: str, routers=None, asbr=None):
        self.AS_number = str(num)
        self.intradomain_protocol = protocol
        self.AS_prefix = prefix
        self.routers = []
        self.AS_neighbors = {}  # liste des neighbors (clé) avec la ou les ASBR (en liste)
        self.AS_neighbors_peering_prefixes = {}  # liste des neighbors (clé) avec les peering prefix (en string)

    def add_router(self, router):
        self.routers.append(router)

        # vérifier s'il y a des nouveaux AS voisins
        if type(router) == ASBR:
            for interface in router.interfaces:
                if interface.neighbor_router.AS_number not in self.AS_neighbors:
                    print("Erreur add_router(): le routeur ", router.router_hostname,
                          " est connecté à un routeur d'un AS inconnu (AS:", interface.neighbor_router.AS_number, ")"
                          + ". Il faut ajouter les ASBR à leur AS avant de leur donner une interface connectée à un "
                            "AS voisin"
                          + "Ou sinon les ajouter après avoir fait add_neighbor_as() sur le futur AS parent")

    # cas d'utilisation : lorsqu'on ajoute
    def add_neighbor_as(self, neighbor, gateways, peering_prefix=None):
        if type(gateways) != 'list':
            gateways = [gateways]

        self.AS_neighbors[neighbor.AS_number] = gateways
        self.AS_neighbors_peering_prefixes[neighbor.AS_number] = peering_prefix

    def craft_ip_on_all_routers_interfaces(self):
        for router in self.routers:
            router.craft_ip_on_all_interfaces()

    # pour rapidement print la classe
    def __str__(self):
        return "(AS " + self.AS_number + ")"

    def __repr__(self):
        return "(AS " + self.AS_number + ")"

    def description(self):
        print("------------------")
        print("L'AS", self.AS_number, "a pour préfixe", self.AS_prefix, "et doit utiliser le protocole intra-domaine",
              self.intradomain_protocol)
        print("Ses routeurs sont :", self.routers)
        print("Ses AS voisins et le/les ASBR vers ce voisin :", self.AS_neighbors)
        print("Ses AS voisins et le peering prefix à utiliser pour ce voisin :", self.AS_neighbors_peering_prefixes)
        print("------------------")


class Router:
    def __init__(self, num: int, parent_as=None):
        self.router_hostname = num
        self.router_ID = str(num) + 3 * ("." + str(num))  # anticipation OSPF
        self.parent_AS = parent_as
        self.interfaces = []
        if parent_as:
            parent_as.add_router(self)

    def __len__(self):
        pass  # todo: method here

    # ne fait qu'ajouter l'interface à la liste (pas de répercussions dans le parent AS)
    def add_existing_interfaces(self, interface):
        self.interfaces.append(interface)

    # overidée dans la classe héritée ASBR (car comportement différent)
    def add_interface_from_neighbor_router(self, interface_name, neighbor_router):
        new_interface = Interface(interface_name, self.parent_AS.AS_prefix, self, neighbor_router)
        self.interfaces.append(new_interface)

    def add_loopback_interface(self):
        new_interface = LoopbackInterface(self.parent_AS.AS_prefix, self)
        self.interfaces.append(new_interface)

    def craft_ip_on_all_interfaces(self):
        # if self.interfaces.len == 0:
        if len(self.interfaces) == 0:
            print("Erreur craft_ip_on_all_interfaces() : aucune interface dans le routeur", self.router_hostname)
        else:
            for interface in self.interfaces:
                interface.craft_ip()

    # récupérer les neighbor routers depuis les interfaces existantes   
    def get_neighbor_routers(self):
        liste_voisins = []
        for interface in self.interfaces:
            if type(interface) != LoopbackInterface:
                liste_voisins.append(interface.neighbor_router)
        return liste_voisins

    def __str__(self):
        return "( Routeur: N°" + str(self.router_hostname) + ")"

    def __repr__(self):
        return "( Routeur: N°" + str(self.router_hostname) + ")"

    def description(self):
        print("------------------")
        print("Le routeur", self.router_hostname, "appartient à l'AS", self.parent_AS.AS_number)
        print("Ses interfaces sont (nom,prefixe) :", self.interfaces)
        print("Ses routeurs voisins sont :", self.get_neighbor_routers())
        print("------------------")


class ASBR(Router):
    # Conseillé de créer l'ASBR avec un AS parent... NON, OBLIGATOIRE SINON NE FONCTIONNE PAS
    def __init__(self, num, parent_as):
        super().__init__(num, parent_as)

    # méthode retenue pour l'instant : les IP entre 2 AS ont pour préfixe FFFF::/16
    # A une repercussion sur le parent AS : si le neighbor routeur est dans un autre AS on ajoute l'AS
    # dans la liste des voisins avec un peering prefixe par défault (None => "FFFF::/16")
    def add_interface_from_neighbor_router(self, interface_name, neighbor_router):
        if self.parent_AS.AS_number != neighbor_router.parent_AS.AS_number:
            if neighbor_router.parent_AS.AS_number not in self.parent_AS.AS_neighbors:
                # si l'as voisin n'est pas dans la liste
                self.parent_AS.add_neighbor_as(neighbor_router.parent_AS, self)
                print("L'AS", neighbor_router.parent_AS.AS_number, "n'était pas dans la liste des AS voisins de",
                      self.parent_AS, " il a été rajouté")
                new_interface = Interface(interface_name,
                                          self.parent_AS.AS_neighbors_peering_prefixes[
                                              neighbor_router.parent_AS.AS_number],
                                          self, neighbor_router)
        else:
            new_interface = Interface(interface_name, self.parent_AS.AS_prefix, self, neighbor_router)
        self.interfaces.append(new_interface)

    def __str__(self):
        return "( ASBR: N°" + str(self.router_hostname) + ")"

    def __repr__(self):
        return "( ASBR: N°" + str(self.router_hostname) + ")"


class Interface:
    def __init__(self, name, ip_prefix, parent_router, neighbor_router=None):
        self.ip = None
        self.name = name

        """mal géré mais tant pis c'est déjà trop le bazar: 
        si pas de ip_prefix, on considère que c'est une interface de peering avec un autre AS 
        qui n'a pas de peering prefix spécifié et pareil en face 
        (le routeur avec qui on est connecté n'a pas de peering prefix spécifié avec nous)
        aucune autre raison supportée pour laquelle l'ip_prefix serait de"""
        if ip_prefix:
            self.ip_prefix = ip_prefix
        else:
            self.ip_prefix = "FFFF::/16"

        self.parent_router = parent_router
        if neighbor_router is not None:
            self.neighbor_router = neighbor_router
            self.multi_AS = parent_router.parent_AS.AS_number != neighbor_router.parent_AS.AS_number

    # construction de l'IP selon notre nomenclature un peu trop compliquée (définie dans readme)
    def craft_ip(self):
        if self.neighbor_router is not None:
            debut_masque = self.ip_prefix.index("/")
            masque = int(self.ip_prefix[(debut_masque + 1):])

            # premier bloc :XXXX: disponible d'après l'IP prefixe 
            # (nom des deux routeurs collés, en commençant par le + petit)
            min_hostn = str(min(int(self.parent_router.router_hostname), int(self.neighbor_router.router_hostname)))
            max_hostn = str(max(int(self.parent_router.router_hostname), int(self.neighbor_router.router_hostname)))
            bloc_prefix = min_hostn + max_hostn

            # avant dernier bloc :XXXX: (dans la partie hôte de l'IP) composé de juste l'hostname du routeur
            bloc_hostname = self.parent_router.router_hostname

            # dernier bloc :XXXX (dans la partie hôte de l'IP) composé du nom de l'interface 
            # (si interface 0, on met 10 pas 0)
            bloc_intname = self.name if self.name != "0" else "10"

            self.ip = self.ip_prefix[
                      :debut_masque - 1] + bloc_prefix + "::" + str(bloc_hostname) + ":" + bloc_intname + "/" + str(
                masque + 16)
            print("Craft IP : l'interface " + self.name + " du routeur " + str(
                self.parent_router.router_hostname) + " a l'IP " + self.ip)
        else:
            print("Erreur craft_ip : aucun routeur voisin sur l'interface",
                  self.name + ". Pour une interface loopback utiliser LoopbackInterface")

    def __repr__(self):
        return "(0/"+self.name+","+self.ip_prefix+")"


# l'ip est créée dès la création de l'interface
class LoopbackInterface(Interface):
    def __init__(self, ip_prefix, parent_router):
        super().__init__("lo0", ip_prefix, parent_router)
        debut_masque = self.ip_prefix.index("/")
        longueur_hostname = len(str(self.name))
        self.ip = self.ip_prefix[:debut_masque] + parent_router.routeur_hostname + "/128"
