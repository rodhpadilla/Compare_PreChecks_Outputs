#!/usr/bin/env python3

__author__ = "Rodrigo H Padilla"
__email__ = "rod.hpadilla@gmail.com"


import difflib
import argparse
from netmiko import ConnectHandler
from devices import device_list


def backup_config(device, command_list, filename):
    with ConnectHandler(**device) as net_connect:
        with open(filename, "w") as file_command_outputs:
            file_command_outputs.write(f"Device: {device['host']}\n")
            for command in command_list:
                output_command = net_connect.send_command(command, expect_string=r"#")
                file_command_outputs.write("\n\n")
                file_command_outputs.write(f" {command} ".center(90, "="))
                file_command_outputs.write("\n")
                file_command_outputs.write(f"\n{output_command}")
    return f"SUCCESS --> {device['host']}"


def report_man(device):
    try:
        sh_int_PRE = f"{device['host']}--pre.txt"
        sh_int_POST = f"{device['host']}--post.txt"
        pre_lines = open(sh_int_PRE).readlines()
        post_lines = open(sh_int_POST).readlines()
        difference = difflib.HtmlDiff().make_file(
            pre_lines, post_lines, sh_int_PRE, sh_int_POST
        )
        report_name = f"DIFF-REPORT__{device['host']}.html"
        difference_report = open(report_name, "w")
        difference_report.write(difference)
        difference_report.close()
        print(f"Report Success ==> {device['host']}")
    except Exception:
        print(f"Report Failed ==> {device['host']}")


def get_args():
    parser = argparse.ArgumentParser(description="Pre/Post/Comparator Tool")

    # Type of pre-checks
    parser.add_argument(
        "-t",
        "--type",
        required=True,
        choices=("pre", "post"),
        help="PRE or POST",
    )

    arg = parser.parse_args()
    return arg


def main():
    args = get_args()
    job_type = args.type
    commands = [
        "show clock",
        "show int description",
        "show ip interface brief",
        "show ip route",
        "show inventory",
        "show run",
    ]
    for device in device_list:
        filename = f"{device['host']}--{job_type}.txt"
        result_connect = backup_config(device, commands, filename)
        if "SUCCESS" in result_connect:
            print(result_connect)
        else:
            print(f"FAILED --> {device['host']}")

    # Running reports for POST
    if job_type == "post":
        print("\n\nComparing PREvsPOST...\n")
        for gear in device_list:
            report_man(gear)


if __name__ == "__main__":
    main()
