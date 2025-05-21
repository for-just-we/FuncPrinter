#!/usr/bin/env python3

import argparse
import json
import os
from typing import List, Dict, Any
import subprocess

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", required=True, help="Path to build directory")
    parser.add_argument("-e", "--exe", required=False, default="FuncPrinter", help="executable path")
    parser.add_argument("-extra", "--extra_arg", default="")
    return parser


def generate_preprocess_cmd(arguments: List[str], file_name):
    new_argument: List[str] = list()
    output_file = ""
    for i in range(len(arguments)):
        arg = arguments[i]
        if arg == "-emit-llvm":
            continue
        elif arg == "-c":
            new_argument.append("-E")
        elif arg == "-o":
            output_file = arguments[i + 1]
            continue
        elif arg == output_file:
            continue
        else:
            new_argument.append(arg)
    new_argument.extend(["-o", file_name + ".tmp.c"])
    return new_argument



# bear生成的compile_commands.json包括file和directory、cmake生成的只有file
def main():
    parser = get_parser()
    args = parser.parse_args()
    analyzed_files = set()
    analyzed_funcs = set()

    build_path = args.path
    compile_commands_path = os.path.join(build_path, "compile_commands.json")

    if not os.path.isfile(compile_commands_path):
        print(f"Error: {compile_commands_path} does not exist.")
        return

    with open(compile_commands_path, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    # data 应该是 List[Dict]
    for entry in data:
        # 设置当前工作目录
        work_dir = entry.get("directory", build_path)
        file_name = entry.get("file")
        cur_file = os.path.join(entry.get("directory"), file_name)
        if cur_file in analyzed_files:
            continue
        if not os.path.exists(cur_file):
            continue
        analyzed_files.add(cur_file)
        total_command = "{} -p {} {}".format(args.exe, build_path, cur_file)
        if args.extra_arg != "":
            total_command += " --extra-arg={}".format(args.extra_arg)

        preprocess_success = False
        # 执行命令
        try:
            result = subprocess.run(total_command, shell=True, check=True, capture_output=True, text=True, cwd=work_dir)
            lines = result.stdout.split('\n')

            cur_analyzed_datas = {}

            for line in lines:
                if len(line) == 0:
                    continue
                if line == "\n":
                    continue
                json_data = json.loads(line)
                file_name = json_data["file"]
                if not os.path.isabs(file_name):
                    json_data["file"] = os.path.normpath(os.path.join(work_dir, file_name))
                # 不重复输出
                func_key = (json_data["file"], json_data["line"], json_data["name"])
                if func_key in analyzed_funcs:
                    continue
                analyzed_funcs.add(func_key)
                func_dict_key = json_data["file"] + ":" + str(json_data["line"]) +":" + json_data["name"]
                cur_analyzed_datas[func_dict_key] = json_data


            preprocess_args = generate_preprocess_cmd(entry.get("arguments"), file_name)
            # generate preprocessed file
            subprocess.run(" ".join(preprocess_args), shell=True, check=True, capture_output=True, text=True, cwd=work_dir)
            # generate command for analyzing preprocessed file
            analyze_preprocess_file_cmd = "{} {} --".format(args.exe, file_name + ".tmp.c")
            result_preprocessed = subprocess.run(analyze_preprocess_file_cmd, shell=True, check=True, capture_output=True, text=True, cwd=work_dir)
            subprocess.run("rm -f {}".format(file_name + ".tmp.c"), shell=True, check=True, capture_output=True, text=True, cwd=work_dir)
            lines_preprocessed = result_preprocessed.stdout.split('\n')
            # traverse preprocessed results
            printed_datas = set()
            for line in lines_preprocessed:
                if len(line) == 0:
                    continue
                if line == "\n":
                    continue
                json_data = json.loads(line)
                file_name = json_data["file"]
                if not os.path.isabs(file_name):
                    json_data["file"] = os.path.normpath(os.path.join(work_dir, file_name))
                # 不重复输出
                func_key = json_data["file"] + ":" + str(json_data["line"]) +":" + json_data["name"]
                if func_key in cur_analyzed_datas.keys() and func_key not in printed_datas:
                    cur_analyzed_datas[func_key]["preprocessed_code"] = json_data["code"]
                    str_content = json.dumps(cur_analyzed_datas[func_key])
                    print(str_content)
                    printed_datas.add(func_key)

            preprocess_success = True

        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print("Error output:")
            print(e.stderr)

        finally:
            if not preprocess_success:
                for func_key, json_data in cur_analyzed_datas.items():
                    str_content = json.dumps(cur_analyzed_datas[func_key])
                    print(str_content)




if __name__ == '__main__':
    main()