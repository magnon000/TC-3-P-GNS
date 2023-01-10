# Repository for TC-3-P-GNS
---
- [Repository for TC-3-P-GNS](#repository-for-tc-3-p-gns)
  - [Part 1 : Network Configuration](#part-1--network-configuration)
    - [Consignes :](#consignes-)
    - [Première étape : déployer RIP et OSPF et BGP](#première-étape-déployer-rip-et-ospf-et-bgp)
  - [Part 2 : Network Intent](#part-2--network-intent)
---
## Part 1 : Network Configuration
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
## Part 2 : Network Intent
