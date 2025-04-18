import sys
import json
import argparse

from parser import get_ast
from libs.refalpy.refalpy import refal


imports = {
    'eq': lambda arg: (arg[0] == arg[1],),
    'grt': lambda arg: (arg[0] > arg[1],),
    'less': lambda arg: (arg[0] < arg[1],),
    'lesseq': lambda arg: (arg[0] <= arg[1],),
    'grteq': lambda arg: (arg[0] >= arg[1],),
    'add': lambda arg: (arg[0] + arg[1],),
    'sub': lambda arg: (arg[0] - arg[1],),
    'mul': lambda arg: (arg[0] * arg[1],),
    'div': lambda arg: (arg[0] // arg[1],),
    'type': lambda arg: (type(arg[0]).__name__,),
    'joinfvar': lambda arg: (f"@{arg[0]}@{arg[1]}", ),
    'cond': lambda arg: (arg[1], ) if arg[0] else (arg[2], ),
    
    'expand': lambda arg: arg[0] * int(arg[1][0]),
    
    'prout': lambda arg: (print("-- STDOUT:", arg, "\n"), ())[~0],
    'pexit': lambda arg: (print("-- STDOUT:", arg, "\n"), sys.exit(0), ())[~0],
}

@refal(imports)
def refun():
    
    # p[e.x] = prout[e.x]
    # pp[e.x] = pexit[e.x]
    
    cmd['int'] = 'push'
    cmd['str'] = 'load'
    
    join[s.x, s.y] = joinfvar[s.x, s.y]
    join[{e.l}, {e.r}] = {e.l, e.r}
    
    unpack[{e.x}] = e.x
    
    get[{e.x, {s.key, t.val}, e.y}, s.key] = t.val
    
    get_fbody[{e.p, {s.fnm, {e.body}}, e.n}, s.fnm] = e.body
    
    glob[{'func', {s.fnm, {e.specs}, {e.args}, {e.ret}}, {e.body}}, e.oth] = {s.fnm, join[{make_tvars[e.args]}, {stat[e.body]}]}, glob[e.oth]
    glob = _
    
    set[{e.x, {s.key, t.val}, e.y}, s.key, t.new] = {e.x, {s.key, t.new}, e.y}
    set[{e.x}, s.key, t.val] = {e.x, {s.key, t.val}}
    
    exprs[t.expr, e.oth] = expr[t.expr], exprs[e.oth]
    exprs = _
    
    make_tvars[{s.ty, s.var}, e.oth] = make_tvars[e.oth], {'store', s.var}
    make_tvars[s.ty, s.var] = {'store', s.var}
    make_tvars = _
    
    resolve_args[s.arg, e.oth] = expr[s.arg], resolve_args[e.oth]
    resolve_args[t.arg, e.oth] = expr[t.arg], resolve_args[e.oth]
    resolve_args[{{s.fnm, s.infnm, {e.inargs}}}, e.oth] = resolve_args[e.inargs], {'fcall', s.infnm}, resolve_args[e.oth]
    resolve_args = _
    
    resolve_chain_call[{{'fcall', s.fnm1, {e.args1}}, {'fcall', s.fnm2, {e.args2}}, e.oth}] = resolve_chain_call[{{'fcall', s.fnm2, {{{'fcall', s.fnm1, {e.args1}}}, e.args2}}, e.oth}]
    resolve_chain_call[{{'fcall', s.fnm1, {e.args1}}, {'fcall', s.fnm2, {e.args2}}}] = {{'fcall', s.fnm2, {{{'fcall', s.fnm1, {e.args1}}}, e.args2}}}
    resolve_chain_call[e.f] = e.f
    
    doloop[s.ctxf, {{t.cond, t.body, t.oth}, {e.stack, s.bl}, t.env, t.fs}, t.body] = cond[s.bl, {steps[{s.ctxf, t.body, {e.stack}, t.env, t.fs}, {t.cond, t.body, t.oth}]}, {{e.stack}, t.env, t.fs}]
    
    steps[{s.ctxf, {t.cmd, e.tail}, e.oth}, {t.cond, t.body, t.oth}] = steps[{s.ctxf, step[s.ctxf, t.cmd, {e.tail}, e.oth]}, {t.cond, t.body, t.oth}]
    steps[{s.ctxf, {}, e.csef}, {t.cond, t.body, t.oth}] = {t.cond, t.body, t.oth}, e.csef
    
    stat[{'bind', {e.vars}, t.expr}, e.oth] = expr[t.expr], make_tvars[e.vars], stat[e.oth]
    stat[{'assign', s.var, t.expr}, e.oth] = expr[t.expr], {'store', s.var}, stat[e.oth]
    stat[{'fcall', s.fnm, {e.args}}, e.oth] = resolve_args[e.args], {'fcall', s.fnm}, stat[e.oth]
    stat[{'if', t.cond, t.do, {}}, e.oth] = expr[t.cond], 'cond', {{stat[t.do]}, {}}, stat[e.oth]
    stat[{'if', t.cond, t.do, t.alt}, e.oth] = expr[t.cond], 'cond', {{stat[t.do]}, {stat[t.alt]}}, stat[e.oth]
    stat[{'while', t.cond, {e.body}}, e.oth] = 'condrep', {expr[t.cond]}, {stat[e.body]}, {stat[e.oth]}
    stat[{'repeat', s.ti, {e.body}}, e.oth] = expr[s.ti], 'rep', {stat[e.body]}, stat[e.oth]
    stat[{'return', {e.rets}}] = exprs[e.rets], 'ret'
    stat = _

    expr[{{'fcall', s.fnm, {e.args}}}] = resolve_args[e.args], {'fcall', s.fnm}
    expr[{{'fcall', s.fnm, {e.args}}, e.oth}] = expr[resolve_chain_call[{{'fcall', s.fnm, {e.args}}, e.oth}]]
    expr[{'+', t.a, t.b}] = expr[t.a], expr[t.b], 'add'
    expr[{'-', t.a, t.b}] = expr[t.a], expr[t.b], 'sub'
    expr[{'*', t.a, t.b}] = expr[t.a], expr[t.b], 'mul'
    expr[{'/', t.a, t.b}] = expr[t.a], expr[t.b], 'div'
    expr[{'==', t.a, t.b}] = expr[t.a], expr[t.b], 'eq'
    expr[{'>', t.a, t.b}] = expr[t.a], expr[t.b], 'grt'
    expr[{'<', t.a, t.b}] = expr[t.a], expr[t.b], 'less'
    expr[{'<=', t.a, t.b}] = expr[t.a], expr[t.b], 'lesseq'
    expr[{'>=', t.a, t.b}] = expr[t.a], expr[t.b], 'grteq'
    expr[s.val] = {cmd[type[s.val]], s.val}
    expr[{e.exprs}] = exprs[e.exprs]

    interp[{{s.ctxf, e.body}, e.oth}, t.flst] = interp[s.ctxf, e.body, {}, {}, t.flst]
    interp[s.ctxf, {t.cmd, e.code}, t.stack, t.env, t.flst] = interp[s.ctxf, step[s.ctxf, t.cmd, {e.code}, t.stack, t.env, t.flst]]
    interp[s.ctxf, {}, {}, t.env, t.flst] = t.env
    interp[s.ctxf, {}, t.stack, t.env, t.flst] = t.stack, t.env
      
    step[s.ctxf, {'fcall', s.fnm}, t.c, t.stack, t.env, t.flst] = t.c, interp[s.fnm, {get_fbody[t.flst, s.fnm]}, t.stack, t.env, t.flst], t.flst
    step[s.ctxf, 'ret', t.c, t.stack, e.ef] = t.c, t.stack, e.ef
    step[s.ctxf, 'add', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, add[s.x, s.y]}, e.ef
    step[s.ctxf, 'sub', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, sub[s.x, s.y]}, e.ef
    step[s.ctxf, 'mul', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, mul[s.x, s.y]}, e.ef
    step[s.ctxf, 'div', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, div[s.x, s.y]}, e.ef
    step[s.ctxf, 'eq', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, eq[s.x, s.y]}, e.ef
    step[s.ctxf, 'grt', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, grt[s.x, s.y]}, e.ef
    step[s.ctxf, 'less', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, less[s.x, s.y]}, e.ef
    step[s.ctxf, 'lesseq', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, lesseq[s.x, s.y]}, e.ef
    step[s.ctxf, 'grteq', t.c, {e.stack, s.x, s.y}, e.ef] = t.c, {e.stack, grteq[s.x, s.y]}, e.ef
    step[s.ctxf, 'cond',  {{e.c}, e.othc}, {e.stack, s.bl}, e.ef] =  join[cond[s.bl, e.c], {e.othc}], {e.stack}, e.ef
    step[s.ctxf, 'rep',  {{e.c}, e.othc}, {e.stack, s.x}, e.ef] = {expand[{e.c}, {s.x}], e.othc}, {e.stack}, e.ef
    step[s.ctxf, 'condrep', {}, t.env, t.fs, t.oth] =  t.oth, {}, t.env, t.fs
    step[s.ctxf, 'condrep', {t.cond, t.body, t.oth}, t.stack, t.env, t.fs, e.oth] = step[s.ctxf, 'condrep', unpack[doloop[s.ctxf, {steps[{s.ctxf, t.cond, t.stack, t.env, t.fs}, {t.cond, t.body, t.oth}]}, t.body]], t.oth]
    step[s.ctxf, {'push', s.x}, t.c, {e.stack}, e.ef] = t.c, {e.stack, s.x}, e.ef
    step[s.ctxf, {'load', s.var}, t.c, {e.stack}, t.env, t.flst] = t.c, {e.stack, get[t.env, join[s.ctxf, s.var]]}, t.env, t.flst
    step[s.ctxf, {'store', s.var}, t.c, {e.stack, s.val}, t.env, t.flst] = t.c, {e.stack}, set[t.env, join[s.ctxf, s.var], s.val], t.flst
    
    main[e.ast] = interp[{glob[e.ast]}, {glob[e.ast]}]
    

def make_dict(envi: tuple) -> dict:
    envi_dict = {}
    for (key, value) in envi[0]:
        parts = key.split('@')
        func_name, var_name = parts[1], parts[2]
        if func_name not in envi_dict:
            envi_dict[func_name] = {}
        envi_dict[func_name][var_name] = value
    return envi_dict

def main():
    argsp = argparse.ArgumentParser(description="FunC Interpreter")
    argsp.add_argument("filename", help="FunC source code filename")
    argsp.add_argument("--ast-on", action="store_true", help="Enable AST output")
    
    args = argsp.parse_args()

    ast = get_ast(args.filename)
    
    if args.ast_on:
        print("-- AST:", ast, "\n")
    
    interp_res = refun('main', ast)
    envi_dict = make_dict(interp_res)
    print("-- RES: ", json.dumps(envi_dict, indent=4))
      
if __name__ == "__main__":  
    main()

