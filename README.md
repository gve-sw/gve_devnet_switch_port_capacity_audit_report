# Switch Port Capacity Audit Script

This code repository contains a quick script to automate collection of port information from Cisco Catalyst switches.

This script can be run against any number of Catalyst Switches to collect the following per-interface data:
* Port Description
* Speed / Duplex
* Enabled / Admin Disabled
* Operational state (Up / Down)
* Media Type
* Input / Output counters

## Contacts
* Matt Schmitz (mattsc@cisco.com)

## Solution Components
* Catalyst Switches
* Scrapli / PyATS

## Installation/Configuration

**Clone repo:**
```bash
git clone <repo_url>
```

**Install required dependancies:**
```bash
pip install -r requirements.txt
```

**Provide device list**

In order to use this script, a YAML file of device addresses & credentials must be provided. This file must be named `devices.yml`

A sample file has been provided. The configuration takes the following format:
```
Devices:
  <device name>:
    address: <ip address>
    username: <password>
    password: <password>
    #Optional:
    enable: <enable pass>
    port: <non-standard SSH port>

# For example:
Devices:
  switch01:
    address: 10.10.10.2
    username: admin
    password: admin
  switch02:
    address: 10.10.10.3
    username: admin
    password: admin
    enable: admin
    port: 3022
```

## Usage

Run the application with the following command:

```
python generate_report.py
```

Script will attempt to connect to each device & run `show version` and `show interfaces` commands. It will then parse the output & write the collected information to a local CSV file.


# Screenshots

**Example of script execution:**

![/IMAGES/example_script.png](/IMAGES/example_script.png)

**Example of CSV report:**

![/IMAGES/example_output.png](/IMAGES/example_output.png)


### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.