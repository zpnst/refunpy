from libs.peco.peco import *

ws = eat(r'\s*')
token = lambda f: memo(seq(ws, f))
tok = lambda c: token(push(eat(c)))
skip = lambda c: token(eat(c))

mkvar = to(lambda x: x)
mkstr = to(lambda s: s)
mknum = to(lambda x: int(x))
mkbop = to(lambda a, o, b: (o, a, b))
mkbind = to(lambda t, v, e: ('bind', (t, v), e))
mkbbind = to(lambda b, e: ('bind', b, e))
mkassign = to(lambda v, e: ('assign', v, e))
mksassign = to(lambda v, s, e: ('assign', v, (s, v, e)))

mkloop = to(lambda lname, cond, body: (lname, cond, body))
mkdoloop = to(lambda body, cond: ('dountil', cond, body))

mkifcond = to(lambda cond, body, ob: ('if', cond, body, ob))
mksifcond = to(lambda cond, body: ('if', cond, body, ()))
mkecond = to(lambda _, body: (body))

mkret = to(lambda ret: ('return', ret))
mkcall = to(lambda fn, args: ('fcall', fn, args))
mkchcall = to(lambda fns: ('chain_call', fns))
mkfooargs = to(lambda x, y: (x, y))
mkfoo = to(lambda ret, name, args, specs, body: ('func', (name, specs, args, ret), body))

mkinc = to(lambda path: ('include', path))

var = seq(tok(r'[a-zA-Z][a-zA-Z0-9_]*'), mkvar)
path = seq(tok(r'[a-zA-Z0-9_/.]+'), mkvar)
num = seq(tok(r'-?\d+'), mknum)
type = tok(r'int|slice|cell|builder')
string = seq(tok(r'\"[a-zA-Z0-9!,]*\"'), mkstr)
specs = tok(r'impure|inline_ref|inline|method_id')

expr = lambda s: expr(s)
term = lambda s: term(s)
stat = lambda s: stat(s)

cond_expr = lambda s: cond_expr(s)

block = group(many(seq(stat, ws)))
fcall = seq(var, skip(r'\('), group(many(seq(expr, skip(r',?')))), skip(r'\)'), mkcall)

fdec = seq(skip(r'\(?'), group(many(seq(type, skip(r',?')))), skip(r'\)?'),
        var, skip(r'\('), group(many(seq(type, var, skip(r',?'), mkfooargs))), skip(r'\)'), group(many(seq(specs, ws))), skip(r'{'), block, skip(r'}'), mkfoo)

glob = alt(
    fdec,
    seq(skip(r'#'), skip(r'include'), skip(r'"'), path, skip(r'"'), skip(r';'), mkinc)  
)

main = group(many(seq(glob, ws)))

atoms = alt(
    var,
    num,
)

factor = alt(
    group(seq(fcall, many(seq(skip(r'\.?'), fcall)))),
    seq(skip(r'\('), expr, skip(r'\)')),
    var,
    num,
    string,
)

term = left(alt(
    seq(term, tok(r'=='), factor, mkbop),
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
    seq(tok(r'repeat'), skip(r'\('), atoms, skip(r'\)'), skip(r'{'), group(many(stat)), skip(r'}'), skip(r';?'), mkloop),
    seq(tok(r'while'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), group(many(stat)), skip(r'}'), skip(r';?'), mkloop),
    seq(tok(r'do'), skip(r'{'), group(many(stat)), skip(r'}'), skip(r'until'), skip(r'\('), expr, skip(r'\)'), skip(r';?'), mkdoloop),
)

cond_expr = alt(
    seq(skip(r'if'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), many(stat), skip(r'}'), cond_expr, skip(r';?'), mkifcond),
    seq(skip(r'if'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), many(stat), skip(r'}'), skip(r';?'), mksifcond),
    seq(skip(r'elseif'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), many(stat), skip(r'}'), cond_expr, skip(r';?'), mkifcond),
    seq(skip(r'elseif'), skip(r'\('), expr, skip(r'\)'), skip(r'{'), many(stat), skip(r'}'), skip(r';?'), mksifcond),
    seq(tok(r'else'), skip(r'{'), many(stat), skip(r'}'), skip(r';?'), mkecond),
)

stat = alt(
    seq(skip(r'\(?'), group(many(seq(type, var, skip(r',?'), mkfooargs))), skip(r'\)?'), skip(r'='), skip(r'\(?'), group(many(seq(expr, skip(r',?'), mkvar))), skip(r'\)?'), skip(r';'), mkbbind),
    seq(var, skip(r'='), expr, skip(r';'), mkassign),
    seq(var, tok(r'[*-/\+]'), skip(r'='), expr, skip(r';'), mksassign),
    seq(skip(r'return'), skip(r'\(?'), group(many(seq(expr, skip(r',?')))), skip(r'\)?'), skip(r';'), mkret),
    seq(fcall, skip(r';')),
    iter_expr,
    cond_expr,
)

rsrc = lambda path: "".join([line for line in open(path, mode="r").readlines() \
    if not line.strip().startswith(';;')]).replace("\n", "").replace(" ", "")


def prepare_ast(ast: tuple) -> tuple:
    special_funcs = [f for f in ast if f[0] == 'func' and f[1][0] in ('recv_internal', 'main')]
    if len(special_funcs) != 1:
        raise ValueError("AST must contain exactly one entry point 'recv_internal' or 'main'")
    
    special_func = special_funcs[0]
    others = tuple(f for f in ast if f != special_func)
    return (special_func,) + others


def get_ast(path: str):
    src = rsrc(path)
    ast = prepare_ast(parse(src, main).stack[0])
    return ast