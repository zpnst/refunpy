import sys
import json
import argparse

from parser import main_ast, lib_ast
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
    
    'prout': lambda arg: (eval(f"print({arg[0]}, end='')"), ())[~0],
}

@refal(imports)
def refun():
    
    # -- U
    
    u[s.s] = s.s
    u[{e.e}] = u[e.e]
    
    # -- FIRST
     
    first[t.a, t.b] = t.a
    
    # -- JOIN
    
    join[{e.l}, {e.r}] = {e.l, e.r}
    
    # -- MKFARGS

    mkfargs[{{s.ty, s.var}, e.otha}, {t.val, e.othv}, t.octx, t.ctx, t.fns] =\
        mkfargs[{e.otha}, {e.othv}, t.octx, put[t.ctx, s.var, expr[t.val, t.octx, t.fns]], t.fns]
        
    mkfargs[{}, {}, t.octx, t.ctx, t.fns] = t.ctx
    
    # -- GET

    get[{'glob', t.g, 'funcs', {e.e, t.l}}, s.key] =\
        get[join[t.g, t.l], s.key]
        
    get[{e.x, {s.key, t.val}, e.y}, s.key] = t.val
    get[e.e, '@rets'] = {}
    
    # -- PUTG
    
    putg[{'glob', {e.g}, 'funcs', t.f}, s.key, t.new] =\
        {'glob', {e.g, {s.key, t.new}}, 'funcs', t.f}
    
    # -- PUT

    put[{'glob', t.g, 'funcs', {e.e, {e.x, {s.key, t.val}, e.y}}}, s.key, t.new] =\
        {'glob', t.g, 'funcs', {e.e, {e.x, {s.key, t.new}, e.y}}}

    put[{'glob', t.g, 'funcs', {e.e, {e.l}}}, s.key, t.new] =\
        {'glob', t.g, 'funcs', {e.e, {e.l, {s.key, t.new}}}}

    # -- RESOLVE_CHAIN_CALL

    resolve_chain_call[{{'fcall', s.fnm1, {e.args1}}, {'fcall', s.fnm2, {e.args2}}, e.oth}] =\
        resolve_chain_call[{{'fcall', s.fnm2, {{{'fcall', s.fnm1, {e.args1}}}, e.args2}}, e.oth}]
        
    resolve_chain_call[{{'fcall', s.fnm1, {e.args1}}, {'fcall', s.fnm2, {e.args2}}}] =\
        {{'fcall', s.fnm2, {{{'fcall', s.fnm1, {e.args1}}}, e.args2}}}
        
    resolve_chain_call[e.f] = e.f

    # -- MKCOMV

    mkcomv[{{e.ty, s.var}, e.oth}, {{{'fcall', e.fc}}, e.oexp}, t.ctx, t.fns] =\
        mkcomv[{{e.ty, s.var}, e.oth}, join[expr[{{'fcall', e.fc}}, t.ctx, t.fns], {e.oexp}], t.ctx, t.fns]

    mkcomv[{{e.ty, s.var}, e.oth}, {t.cexp, e.oexp}, t.ctx, t.fns] =\
        mkcomv[{e.oth}, {e.oexp}, put[t.ctx, s.var, expr[t.cexp, t.ctx, t.fns]], t.fns]
    
    mkcomv[{}, {}, t.ctx, t.fns] = t.ctx
    
    # -- MKRVLS

    mkrvls[{t.ret, e.oret}, t.ctx, t.fns, {e.buf}] =\
        mkrvls[{e.oret}, t.ctx, t.fns, {e.buf, {expr[t.ret, t.ctx, t.fns]}}]
    mkrvls[{}, t.ctx, t.fns, t.buf] = put[t.ctx, '@rets', t.buf]
    
    # -- LITERAL

    literal['int', s.v, t.ctx] = s.v
    literal['slice', s.v, t.ctx] = s.v
    literal['var', s.v, t.ctx] = get[t.ctx, s.v]
    
    # -- EXPR
    
    expr[{{'fcall', s.fnm, {e.args}}}, {e.g, 'funcs', {e.f}}, 
        {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}] =\
        get[interp[t.b, {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}, 
            mkfargs[t.a, {e.args}, {e.g, 'funcs', {e.f}}, {e.g, 'funcs', {e.f, {}}},
                    {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}]], '@rets']

    expr[{{'fcall', s.fnm, {e.args}}, e.oth}, {e.g, 'funcs', {e.f}}, 
        {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}] =\
            u[expr[resolve_chain_call[{{'fcall', s.fnm, {e.args}}, e.oth}], 
                 {e.g, 'funcs', {e.f}}, {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}]]

    expr[{'+', t.e1, t.e2}, t.ctx, t.fns] = add[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'-', t.e1, t.e2}, t.ctx, t.fns] = sub[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'*', t.e1, t.e2}, t.ctx, t.fns] = mul[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'/', t.e1, t.e2}, t.ctx, t.fns] = div[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    
    expr[{'==', t.e1, t.e2}, t.ctx, t.fns] = eq[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'!=', t.e1, t.e2}, t.ctx, t.fns] = neq[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'>', t.e1, t.e2}, t.ctx, t.fns] = grt[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'<', t.e1, t.e2}, t.ctx, t.fns] = less[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'<=', t.e1, t.e2}, t.ctx, t.fns] = lesseq[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'>=', t.e1, t.e2}, t.ctx, t.fns] = grteq[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'|', t.e1, t.e2}, t.ctx, t.fns] = _or[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    expr[{'&', t.e1, t.e2}, t.ctx, t.fns] = _and[
        u[expr[t.e1, t.ctx, t.fns]], u[expr[t.e2, t.ctx, t.fns]]]
    
    expr[{s.v}, t.ctx, t.fns] = literal[
        typeof[s.v], s.v, t.ctx]
 
    # -- INTRINSICS

    intrinsics['STRDUMP', {{'slice', s.var}}, t.ctx] =\
        t.ctx, prout[get[t.ctx, s.var]]
        
    intrinsics['s0 DUMP', {{'int', s.var}}, t.ctx] =\
        t.ctx, prout[get[t.ctx, s.var]]
    
    # -- WHILE_STMT
    
    while_stmt[False, t._, t.ctx, t.fns] = t.ctx
    while_stmt[s._, {t.e, {e.block}}, t.ctx, t.fns] =\
        interp[{e.block, {'while', t.e, {e.block}}}, t.fns, t.ctx]

    # -- STMT
    
    stmt[{'include', s.path}, t.ctx, t.fns] =\
        mkast[s.path]
    
    stmt[{'const', s.var, t.expr}, t.ctx, t.fns] =\
        putg[t.ctx, s.var, expr[t.expr, t.ctx, t.fns]]
    
    stmt[{'bind', t.vars, t.expr}, t.ctx, t.fns] =\
        mkcomv[t.vars, t.expr, t.ctx, t.fns]
        
    stmt[{'assign', t.vars, t.expr}, t.ctx, t.fns] =\
        mkcomv[t.vars, t.expr, t.ctx, t.fns]
    
    stmt[{'if', t.cond, t.do, {}}, t.ctx, t.fns] =\
        interp[cond[expr[t.cond, t.ctx, t.fns], {{t.do}, t.fns, t.ctx}, {t.ctx}]]
    
    stmt[{'if', t.cond, t.do, t.alt}, t.ctx, t.fns] =\
        interp[cond[expr[t.cond, t.ctx, t.fns], 
             {{t.do}, t.fns, t.ctx}, {{t.alt}, t.fns, t.ctx}]]

    stmt[{'repeat', t.expr, {e.body}}, t.ctx, t.fns] =\
        interp[expand[{e.body}, {expr[t.expr, t.ctx, t.fns]}], t.fns, t.ctx]
        
    stmt[{'while', t.e, t.block}, t.ctx, t.fns] =\
        while_stmt[expr[t.e, t.ctx, t.fns], {t.e, t.block}, t.ctx, t.fns]
    
    stmt[{'return', {}}, t.ctx, t.fns] = t.ctx
    stmt[{'return', t.rets}, t.ctx, t.fns] =\
        mkrvls[t.rets, t.ctx, t.fns, {}]
    
    stmt[{'fcall', s.fnm, {e.args}}, t.ctx, t.fns] =\
        first[t.ctx, expr[{{'fcall', s.fnm, {e.args}}}, t.ctx, t.fns]]

    stmt[{'intrinsic', t.args, s.instr}, t.ctx, t.fns] =\
        intrinsics[s.instr, t.args, t.ctx]
    
    # -- GLOB
    
    glob[e.h, {'const', s.var, t.expr}, e.oth, t.ctx] =\
        glob[e.h, e.oth, stmt[{'const', s.var, t.expr}, t.ctx, {}]]  
        
    glob[e.h, {'include', s.path}, e.oth, t.ctx] =\
        glob[e.h, stmt[{'include', s.path}, t.ctx, {}], e.oth, t.ctx] 
          
    glob[e.h, {'func', {'main', e.o}, e.mb}, e.t, {e.g, 'funcs', {e.f}}] =\
        interp[e.mb, {e.h}, {e.g, 'funcs', {e.f, {}}}]

    # -- INTERP
    
    interp[{t.stmt, e.block}, t.fns, t.ctx] =\
        interp[{e.block}, t.fns, stmt[t.stmt, t.ctx, t.fns]]
        
    interp[{}, t.fns, t.ctx] = t.ctx
    interp[t.ctx] = t.ctx
    
    # -- GO

    go[e.ast] = glob[e.ast, {'glob', {},  'funcs', {}}]

def main():
    argsp = argparse.ArgumentParser(description="FunC Interpreter")
    argsp.add_argument("filename", help="FunC source code filename")
    argsp.add_argument("--ast-on", action="store_true", help="Enable AST output")
    argsp.add_argument("--env-on", action="store_true", help="Enable ENV output")
    
    args = argsp.parse_args()

    ast = main_ast(args.filename)

    if args.ast_on:
        print("-- AST:", ast, "\n")
    
    interp_res = refun('go', ast)
    
    if args.env_on:
        print("-- RES: ", interp_res)
      
if __name__ == "__main__":  
    main()