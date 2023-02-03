# Repository for TC-3-P-GNS
---
- [Repository for TC-3-P-GNS](#repository-for-tc-3-p-gns)
  - [Part 1: Network Configuration](#part-1-network-configuration)
    - [Consignes :](#consignes-)
    - [Première étape : déployer RIP et OSPF et BGP](#première-étape-déployer-rip-et-ospf-et-bgp)
  - [Part 2: Network Intent](#part-2-network-intent)
    - [JSON structure:](#json-structure)
  - [Part 3: Network Automation](#part-3-network-automation)
    - [3.1 Architecture](#31-architecture)
    - [3.2 Addressing](#32-addressing)
    - [3.3 Protocols](#33-protocols)
    - [3.4 Policies](#34-policies)
  - [Part 4: Deployment](#part-4-deployment)
    - [4.1 Load JSON config to Python persistent Object](#41-load-json-config-to-python-persistent-object)
    - [4.2 Pass persistent object to Python class](#42-pass-persistent-object-to-python-class)
    - [4.3 Choose one method to deploy the generated configurations](#43-choose-one-method-to-deploy-the-generated-configurations)
  - [Part 5: Constrain](#part-5-constrain)
---
## Part 1: Network Configuration
### Consignes :
1. Un AS RIP un autre OSPF
2. Faire BGP
3. Une seule Area par AS
4. Faire que verticalement les 4 colonnes de routeurs centrales pour gagner du temps (pas nécessaire)
### Première étape : déployer RIP et OSPF et BGP
1. Plan d’adressage de l’AS Z : `Part 1/config_ipv6` 
* IPv6
* Addresse entière du routeur : 
* * AS : numero_Routeur_Inf + numero_Routeur_Max :: numero_Routeur : num_Interface / 32
* Avec num_Interface = le numéro avant le / dans le nom de l'interface, sauf 0 qui est égal à 10.
* Règle générale (pas absolue) :
* * Interface liaison verticale : g1/0
* * Interface liaison horizontale : g2/0 - g1/0 (AS1) g1/0 - g2/0 (AS2) 
1. RIP et OSPF : `Part 1/config_ipv6_rip_ospf`
* OSPF area 0
2. eBGP et iBGP : `Part 1/config_bgp`
* Use loopback address for full mesh in each AS
* Do not pollute the BGP routing table in other AS
* * Route aggregation 
## Part 2: Network Intent
* JSON
* 2 AS qui ont un protocole intra domaine
* Chaque AS a des routeurs
* Chaque routeur a un identifiant et des voisins
### JSON structure:
* as [1
* * as-number `int`
* * intra-protocol `str`
* * as-prefix `str`
* * neighbor-as [2
* * * as-number `int`
* * * local-pref: `int`
* * * peering-prefix: `str`
* * * asbr [3
* * * * router-number `int`
* * * * MED `str || int`3]2]
* * routers [4
* * * router-hostname `int`
* * * router-neighbors [5]
* * * * neighbor-number `int`
* * * * interface `int`
* * * * neighbor-cost `int` (if needed)4]1]

## Part 3: Network Automation
* Python
* json as config input
* * dependence:
* * * tkinter 
* * * * possible ImportError on Ubuntu (try `sudo apt-get install python3-tk`)
* gns3fy (propositions_prof, not used because .gns3 is similar to .json)
### 3.1 Architecture
physical network architecture -> JSON
### 3.2 Addressing
Automated
IP range :
1. as-prefix/[multiple de 16] -> physical interface
2. as-prefix/128 -> loopback
3. peering-prefix/[multiple de 16] -> AS-AS connection
### 3.3 Protocols
* IGP -> "intra-protocol"
* to which BGP AS a given router belongs -> "routers"
* iBGP/eBGP -> as["neighbor-as"] (to define eBGP routers)
### 3.4 Policies
!!!! NON FAIT !!!! (manque de temps)
3.4.1 BGP Policies
business relationship with the neighboring AS -> "local-pref" & "MED"
3.4.2 OSPF Metric Optimization
link metrics -> "neighbor-cost"

## Part 4: Deployment
### 4.1 Load JSON config to Python persistent Object
lauch `0_start_load_json_save_pObj.py`

For the same network, this is required only once, then following methods `Drag and Drop`,  `Drag and Drop bot` and `Telnet`.
### 4.2 Pass persistent object to Python class
handle by `charge_objects.py`
### 4.3 Choose one method to deploy the generated configurations
`1_start_drag_and_drop.py`

`2_start_auto_deplacement.py`

`3_start_telnet.py`

## Part 5: Constrain
todo: shelve behaves different in Linux
- contrainte utilisateur : pour les IP d'interfaces connectées à un routeur, le masque ne doit pas être trop petit (2 blocs :XXXX:XXXX réservés à l'hôte) (donc /96 max ?)

- contrainte utilisateur : max 99 routeurs dans le projet

- contrainte utilisateur : peering prefix le même pour toutes les liaison d'un couple d'AS => ne supporte pas 2 interfaces d'1 routeur vers le même routeur du même AS voisin (=> pas de double liaison entre 2 routeurs d'AS différents)

- contrainte utilisateur : peering prefix de l'AS A vers l'AS B le même que de l'AS B vers l'AS A (PAS vérifié automatiquement par le script) EXTREMEMENT IMPORTANT

- contrainte utilisateur : une interface ne peut pas exister sans routeur (routeur parent nécessaire au constructeur)

- contrainte utilisateur : 1 seule protocole intra domaine par AS qui relie FORCEMENT tous les routeurs de l'AS

- contrainte utilisateur : peering prefix entre 2 as à spécifier obligatoirement (long bloc de commentaire qui dit l'inverse dans instruments.py mais c'est pour si jamais on a le temps)

- contrainte pour lecteur/éditeur du code : instruments.py très sale, fonction add_interface_from_neighbor_router() dans ASBR TRES TRES TRES BANCALE FAIRE TRES ATTENTION
