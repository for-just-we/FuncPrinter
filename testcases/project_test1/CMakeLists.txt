cmake_minimum_required(VERSION 3.10)
project(FunctionPrinterTest C)

# use cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 ..

# 添加两个源文件
add_executable(FunctionPrinterTest main.c lib.c)