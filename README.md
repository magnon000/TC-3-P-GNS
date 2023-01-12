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
---
## Part 1: Network Configuration
### Consignes :
1. Un AS RIP un autre OSPF
2. Faire BGP
3. Une seule Area par AS
4. Faire que verticalement les 4 colonnes de routeurs centrales pour gagner du temps
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
* * * gateway-routers [3
* * * * router-number `int`
* * * * MED `str || int`3]2]
* * routers [4
* * * router-hostname `int`
* * * router-neighbors [5]
* * * * router-number `int`
* * * * interface `int`
* * * * neighbor-cost `int` (if needed)4]1]

## Part 3: Network Automation
* Python
* * import json
### 3.1 Architecture
physical network architecture -> JSON
### 3.2 Addressing
Automated
IP range :
1. as-prefix/32 -> physical interface
2. as-prefix/128 -> loopback
3. peering-prefix/32 -> AS-AS connection
### 3.3 Protocols
* IGP -> "intra-protocol"
* to which BGP AS a given router belongs -> "routers"
* iBGP/eBGP -> as["neighbor-as"] (to define eBGP routers)
### 3.4 Policies
3.4.1 BGP Policies
business relationship with the neighboring AS -> "local-pref" & "MED"
3.4.2 OSPF Metric Optimization
link metrics -> "neighbor-cost"

## Part 4: Deployment