"""
Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""


import os

import yaml
from scrapli.driver.core import IOSXEDriver
from rich import print
from rich.progress import Progress
from rich.panel import Panel
from time import sleep
from datetime import datetime
import csv

filename = datetime.now().strftime(f"%Y%m%d-%H%M") + "_switch_ports.csv"

def loadDevices():
    """
    Load device inventory from devices.yml
    """
    with open("devices.yml", "r") as config:
        devicelist = yaml.full_load(config)
    return devicelist["Devices"]


def connectToDevice(deviceconfig):
    """
    Parse device config data & open SSH connection to target device
    """
    device = {}
    device["host"] = deviceconfig["address"]
    device["auth_username"] = deviceconfig["username"]
    device["auth_password"] = deviceconfig["password"]
    device["auth_strict_key"] = False
    device["timeout_socket"] = 10
    device["timeout_ops"] = 10
    # Avoid issue with weak ciphers
    device["transport_options"] = {
        "open_cmd": [
            "-o",
            "KexAlgorithms=+diffie-hellman-group-exchange-sha1",
            "-o",
            "Ciphers=+aes256-cbc",
        ]
    }
    # If device needs special port for SSH
    try:
        device["port"] = deviceconfig["port"]
    except KeyError:
        pass
    # Check if enable password is needed
    try:
        device["enable"] = deviceconfig["auth_secondary"]
    except KeyError:
        pass 
    # Open device connection
    conn = IOSXEDriver(**device)
    try:
        conn.open()
        err = None
    except Exception as e:
        return None, e
    return conn, err


def getInterfaceInfo(device):
    """
    Issue 'Show Interfaces' command to device
    Process data & populate dict with interface status
    """
    # Send command to device
    resp = device.send_command("show interfaces")
    # Parse raw CLI using Genie
    intdata = resp.genie_parse_output()
    return intdata


def processInterfaces(device, systeminfo, interfaces):
    """
    Write each interface to CSV
    """

    with open(filename, "a") as file:
        writer = csv.writer(file)
        for interface in interfaces:
            inttype = interfaces[interface]["type"]
            # Skip VLAN or EtherChannel interfaces
            if "SVI" in inttype or "EtherChannel" in inttype:
                continue
            # If no interface description exists, key doesn't exist
            try:
                description = interfaces[interface]["description"]
            except KeyError:
                description = ""

            # If no media type exists, key doesn't exist
            try:
                media = interfaces[interface]["media_type"]
            except KeyError:
                media = "Unknown"

            # Write to CSV
            writer.writerow(
                [
                device,
                systeminfo["serial"],
                systeminfo["model"],
                interface,
                description,
                interfaces[interface]["enabled"],
                interfaces[interface]["oper_status"],
                media,
                interfaces[interface]["port_speed"],
                interfaces[interface]["duplex_mode"],
                interfaces[interface]["mtu"],
                interfaces[interface]["counters"]["in_octets"],
                interfaces[interface]["counters"]["out_octets"],
                interfaces[interface]["counters"]["last_clear"],
                ]
            )



def writeCSVHeaders():
    """
    Write initial headers to CSV file
    """
    with open(filename, "a") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Switch Name",
                "Serial",
                "Model",
                "Interface Name",
                "Description",
                "Enabled",
                "Operational Status",
                "Media Type",
                "Speed",
                "Duplex",
                "MTU",
                "In Octets",
                "Out Octets",
                "Last Cleared"
            ]
        )


def getSystemInfo(device):
    """
    Issue 'Show Version' command to device
    Return serial number and model
    """
    resp = device.send_command("show version")
    parsed = resp.genie_parse_output()
    sysinfo = {}
    sysinfo["serial"] = parsed["version"]["chassis_sn"]
    sysinfo["model"] = parsed["version"]["chassis"]
    return sysinfo


def run():
    print("Starting...\n\n")
    # Load all of our devices from config, then add to DB
    print(Panel.fit("Load devices from config file", title="Step 1"))
    devicelist = loadDevices()
    print(f"Found {len(devicelist)} device(s) to work on.\n\n")

    # Init CSV file
    writeCSVHeaders()

    print(Panel.fit("Collect interface data", title="Step 2"))
    # Iterate through each device for processing
    with Progress() as progress:
        overall_progress = progress.add_task(
            "Overall Progress", total=len(devicelist), transient=True
        )
        counter = 1
        for device in devicelist:
            # Open device connection
            progress.console.print(
                f"Attempting to connect to {device}. ({str(counter)} of {len(devicelist)})"
            )
            devcon, err = connectToDevice(devicelist[device])
            if err:
                progress.console.print(f"[red] Failed to connect. Error: {err}")
                progress.update(overall_progress, advance=1)
                counter += 1
                continue
            if devcon:
                progress.console.print(f"[green] Connected!")
                try:
                    # Query device for system & port info
                    system = getSystemInfo(devcon)
                    interfaces = getInterfaceInfo(devcon)
                except Exception as e:
                    progress.console.print(f"[red] Failed to collect data. Error: {e}")
                    progress.update(overall_progress, advance=1)
                    counter += 1
                    continue

                # Process data & write to csv
                processInterfaces(device, system, interfaces)

            progress.update(overall_progress, advance=1)
            counter += 1

    print()
    print(Panel.fit("Done!"))
    print(f"File saved to: {filename}\n")


if __name__ == "__main__":
    run()
