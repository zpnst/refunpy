import sys
import json
import argparse

from refmt import fmt

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
    
    # 'prout': lambda arg: (eval(f"print({arg[0]}, end='')"), ())[~0],
    'prout': lambda args: (print(args, "\n"), ())[~0],
}

@refal(imports)
def refun():
    
    p[e.e] = prout[e.e]
    
    # -- UNPACK
    
    unpack[s.s] = s.s
    unpack[{t.e1, t.e2, e.e}] = {t.e1, t.e2, e.e}
    unpack[{e.e}] = unpack[e.e]
    
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

    mkcomv[{{e.ty, s.var}, e.oth}, {{{'fcall', e.fc}}, e.oexp}, e.state] =\
        mkcomv[{{e.ty, s.var}, e.oth}, join[expr[{{'fcall', e.fc}}, e.state], {e.oexp}], e.state]

    mkcomv[{{e.ty, s.var}, e.oth}, {t.cexp, e.oexp}, t.ctx, t.fns] =\
       mkcomv[{e.oth}, {e.oexp}, put[t.ctx, s.var, expr[t.cexp, t.ctx, t.fns]], t.fns]
    
    mkcomv[{}, {}, t.ctx, t.fns] = t.ctx
    
    # -- MKRVLS

    mkrvls[{t.ret, e.oret}, e.state, {e.buf}] =\
        mkrvls[{e.oret}, e.state, {e.buf, {expr[t.ret, e.state]}}]
    mkrvls[{}, t.ctx, t.fns, t.buf] = put[t.ctx, '@rets', t.buf]
    
    # -- LITERAL

    literal['int', s.v, t.ctx] = s.v
    literal['slice', s.v, t.ctx] = s.v
    literal['var', s.v, t.ctx] = get[t.ctx, s.v]
    
    # -- EXPR
    
    expr[{{'fcall', s.fnm, {e.args}}}, {e.g, 'funcs', {e.f}}, 
        {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}] =\
        unpack[get[interp[t.b, mkfargs[t.a, {e.args}, {e.g, 'funcs', {e.f}}, {e.g, 'funcs', {e.f, {}}},
            {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}], 
                   {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}], '@rets']]

    expr[{{'fcall', s.fnm, {e.args}}, e.oth}, {e.g, 'funcs', {e.f}}, 
        {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}] =\
            unpack[expr[resolve_chain_call[{{'fcall', s.fnm, {e.args}}, e.oth}], 
                 {e.g, 'funcs', {e.f}}, {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}]]

    expr[{'+', t.e1, t.e2}, e.state] = add[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'-', t.e1, t.e2}, e.state] = sub[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'*', t.e1, t.e2}, e.state] = mul[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'/', t.e1, t.e2}, e.state] = div[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    
    expr[{'==', t.e1, t.e2}, e.state] = eq[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'!=', t.e1, t.e2}, e.state] = neq[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'>', t.e1, t.e2}, e.state] = grt[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'<', t.e1, t.e2}, e.state] = less[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'<=', t.e1, t.e2}, e.state] = lesseq[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'>=', t.e1, t.e2}, e.state] = grteq[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'|', t.e1, t.e2}, e.state] = _or[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    expr[{'&', t.e1, t.e2}, e.state] = _and[
        expr[t.e1, e.state], expr[t.e2, e.state]]
    
    expr[{s.v}, t.ctx, t.fns] = literal[
        typeof[s.v], s.v, t.ctx]
 
    # -- BUILTIN

    builtin['STRDUMP', {{'slice', s.var}}, t.ctx] =\
        t.ctx, prout[get[t.ctx, s.var]]
        
    builtin['s0 DUMP', {{'int', s.var}}, t.ctx] =\
        t.ctx, prout[get[t.ctx, s.var]]
    
    # -- WHILE_STMT
    
    while_stmt[False, t._, t.ctx, t.fns] = t.ctx
    while_stmt[s._, {t.e, {e.block}}, e.state] =\
        interp[{e.block, {'while', t.e, {e.block}}}, e.state]

    # -- STMT
    
    stmt[{'include', s.path}, e.state] =\
        mkast[s.path]
    
    stmt[{'const', s.var, t.expr}, t.ctx, t.fns] =\
        putg[t.ctx, s.var, expr[t.expr, t.ctx, t.fns]]
    
    stmt[{'bind', t.vars, t.expr}, e.state] =\
        mkcomv[t.vars, t.expr, e.state]
        
    stmt[{'assign', t.vars, t.expr}, e.state] =\
        mkcomv[t.vars, t.expr, e.state]
    
    stmt[{'if', t.cond, t.do, {}}, t.ctx, t.fns] =\
        interp[cond[expr[t.cond, t.ctx, t.fns], {{t.do}, t.ctx, t.fns}, {t.ctx}]]
    
    stmt[{'if', t.cond, t.do, t.alt}, e.state] =\
        interp[cond[expr[t.cond, e.state], 
             {{t.do}, e.state}, {{t.alt}, e.state}]]

    stmt[{'repeat', t.expr, {e.body}}, e.state] =\
        interp[expand[{e.body}, {expr[t.expr, e.state]}], e.state]
        
    stmt[{'while', t.e, t.block}, e.state] =\
        while_stmt[expr[t.e, e.state], {t.e, t.block}, e.state]
    
    stmt[{'return', {}}, t.ctx, t.fns] = t.ctx
    stmt[{'return', t.rets}, e.state] =\
        mkrvls[t.rets, e.state, {}]
    
    stmt[{'fcall', s.fnm, {e.args}}, t.ctx, t.fns] =\
        first[t.ctx, expr[{{'fcall', s.fnm, {e.args}}}, t.ctx, t.fns]]

    stmt[{'intrinsic', t.args, s.instr}, t.ctx, t.fns] =\
        builtin[s.instr, t.args, t.ctx]
    
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
    argsp = argparse.ArgumentParser(description="FunC Interpreter")
    argsp.add_argument("filename", help="FunC source code filename")
    argsp.add_argument("--ast-on", action="store_true", help="Enable AST output to STDOUT")
    argsp.add_argument("--env-on", action="store_true", help="Enable ENV output to STDOUT")
    argsp.add_argument("--fmt-on", action="store_true", help="Enable FMT output to FMT DIR")
    
    args = argsp.parse_args()

    ast = main_ast(args.filename)

    if args.ast_on:
        print("-- AST:", ast, "\n")
    
    interp_res = refun('go', ast)
    
    if args.env_on:
        print("-- RES: ", interp_res)
        
    if args.fmt_on:
        with open("./fmt/interp.ref", encoding="utf-8", mode="a") as f:
            print("-- FMT: The rules have been written to a file: ./fmt/interp.ref")
            f.write(fmt(refun))
      
if __name__ == "__main__":  
    main()