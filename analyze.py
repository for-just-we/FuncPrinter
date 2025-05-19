#!/usr/bin/env python

import argparse
import json
import os
from typing import List, Dict
import subprocess

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", required=True, help="Path to build directory")
    parser.add_argument("-e", "--exe", required=False, default="FuncPrinter", help="executable path")
    parser.add_argument("-extra", "--extra_arg", default="")
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    build_path = args.path
    compile_commands_path = os.path.join(build_path, "compile_commands.json")

    if not os.path.isfile(compile_commands_path):
        print(f"Error: {compile_commands_path} does not exist.")
        return

    with open(compile_commands_path, "r", encoding="utf-8") as f:
        data: List[Dict[str, str]] = json.load(f)

    # data 应该是 List[Dict]
    file_names = ""
    for entry in data:
        file_name = entry.get("file")
        if "directory" in entry.keys():
            file_name = os.path.join(entry.get("directory"), file_name)
        if file_name:
            file_names += file_name + " "

    total_command = "{} -p {} {}".format(args.exe, build_path, file_names)
    if args.extra != "":
        total_command += " --extra-arg={}".format(args.extra)
    # 执行命令
    try:
        result = subprocess.run(total_command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        print("Error output:")
        print(e.stderr)


if __name__ == '__main__':
    main()