//
// Created by prophe cheng on 2025/5/19.
//

#include "common.h"

void funcB();

void funcA() {
    staticHelper();
}

int main() {
    funcA();
    funcB();
    return 0;
}