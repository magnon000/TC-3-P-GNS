# Repository for TC-3-P-GNS

Consignes :
Un AS RIP un autre OSPF
Faire BGP...

Une seule Area par AS

Faire que verticalement les 4 colonnes de routeurs centrales pour gagner du temps

Première étape : déployer RIP et OSPF et BGP



Plan d’adressage de l’AS Z :

Préfixe :
Z:numeroRouteurInfnumeroRouteurMax::

Addresse entière du routeur :
Z:numeroRouteurInfnumeroRouteurMax::numeroRouteur:numInterface

avec numInterface = le numéro avant le / dans le nom de l'interface, sauf 0 qui est égal à 10




\/ NON \/
Règle générale (pas absolue) :
Interface liaison verticale : 1/0
Interface liaison horizontale
/\ NON /\

---
*Jan  5 11:04:25.339: %BGP-3-NOTIFICATION: received from neighbor 3:68::8:2 active 2/8 (no supported AFI/SAFI) 3 bytes 000000
*Jan  5 11:04:25.343: %BGP-5-NBR_RESET: Neighbor 3:68::8:2 active reset (BGP Notification received)
*Jan  5 11:04:25.347: %BGP-5-ADJCHANGE: neighbor 3:68::8:2 active Down BGP Notification received
*Jan  5 11:04:25.347: %BGP_SESSION-5-ADJCHANGE: neighbor 3:68::8:2 IPv6 Unicast topology base removed from session  BGP Notification
*Jan  5 11:04:30.099: %BGP-5-NBR_RESET: Neighbor 3:68::8:2 passive reset (BGP Notification sent)
*Jan  5 11:04:30.103: %BGP-5-ADJCHANGE: neighbor 3:68::8:2 passive Down AFI/SAFI not supported
*Jan  5 11:04:37.659: %BGP-5-ADJCHANGE: neighbor 3:68::8:2 Up
---