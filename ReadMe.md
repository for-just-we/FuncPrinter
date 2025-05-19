
cmakelist中下面这段代码比较重要，删除容易导致编译错误

```cmake
if (NOT ${LLVM_ENABLE_RTTI})
    message(STATUS "close rtti")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif()
```

编译:

```shell
mkdir build && cd build
cmake -DLLVM_ROOT=<path/to/llvm> .. # 如果环境变量有，LLVM_ROOT也可以删除 
cmake --build . -j 8
```

运行: 

- 单个c文件: `./FuncPrinter test.c --`

- project下（以测试用例为例）: `./FuncPrinter -p testcases/project_test1/compile_commands.json testcases/project_test1/main.c testcases/project_test1/lib.c`。
比较麻烦的是需要一个个手动指定需要分析的c文件，不能自动指定。

- 用 `analyze.py` (本质是python套娃，就是读取 `compile_commands.json` 的内容然后自动分析所有的c文件), `python analyze.py -p=testcases/project_test1/build -e=build/FuncPrinter`