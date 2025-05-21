//
// Created by prophe cheng on 2025/5/16.
//
#include "clang/AST/AST.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Lex/MacroArgs.h"
#include "clang/Lex/PPCallbacks.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/JSON.h"

#include <unordered_set>
#include <mutex>

using namespace clang;
using namespace clang::tooling;
using namespace llvm;
using namespace llvm::json;
using namespace std;

// 定义命令行选项分类
cl::OptionCategory FunctionInfoPrinterCategory("Function Info Printer");

static unordered_set<std::string> GlobalPrintedFunctions;
static mutex GlobalMutex;

namespace clang {

class FunctionVisitor : public RecursiveASTVisitor<FunctionVisitor> {
public:
    FunctionVisitor(ASTContext &Context,
                    unordered_set<string> &PrintedFunctions,
                    mutex &Mutex)
            : Context(Context), RW(Context.getSourceManager(), Context.getLangOpts()),
              PrintedFunctions(PrintedFunctions), Mutex(Mutex) {}

    bool VisitFunctionDecl(FunctionDecl* FD) {
        if (!FD->isThisDeclarationADefinition() || Context.getSourceManager().isInSystemHeader(FD->getLocation()))
            return true;

        const SourceManager &SM = Context.getSourceManager();
        SourceLocation SL = FD->getBeginLoc();
        PresumedLoc PLoc = SM.getPresumedLoc(SL);
        if (PLoc.isInvalid())
            return true;

        string FilePath = PLoc.getFilename();
        unsigned Line = PLoc.getLine();
        string FuncName = FD->getNameAsString();

        // 构造唯一标识
        string Key = FilePath + ":" + to_string(Line) + ":" + FuncName;

        // 如果没有下面代码.h中的static函数可能被多次输出
        {
            lock_guard<std::mutex> Lock(Mutex);
            if (PrintedFunctions.find(Key) != PrintedFunctions.end())
                return true;
            PrintedFunctions.insert(Key);
            // 获取预处理前的source code
            SourceLocation Start = SM.getExpansionLoc(FD->getBeginLoc());
            SourceLocation End = SM.getExpansionLoc(FD->getEndLoc());
            SourceRange SR(Start, End);
            string FuncCode = RW.getRewrittenText(SR);
            Object FuncInfo{
                    {"file", std::move(FilePath)},
                    {"line", Line},
                    {"name", std::move(FuncName)},
                    {"code", std::move(FuncCode)}};

            // 先用右值构造一个 json::Value
            Value FuncInfoVal(move(FuncInfo));
            outs() << FuncInfoVal << "\n";
        }


        return true;
    }

private:
    ASTContext &Context;
    Rewriter RW;
    unordered_set<std::string> &PrintedFunctions;
    mutex &Mutex;
};

class FunctionConsumer : public ASTConsumer {
public:
    FunctionConsumer(ASTContext &Context,
                     std::unordered_set<std::string> &PrintedFunctions,
                     std::mutex &Mutex)
            : Visitor(Context, PrintedFunctions, Mutex) {}

    void HandleTranslationUnit(ASTContext &Context) override {
        Visitor.TraverseDecl(Context.getTranslationUnitDecl());
    }

private:
    FunctionVisitor Visitor;
};

class FunctionAction : public PluginASTAction {
public:
    unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI, StringRef) override {
        return make_unique<FunctionConsumer>(CI.getASTContext(), GlobalPrintedFunctions, GlobalMutex);
    }

    bool ParseArgs(const CompilerInstance &CI,
                   const std::vector<std::string> &args) override {
        return true;
    }
};
} // namespace

int main(int argc, const char **argv) {
    llvm::Expected<CommonOptionsParser> OptionsParserOrErr = CommonOptionsParser::create(argc, argv, FunctionInfoPrinterCategory);
    if (!OptionsParserOrErr) {
        errs() << "Error parsing command-line options: " << llvm::toString(OptionsParserOrErr.takeError()) << "\n";
        return 1;
    }
    CommonOptionsParser &OptionsParser = *OptionsParserOrErr;
    ClangTool Tool(OptionsParser.getCompilations(),
                   OptionsParser.getSourcePathList());

    int ret = Tool.run(newFrontendActionFactory<FunctionAction>().get());
    return ret;
}
