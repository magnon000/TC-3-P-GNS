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
    def add_neighbor_as(self, neighbor, gateways, peering_prefix=None):  # gateways: object ASBR
        if type(gateways) != 'list':
            gateways = [gateways]

        self.AS_neighbors[neighbor.AS_number] = gateways
        self.AS_neighbors_peering_prefixes[neighbor.AS_number] = peering_prefix

    def craft_ip_on_all_routers_interfaces(self):
        for router in self.routers:
            router.craft_ip_on_all_interfaces()

    def get_router_by_hostname(self, hostname):
        for routeur in self.routers:
            if routeur.router_hostname == hostname:
                return routeur
        print("Erreur get_router_by_hostname: le routeur " + str(hostname) + " n'est pas dans l'AS " + self.AS_number)

    def get_sorted_list_of_routers(self):
        sorted_routers = self.routers
        sorted_routers.sort(key=lambda routeur: routeur.router_hostname)
        return sorted_routers

    # pas très joli (aurait du être géré automatiquement)
    # mais ça peut être utile si un jour on utilise la liste des gateways
    # à lancer lorsque tous les voisins sont connus avec au moins 1 gateway
    # not utiliser in charge_objects
    def update_gateways(self):
        for routeur in self.routers:
            if routeur.is_asbr():
                for interface in routeur.interfaces:
                    if (not interface.is_loopback()) and interface.multi_AS:
                        as_neigh = interface.neighbor_router.parent_AS.AS_number
                        if routeur not in self.AS_neighbors[as_neigh]:
                            self.AS_neighbors[as_neigh].append(routeur)


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
    def __init__(self, num: int, parent_as: AS = None):
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
    # not used in charge_objects
    def add_interface_from_neighbor_router(self, interface_name, neighbor_router):
        new_interface = Interface(interface_name, self.parent_AS.AS_prefix, self, neighbor_router)
        self.interfaces.append(new_interface)

    # paramètre dict: clé = interface name, élement = routeur
    # Ne pas utiliser pour les ASBR (héritée)
    # not used in charge_objects
    def add_many_interfaces_from_routers(self, routeurs: dict):
        for interface in routeurs:
            self.add_interface_from_neighbor_router(interface, routeurs[interface])

    def add_loopback_interface(self):
        new_interface = LoopbackInterface(self.parent_AS.AS_prefix, self)
        self.interfaces.append(new_interface)

    def craft_ip_on_all_interfaces(self):
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

    def get_loopback_interface(self):
        for interface in self.interfaces:
            if interface.is_loopback():
                return interface

    def get_interface_by_name(self, name):
        name = str(name)
        for interface in self.interfaces:
            if interface.name == name:
                return interface
        print("Erreur: le routeur " + str(self.router_hostname) + " n'a aucune interface 0/" + name)

    def get_sorted_list_of_interfaces(self):
        sorted_interfaces = self.interfaces
        sorted_interfaces.sort(key=lambda interface: interface.name)
        return sorted_interfaces

    def __str__(self):
        return "(Routeur: N°" + str(self.router_hostname) + ")"

    def __repr__(self):
        return "(Routeur: N°" + str(self.router_hostname) + ")"

    def description(self):
        print("------------------")
        print("Le routeur", self.router_hostname, "appartient à l'AS", self.parent_AS.AS_number)
        print("Ses interfaces sont (nom,prefixe) :", self.interfaces)
        print("Ses routeurs voisins sont :", self.get_neighbor_routers())
        print("------------------")

    def is_asbr(self):
        return False


class ASBR(Router):
    # Conseillé de créer l'ASBR avec un AS parent... NON, OBLIGATOIRE SINON NE FONCTIONNE PAS
    def __init__(self, num, parent_as):
        super().__init__(num, parent_as)

    def add_existing_interfaces(self, interface):
        self.interfaces.append(interface)

    # fonction très mal faite mais trop avancée pour changer : SI ROUTEUR D'UN NOUVEL AS, PRECISER PEERING PREFIX (il
    # sera ajouté dans la liste des peering prefixes de l'AS parent
    def add_interface_from_neighbor_router(self, interface_name, neighbor_router, peering_prefix=None):
        # cas AS différent
        if self.parent_AS.AS_number != neighbor_router.parent_AS.AS_number:
            # cas AS différent ET nouveau (pas dans la liste des AS voisins de l'AS parent)
            if neighbor_router.parent_AS.AS_number not in self.parent_AS.AS_neighbors:
                # si pas de peering prefix en paramètre
                if peering_prefix is None:
                    print("ERREUR: add_interface_from_neighbor_router sur l'interface", interface_name, "du routeur",
                          self.router_hostname)
                    print("le routeur voisin", neighbor_router.router_hostname, "est dans un AS non enregistré")
                    print("C'est possible mais alors il faut préciser un peering_prefix en paramètres")
                    new_interface = None
                else:
                    self.parent_AS.add_neighbor_as(neighbor_router.parent_AS, self, peering_prefix)
                    print("L'AS", neighbor_router.parent_AS.AS_number, "n'était pas dans la liste des AS voisins de",
                          self.parent_AS, " il a été rajouté")
                    new_interface = Interface(interface_name, peering_prefix, self, neighbor_router)
            # cas AS différent mais connu de l'AS parent (=> peering prefix)
            else:
                peering_prefix = self.parent_AS.AS_neighbors_peering_prefixes[neighbor_router.parent_AS.AS_number]
                new_interface = Interface(interface_name, peering_prefix, self, neighbor_router)
        # cas même AS
        else:
            new_interface = Interface(interface_name, self.parent_AS.AS_prefix, self, neighbor_router)
        self.interfaces.append(new_interface)

    def __str__(self):
        return "(ASBR: " + str(self.router_hostname) + ")"

    def __repr__(self):
        return "(ASBR: " + str(self.router_hostname) + ")"

    def is_asbr(self):
        return True


class Interface:
    def __init__(self, number: int, ip_prefix: str, parent_router: Router, neighbor_router: Router):
        self.ip = None
        self.name = str(number)
        self.ip_prefix = ip_prefix  # AS_prefix, not subnetwork prefix !
        self.parent_router = parent_router
        self.ip_no_mask = None # créé après craft_ip()
        self.neighbor_router = neighbor_router  # config in JSON, don't know neighbor router: value=None
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
            self.ip_no_mask = self.ip_prefix[
                      :debut_masque - 1] + bloc_prefix + "::" + str(bloc_hostname) + ":" + bloc_intname
            self.ip_prefix = self.ip_prefix[
                      :debut_masque - 1] + bloc_prefix + "::/" + str(masque + 16)
            # print("Craft IP : l'interface " + self.name + " du routeur " + str(
            #     self.parent_router.router_hostname) + " a l'IP " + self.ip)
        else:
            print("Erreur craft_ip : aucun routeur voisin sur l'interface",
                  self.name + ". Pour une interface loopback utiliser LoopbackInterface")

    def corresponding_interface(self):
        if self.ip is not None:
            for en_face_interface in self.neighbor_router.interfaces:
                if en_face_interface.neighbor_router == self.parent_router:
                    return en_face_interface
        print("ERREUR: Aucun routeur en face (ce n'est pas possible donc erreur très grave)")

    def __repr__(self):
        if self.ip is None:
            return "(g" + self.name + '/0' + "," + self.ip_prefix + ")"
        else:
            return "(g" + self.name + '/0' + "," + self.ip + ")"

    def is_loopback(self):
        return False


# l'ip est créée dès la création de l'interface
class LoopbackInterface(Interface):
    def __init__(self, ip_prefix, parent_router):
        self.name = "lo0"
        self.ip_prefix = ip_prefix
        self.parent_router = parent_router
        debut_masque = self.ip_prefix.index("/")
        longueur_hostname = len(str(self.name))
        self.ip = self.ip_prefix[:debut_masque] + str(parent_router.router_hostname) + "/128"
        self.ip_no_mask = self.ip_prefix[:debut_masque] + str(parent_router.router_hostname)

    def craft_ip(self):
        pass

    def __repr__(self):
        return "("+self.name+","+self.ip+")"   # print l'ip entière (car créée dans __init__ donc existe sûr)

    def is_loopback(self):
        return True
