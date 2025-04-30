from libs.peco.peco import *

ws = eat(r'\s*')
token = lambda f: memo(seq(ws, f))
tok = lambda c: token(push(eat(c)))
skip = lambda c: token(eat(c))
skopt = lambda c: opt(skip(c))

mkvar = to(lambda x: x)
mkstr = to(lambda s: s)
mkwrp = to(lambda w: (w,))
mknum = to(lambda x: int(x))
mkbop = to(lambda a, o, b: (o, a, b))
mkbind = to(lambda t, v, e: ('bind', ((t, v),), (e,)))
mkbbind = to(lambda b, e: ('bind', b, e))
mkassign = to(lambda v, e: ('assign', v, e))
mksassign = to(lambda v, s, e: ('assign', ((v,),), ((s, (v,), e),)))

mkloop = to(lambda lname, cond, body: (lname, cond, body))
mkdoloop = to(lambda body, cond: ('dountil', cond, body))

mkifcond = to(lambda cond, body, ob: ('if', cond, body, ob))
mksifcond = to(lambda cond, body: ('if', cond, body, ()))
mkecond = to(lambda _, body: (body))

mkret = to(lambda ret: ('return', ret))
mkcall = to(lambda fn, args: ('fcall', fn, args))
mkchcall = to(lambda fns: ('chain_call', fns))
mkfooargs = to(lambda x, y: (x, y))

mkconst = to(lambda v, e: ('const', v, e))

mkfoo = to(lambda ret, name, args, specs, body: ('func',
    (name, specs, args, ret), body))

mkasm = to(lambda ret, name, args, specs, instr: ('func',
    (name, specs, args, ret), (('intrinsic', args, instr),)))

mkinc = to(lambda path: ('include', path))

mkstrdump = to(lambda string: ('strdump', string))

var = seq(tok(r'[a-zA-Z][a-zA-Z0-9_]*'), mkvar)
fnm = seq(tok(r'[a-zA-Z0-9_~]+'), mkvar)
asmins = seq(tok(r'[a-zA-Z0-9 ]+'), mkvar)
path = seq(tok(r'[a-zA-Z0-9_/.]+'), mkvar)
num = seq(tok(r'-?\d+'), mknum)
string = seq(tok(r'\"[a-zA-Z0-9!, \\#]*\"'), mkstr)

typ = alt(
    tok(r'int'),
    tok(r'slice'),
    tok(r'cell'),
    tok(r'builder'),
)

specs = alt(
    tok(r'impure'),
    tok(r'inline'),
    tok(r'inline_ref'),
    seq(tok(r'impure'), tok(r'inline')),
    seq(tok(r'impure'), tok(r'inline_ref')),
)

expr = lambda s: expr(s)
term = lambda s: term(s)
stmt = lambda s: stmt(s)

cond_expr = lambda s: cond_expr(s)

block = group(many(stmt))
fcall = seq(fnm, skip(r'\('), group(many(seq(expr, skopt(r',')))), skip(r'\)'), mkcall)

fdec = seq(
        skopt(r'\('), group(many(seq(typ, skopt(r',')))), skopt(r'\)'), fnm,
        skip(r'\('), group(many(seq(typ, var, skopt(r','), mkfooargs))), 
        skip(r'\)'), group(many(seq(specs, ws))), skip(r'{'), block, skip(r'}'), mkfoo)

asmdec = seq(
            skopt(r'\('), group(many(seq(typ, skopt(r',')))), 
            skopt(r'\)'), fnm, skip(r'\('), group(many(seq(typ, var, skopt(r','), mkfooargs))),
            skip(r'\)'), group(many(seq(specs, ws))), skip(r'asm'), skip(r'"'), asmins, skip(r'"'), 
            skip(r';'), mkasm)

glob = alt(
    fdec,
    asmdec,
    seq(skip(r'const'), var, skip(r'='), expr, skip(r';'), mkconst),
    seq(skip(r'#'), skip(r'include'), skip(r'"'), path, skip(r'"'), skip(r';'), mkinc)  
)

main = group(many(glob))

atoms = alt(
    seq(var, mkwrp),
    seq(num, mkwrp),
)

factor = alt(
    group(list_of(fcall, skopt(r'\.'))),
    seq(var, mkwrp),
    seq(num, mkwrp),
    seq(string, mkwrp),
    seq(skip(r'\('), expr, skip(r'\)'))
)

term = left(alt(
    seq(term, tok(r'&|\|'), factor, mkbop),
    seq(term, tok(r'[!=]='), factor, mkbop),
    seq(term, tok(r'[><]'), factor, mkbop),
    seq(term, tok(r'[><]='), factor, mkbop),
    seq(term, tok(r'\*'), factor, mkbop),
    seq(term, tok(r'/'), factor, mkbop),
    factor,
))

expr = left(alt(
    seq(expr, tok(r'\+'), term, mkbop),
    seq(expr, tok(r'-'), term, mkbop),
    term,
))

iter_expr = alt(
    seq(tok(r'repeat'), skip(r'\('), expr, skip(r'\)'), skip(r'{'),
        group(many(stmt)), skip(r'}'), skopt(r';'), mkloop),
    
    seq(tok(r'while'), skip(r'\('), expr, skip(r'\)'), skip(r'{'),
        group(many(stmt)), skip(r'}'), skopt(r';'), mkloop),
    
    seq(tok(r'do'), skip(r'{'), group(many(stmt)), skip(r'}'),
        skip(r'until'), skip(r'\('), expr, skip(r'\)'), skopt(r';'), mkdoloop),
)

cond_expr = alt(
    seq(skip(r'if'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), many(stmt),
        skip(r'}'), cond_expr, skopt(r';'), mkifcond),
    
    seq(skip(r'if'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), many(stmt),
        skip(r'}'), skopt(r';'), mksifcond),
    
    seq(skip(r'elseif'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), many(stmt),
        skip(r'}'), cond_expr, skopt(r';'), mkifcond),
    
    seq(skip(r'elseif'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), many(stmt),
        skip(r'}'), skopt(r';'), mksifcond),
    
    seq(tok(r'else'), skip(r'{'), many(stmt), skip(r'}'), skopt(r';'), mkecond),
)

stmt = alt(
    seq(typ, var, skip(r'='), expr, skip(r';'), mkbind),
    seq(skopt(r'\('), group(many(seq(typ, var, skopt(r','), mkfooargs))),
        skopt(r'\)'), skip(r'='), skopt(r'\('), group(many(seq(expr, skopt(r','), mkvar))), 
        skopt(r'\)'), skip(r';'), mkbbind),
    
    seq(skopt(r'\('), group(many(seq(var, skopt(r','), mkwrp))), 
        skopt(r'\)'), skip(r'='), skopt(r'\('),group(many(seq(expr, skopt(r','), mkvar))), 
        skopt(r'\)'), skip(r';'), mkassign),
    
    
    seq(var, tok(r'[*-/\+]'), skip(r'='), expr, skip(r';'), mksassign),
    seq(skip(r'return'), skopt(r'\('), group(many(seq(expr, skopt(r',')))), 
        skopt(r'\)'), skip(r';'), mkret),
    
    seq(fcall, skip(r';')),
    iter_expr,
    cond_expr,
)

def chek_ast(ast: tuple) -> tuple:
    special_funcs = [f for f in ast if f[0] == 'func' and f[1][0] in ('recv_internal', 'main')]
    if len(special_funcs) != 1:
        raise ValueError("AST must contain exactly one entry point 'recv_internal' or 'main'")
    return ast

def main_ast(path: str):
    src = re.sub(r'{-[\s\S]*?-}|;;.*', '', open(path).read())
    ast = chek_ast(parse(src, main).stack[0])
    return ast

def lib_ast(path: str):
    src = re.sub(r'{-[\s\S]*?-}|;;.*', '', open(path).read())
    ast = parse(src, main).stack[0]
    return ast