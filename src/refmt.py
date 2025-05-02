from libs.refalpy.refalpy import refal

imports = {
    'type': lambda x: (type(x[0]).__name__,),
    'concat': lambda x: (''.join(map(str, x)),),
    'tuple': lambda x: tuple(x[0]),
    'repr': lambda x: (repr(x[0]),),
    'prout': lambda args: (print(args, "\n"), ())[~0],
}

@refal(imports)
def fmt_rules():
    
    p[e.e] = prout[e.e], e.e 

    call[s.name, {}] = '<', s.name, '>'
    call[s.name, t.args] = '<', s.name, ' ', expr[t.args], '>'

    spec[s._, s.name] = s.name
    spec['call', s.name, t.args] = call[s.name, t.args]

    val[t.x, 'list'] = spec[tuple[t.x]]
    val[{}, s._] = '()'
    val[{e.x}, s._] = '(', expr[{e.x}], ')'
    val[t.x, s._] = repr[t.x]

    expr_rest[{}] = _
    expr_rest[{t.x, e.y}] = ' ', val[t.x, type[t.x]], expr_rest[{e.y}]

    expr[{}] = '_'
    expr[{t.x, e.y}] = val[t.x, type[t.x]], expr_rest[{e.y}]

    rule[s.name, t.left, t.right] = call[s.name, t.left], ' = ', expr[t.right], '\n'

    item[s.name, {}] = _
    item[s.name, {{{'docs', s.doc}, t.right}, e.body}] =\
        '\n', '/** MODULE: ', s.name, '\n', '    DESCRIPTION: ', s.doc, '*/', '\n', item[s.name, {e.body}]
    item[s.name, {{t.left, t.right}, e.body}] = rule[s.name, t.left, t.right], item[s.name, {e.body}]
   
    fmt_rest = _
    fmt_rest[{s.name, e.body}, e.x] = '\n', item[s.name, e.body], fmt_rest[e.x]

    fmt[{s.name, e.body}, e.x] = concat[item[s.name, e.body], fmt_rest[e.x]]


def fmt(rules):    
    return fmt_rules('fmt', tuple(rules().ir.items()))[0]