from charge_objects import *
import telnetlib  # DeprecationWarning: 'telnetlib' is deprecated and slated for removal in Python 3.13

PORT_min = 3000
print(router_1_obj.__dict__)
with shelve.open(shelve_path) as obj:
    as_num_list = obj['as_number_list']
    r_num_list = obj['router_number_list']


def config_input_head(teln) -> None:
    teln.write(b'\r\n')
    teln.write(b'enable\r\n')
    teln.write(b'conf t\r\n')
    teln.write(b'ipv6 unicast-routing\r\n')


def config_input_inter(teln) -> None:
    teln.write(b'ipv6 enable\r\n')
    teln.write(b'no shutdown\r\n')


def config_1r(router_obj, r_index: int):
    tn = telnetlib.Telnet("localhost", PORT_min + r_index)
    config_input_head(tn)
    try:
        exec("interface_list = router_{}_obj.interfaces\r\n".format(r_index))
    except NameError:
        exec("interface_list = asbr_{}_obj.interfaces\r\n".format(r_index))
    # config ospf/rip
    as_num = router_obj.parent_AS.AS_number  # str
    as_protocol = router_obj.intradomain_protocol
    tn.write(b'conf t\r\n')
    exec("tn.write(b'ipv6 router ospf {}\r\n')".format(as_num))
    exec("tn.write(b'router-id {}\r\n')".format(router_obj.router_ID))

    # config all interfaces
    for inter in interface_list:
        if inter.name == 'lo0':  # config all param in LOOPBACK interface
            tn.write(b'inter Loopback0\r\n')
            config_input_inter(tn)
            exec("tn.write(b'ipv6 address {}\r\n')".format(inter.ip))
            if as_protocol == 'rip':
                exec("tn.write(b'ipv6 router rip AS{}rip\r\n')".format(as_num))
            elif as_protocol == 'ospf':
                exec("tn.write(b'ipv6 ospf {} area 0\r\n')".format(as_num))
            tn.write(b'redistribute connected\r\n')
            tn.write(b'exit\r\n')
        else:  # GE interfaces
            exec("tn.write(b'inter GigabitEthernet {}/0\r\n')".format(inter.name))
            config_input_inter(tn)
            exec("tn.write(b'ipv6 address {}\r\n')".format(inter.ip))
            if router_obj.is_asbr:
                if as_protocol == 'rip':
                    exec("tn.write(b'ipv6 router rip AS{}rip\r\n')".format(as_num))
                elif as_protocol == 'ospf':
                    exec("tn.write(b'ipv6 ospf {} area 0\r\n')".format(as_num))
                tn.write(b'redistribute connected\r\n')
            tn.write(b'exit\r\n')

    # eBGP/iBGP
    exec("tn.write(b'router bgp {}\r\n')".format(as_num))
    tn.write(b'no bgp default ipv4-unicast\r\n')
    exec("tn.write(b'bgp router-id {}\r\n')".format(router_obj.router_ID))
    if router_obj.is_asbr:  # eBGP
        routers_list = router_obj.parent_AS.routers
        remote_as_num = router_obj.parent_AS.AS_number
        routers_list.remove(router_obj)
        for router in routers_list:
            lo_ip = router.interfaces[0].ip  # index 0 corresponds lo0
            exec("tn.write(b'neighbor {} remote-as {}\r\n')".format(lo_ip, remote_as_num))
            exec("tn.write(b'neighbor {} update-source Loopback0\r\n')".format(lo_ip))
            tn.write(b'address-family ipv6 unicast\r\n')
            exec("tn.write(b'neighbor {} activate\r\n')".format(lo_ip))
            tn.write(b'exit\r\n')
        # for inter in all inters
        # if inter.multi_AS
        # then corresponding_interface
        # corresponding_interface.parent_router.parent_AS.AS_num
        for inter in router_obj.interfaces:
            if inter.multi_AS:
                cor_inter = inter.corresponding_interface
                cor_inter_ip = cor_inter.ip
                remote_as_cor_num = cor_inter.parent_router.parent_AS.AS_num
                exec("tn.write(b'neighbor {} remote-as {}\r\n')".format(cor_inter_ip, remote_as_cor_num))
                tn.write(b'address-family ipv6 unicast\r\n')
                exec("tn.write(b'neighbor {} activate\r\n')".format(cor_inter_ip))
                tn.write(b'exit\r\n')
        tn.write(b'address-family ipv6 unicast\r\n')
        exec("tn.write(b'aggregate-address {} summary-only\r\n')".format(router_obj.interfaces[0].ip))
        tn.write(b'exit\r\n')
    else:  # iBGP
        routers_list = router_obj.parent_AS.routers
        remote_as_num = router_obj.parent_AS.AS_number
        routers_list.remove(router_obj)
        for router in routers_list:
            lo_ip = router.interfaces[0].ip  # index 0 corresponds lo0
            exec("tn.write(b'neighbor {} remote-as {}\r\n')".format(lo_ip, remote_as_num))
            exec("tn.write(b'neighbor {} update-source Loopback0\r\n')".format(lo_ip))
            tn.write(b'address-family ipv6 unicast\r\n')
            exec("tn.write(b'neighbor {} activate\r\n')".format(lo_ip))
            tn.write(b'exit\r\n')
    tn.write(b'end\r\n')


for router_index in range(len((r_num_list))):
    try:
        exec("config_1r(router_{}_obj, router_index)".format(r_num_list[router_index]))
    except NameError:
        exec("config_1r(asbr_{}_obj, router_index)".format(r_num_list[router_index]))
