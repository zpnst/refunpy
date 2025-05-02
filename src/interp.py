import argparse

from .refmt import fmt
from .modules import modules as m
from .parser import main_ast, lib_ast

from libs.refalpy.refalpy import refal

imports = {
    'add': lambda arg: (arg[0] + arg[1],),
    'sub': lambda arg: (arg[0] - arg[1],),
    'mul': lambda arg: (arg[0] * arg[1],),
    'div': lambda arg: (arg[0] // arg[1],),
    
    'eq': lambda arg: (arg[0] == arg[1],),
    'neq': lambda arg: (arg[0] != arg[1],),
    'grt': lambda arg: (arg[0] > arg[1],),
    'less': lambda arg: (arg[0] < arg[1],),
    'lesseq': lambda arg: (arg[0] <= arg[1],),
    'grteq': lambda arg: (arg[0] >= arg[1],),
    
    '_or': lambda arg: (arg[0] or arg[1],),
    '_and': lambda arg: (arg[0] and arg[1],), 

    'cond': lambda arg: arg[1] if arg[0] else arg[2],
    'expand': lambda arg: (arg[0] * int(arg[1][0]),),
    
    'typeof': lambda arg: ('int',) if isinstance(arg[0], int) else ('slice',) if\
        isinstance(arg[0], str) and arg[0].startswith('"') and arg[0].endswith('"')\
            else ('var',) if isinstance(arg[0], str) else type(arg[0]).__name__,
            
    'mkast': lambda path: lib_ast("contracts/" + path[0]),
    'decr': lambda arg: (int(arg[0] - 1 ,),) if (arg[0] - 1) else tuple(),
    
    'prout': lambda arg: (eval(f"print({arg[0]}, end='')"), ())[~0],
}

        
@refal(
    imports=imports, 
    modules=[m.utils, m.stmts, m.exprs, m.mks, m.mem, m.tvm]
)
def refun():
    '''
    The main set of 
    rules of the FunC interpreter
'''
    
    # -- GLOB
    
    glob[e.h, {'const', s.var, t.expr}, e.oth, t.ctx] =\
        glob[e.h, e.oth, stmt[{'const', s.var, t.expr}, t.ctx, {}]]  
        
    glob[e.h, {'include', s.path}, e.oth, t.ctx] =\
        glob[e.h, stmt[{'include', s.path}, t.ctx, {}], e.oth, t.ctx] 
          
    glob[e.h, {'func', {'main', e.o}, e.mb}, e.t, {e.g, 'funcs', {e.f}}] =\
        interp[e.mb, {e.g, 'funcs', {e.f, {}}}, {e.h}]

    # -- INTERP
    
    interp[{t.stmt, e.block}, t.ctx, t.fns] =\
        interp[{e.block}, stmt[t.stmt, t.ctx, t.fns], t.fns]
        
    interp[{}, t.ctx, t.fns] = t.ctx
    interp[t.ctx] = t.ctx
    
    # -- GO

    go[e.ast] = glob[e.ast, {'glob', {},  'funcs', {}}]

def main():
    argsp = argparse.ArgumentParser(
        description="FunC Interpreter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  refunpy contract.func -a\n  refunpy contract.func --fmt-on"
    )
    argsp.add_argument(
        "filename",
        nargs="?",
        help="FunC source code filename"
    )
    argsp.add_argument(
        "-a", "--ast",
        action="store_true",
        help="enable AST output to STDOUT"
    )
    argsp.add_argument(
        "-e", "--env",
        action="store_true",
        help="enable ENV output to STDOUT"
    )
    argsp.add_argument(
        "-d", "--doc",
        action="store_true",
        help="enable FMT output to FMT DIR"
    )
    
    args = argsp.parse_args()
    
    if args.doc and not args.filename:
        with open("./docs/FunC.spec.ref", encoding="utf-8", mode="w") as f:
            print("-- DOC: The documentation have been written to a file: ./docs/FunC.spec.ref")
            f.write(fmt(refun))
        return
    
    if not args.filename:
        argsp.error("Filename is required unless using --doc alone")
        
    ast = main_ast(args.filename)

    if args.ast:
        print("-- AST:", ast, "\n")
    
    interp_res = refun('go', ast)
    
    if args.env:
        print("-- RES: ", interp_res)
        
    if args.doc:
        with open("./docs/FunC.spec.ref", encoding="utf-8", mode="w") as f:
            print("-- DOC: The documentation have been written to a file: ./docs/FunC.spec.ref")
            f.write(fmt(refun))
      
if __name__ == "__main__":  
    main()