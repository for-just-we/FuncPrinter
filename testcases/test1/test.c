//
// Created by prophe cheng on 2025/5/19.
//

#define CALL_FUNC(x) \
    func_##x();      \
    ;  // 这个空语句会影响下一行的行号

// 函数1：普通函数（行号不受宏影响）
void func_a() {
    // 空函数
}

// 函数2：通过宏调用的函数（行号会被宏影响）
void func_b() {
    // 空函数
}

// 宏展开后会调用 func_a 和 func_b
void test_macro() {
    CALL_FUNC(a)  // 展开为：
    // func_a();
    // ;  // 这个空语句会影响下一行的行号
    CALL_FUNC(b)  // 展开为：
    // func_b();
    // ;  // 这个空语句会影响下一行的行号
}

/**
 * 另一个函数，用于验证行号
 **/
void func_c() {
    // 空函数
}

// 主函数（仅用于测试，实际 Clang 工具分析时可能不需要）
int main() {
    test_macro();
    return 0;
}