import sys
import json
import argparse

from parser import get_ast
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


    
    'typeof': lambda arg: ('int',) if isinstance(arg[0], int) else ('slice',) if\
        isinstance(arg[0], str) and arg[0].startswith('"') and arg[0].endswith('"')\
            else ('var',) if isinstance(arg[0], str) else type(arg[0]).__name__,
            
    'prout': lambda arg: (print("-- STDOUT:", arg, "\n"), ())[~0],
    'pexit': lambda arg: (print("-- STDOUT:", arg, "\n"), sys.exit(0), ())[~0],
}

@refal(imports)
def refun():
    
    p[e.x] = prout[e.x]
    pp[e.x] = pexit[e.x]
    
    unpack[{s.v}] = s.v
    unpack[{{s.v}}] = s.v
    unpack[e.e] = e.e
    
    join[{e.l}, {e.r}] = {e.l, e.r}
    
    mkfargs[{{s.ty, s.var}, e.otha}, {t.val, e.othv}, t.octx, t.ctx] =\
        mkfargs[{e.otha}, {e.othv}, t.octx, put[t.ctx, s.var, expr[t.val, t.octx, {}]]]
        
    mkfargs[{}, {}, t.octx, t.ctx] = t.ctx
    
    get[{'glob', t.g, 'funcs', {e.e, t.l}}, s.key] =\
        get[join[t.g, t.l], s.key]
        
    get[{e.x, {s.key, t.val}, e.y}, s.key] = t.val
    
    putg[{'glob', {e.g}, 'funcs', t.f}, s.key, t.new] =\
        {'glob', {e.g, {s.key, t.new}}, 'funcs', t.f}
    
    put[{'glob', t.g, 'funcs', {e.e, {e.x, {s.key, t.val}, e.y}}}, s.key, t.new] =\
        {'glob', t.g, 'funcs', {e.e, {e.x, {s.key, t.new}, e.y}}}

    put[{'glob', t.g, 'funcs', {e.e, {e.l}}}, s.key, t.new] =\
        {'glob', t.g, 'funcs', {e.e, {e.l, {s.key, t.new}}}}

    mkcomv[{{e.ty, s.var}, e.oth}, {{'fcall', e.fc}, e.oexp}, t.ctx, t.fns] =\
        mkcomv[{{e.ty, s.var}, e.oth}, join[expr[{'fcall', e.fc}, t.ctx, t.fns], {e.oexp}], t.ctx, t.fns]

    mkcomv[{{e.ty, s.var}, e.oth}, {t.cexp, e.oexp}, t.ctx, t.fns] =\
        mkcomv[{e.oth}, {e.oexp}, put[t.ctx, s.var, expr[t.cexp, t.ctx, t.fns]], t.fns]
    
    mkcomv[{}, {}, t.ctx, t.fns] = t.ctx
    
    mkrvls[{t.ret, e.oret}, t.ctx, t.fns, {e.buf}] =\
        mkrvls[{e.oret}, t.ctx, t.fns, {e.buf, {expr[t.ret, t.ctx, t.fns]}}]
    mkrvls[{}, t.ctx, t.fns, t.buf] = put[t.ctx, '@rets', t.buf]
    
    literal['int', s.v, t.ctx] = s.v
    literal['slice', s.v, t.ctx] = s.v
    literal['var', s.v, t.ctx] = get[t.ctx, s.v]
    
    expr[{'fcall', s.fnm, {e.args}}, {e.g, 'funcs', {e.f}}, {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}] =\
        unpack[get[interp[t.b, {e.e1, {'func', {s.fnm, t.s, t.a, t.r}, t.b}, e.e2}, 
            mkfargs[t.a, {e.args}, {e.g, 'funcs', {e.f}}, {e.g, 'funcs', {e.f, {}}}]], '@rets']]

    expr[{'+', t.e1, t.e2}, t.ctx, t.fns] = add[expr[t.e1, t.ctx, t.fns], expr[t.e2, t.ctx, t.fns]]
    expr[{'-', t.e1, t.e2}, t.ctx, t.fns] = sub[expr[t.e1, t.ctx, t.fns], expr[t.e2, t.ctx, t.fns]]
    expr[{'*', t.e1, t.e2}, t.ctx, t.fns] = mul[expr[t.e1, t.ctx, t.fns], expr[t.e2, t.ctx, t.fns]]
    expr[{'/', t.e1, t.e2}, t.ctx, t.fns] = div[expr[t.e1, t.ctx, t.fns], expr[t.e2, t.ctx, t.fns]]
    expr[{s.v}, t.ctx, t.fns] = literal[typeof[s.v], s.v, t.ctx]
 
    stmt[{'const', s.var, t.expr}, t.ctx, t.fns] =\
        putg[t.ctx, s.var, expr[t.expr, t.ctx, t.fns]]
    
    stmt[{'bind', t.vars, t.expr}, t.ctx, t.fns] =\
        mkcomv[t.vars, t.expr, t.ctx, t.fns]
        
    stmt[{'assign', t.vars, t.expr}, t.ctx, t.fns] =\
        mkcomv[t.vars, t.expr, t.ctx, t.fns]
    
    stmt[{'return', {}}, t.ctx, t.fns] = t.ctx
    stmt[{'return', t.rets}, t.ctx, t.fns] =\
        mkrvls[t.rets, t.ctx, t.fns, {}]
        
    # stmt[{'fcall', s.fnm, {e.args}}, e.oth] = pp[{'fcall', s.fnm, {e.args}}]#resolve_args[e.args], {'fcall', s.fnm}, stat[e.oth]
    
    glob[e.h, {'const', s.var, t.expr}, e.oth, t.ctx] =\
        glob[e.h, e.oth, stmt[{'const', s.var, t.expr}, t.ctx, {}]]  
          
    glob[e.h, {'func', {'main', e.o}, e.mb}, e.t, {e.g, 'funcs', {e.f}}] =\
        interp[e.mb, {e.h}, {e.g, 'funcs', {e.f, {}}}]

    interp[{t.stmt, e.block}, t.fns, t.ctx] =\
        interp[{e.block}, t.fns, stmt[t.stmt, t.ctx, t.fns]]
        
    interp[{}, t.fns, t.ctx] = t.ctx
    
    start[e.ast] = glob[e.ast, {'glob', {},  'funcs', {}}]

    
def main():
    ast = get_ast("contrs/funcs2.func")
    print("-- AST: ", ast, "\n")

    interp_res = refun('start', ast)
    print("-- RES: ", interp_res)
      
if __name__ == "__main__":  
    main()