# SPDX-FileCopyrightText: The vmnet-helper authors
# SPDX-License-Identifier: Apache-2.0

import ipaddress


def validate_network_options(p, args):
    """
    Validate the network options passed to run.
    """
    if args.network_name:
        if args.operation_mode:
            p.error("--network cannot be used with --operation-mode")
        if args.start_address:
            p.error("--network cannot be used with --start-address")
        if args.end_address:
            p.error("--network cannot be used with --end-address")
        if args.subnet_mask:
            p.error("--network cannot be used with --subnet-mask")

    if args.ip_address:
        if not (args.start_address and args.end_address and args.subnet_mask):
            p.error(
                "--ip-address requires --start-address, --end-address, --subnet-mask"
            )

    if args.start_address and args.end_address and args.subnet_mask:
        start_address = ipaddress.IPv4Interface(
            f"{args.start_address}/{args.subnet_mask}"
        )
        end_address = ipaddress.IPv4Interface(f"{args.end_address}/{args.subnet_mask}")
        subnet = start_address.network
        if end_address not in subnet:
            p.error("--end-address must be in the same subnet as --start-address")
        if end_address < start_address:
            p.error("--end-address must be higher than --start-address")

        if args.ip_address:
            ip_address = ipaddress.IPv4Interface(
                f"{args.ip_address}/{args.subnet_mask}"
            )
            if ip_address not in subnet:
                p.error("--ip-address must be in the requested subnet")
            if start_address <= ip_address <= end_address:
                p.error("--ip-address must be outside of the requested DHCP range")


def private_ipv4_address(ip):
    """
    Validates that "ip" is in the RFC 1918 private range.

    Returns an ipaddress.IPv4Address object, or raises ValueError if validation fails.
    """
    address = ipaddress.IPv4Address(ip)
    rfc1918_subnets = ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"]
    for subnet in rfc1918_subnets:
        network = ipaddress.IPv4Network(subnet)
        if address in network:
            return address
    raise ValueError(f"{ip} is not a valid RFC 1918 IP address")
