import sys
from libs.refalpy.refalpy import refal


@refal({
    'add': lambda arg: (arg[0] + arg[1],),
    'typeof': lambda arg: (type(arg[0]).__name__,),
    
    'prout': lambda arg: (print("-- STDOUT:", arg, "\n"), ())[~0],
    'pexit': lambda arg: (print("-- STDOUT:", arg, "\n"), sys.exit(0), ())[~0],
})
def while_rules():
    
    p[e.x] = prout[e.x]
    pp[e.x] = pexit[e.x]

    get[{e.x, {s.key, t.val}, e.y}, s.key] = t.val
    
    put[{e.x, {s.key, t.val}, e.y}, s.key, t.new] = {e.x, {s.key, t.new}, e.y}
    put[{e.x}, s.key, t.val] = {e.x, {s.key, t.val}}

    literal['int', s.v, t.env] = s.v
    literal['str', s.v, t.env] = get[t.env, s.v]

    expr[s.v, t.env] = literal[typeof[s.v], s.v, t.env]
    expr[{t.e1, '+', t.e2}, t.env] = add[expr[t.e1, t.env], expr[t.e2, t.env]]

    stmt[{s.v, '=', t.e}, t.env] = put[t.env, s.v, expr[t.e, t.env]]

    while_stmt[0, t._, t.env] = t.env
    while_stmt[s._, {t.e, {e.block}}, t.env] = interp[
        {e.block, {'while', t.e, {e.block}}}, t.env]

    stmt[{'while', t.e, t.block}, t.env] = while_stmt[expr[t.e, t.env],
                                                      {t.e, t.block}, t.env]

    interp[{t.stmt, e.block}, t.env] = interp[{e.block}, stmt[t.stmt, t.env]]
    interp[{}, t.env] = t.env


prog = (
    ('r', '=', 0),
    ('i', '=', ((2, "+", 3), '+', 5)),
    ('while', ('i', "+", 11),
        (('i', '=', ('i', '+', -1)),
         ('r', '=', ('r', '+', 2))))
)


print(while_rules('interp', (prog, ())))