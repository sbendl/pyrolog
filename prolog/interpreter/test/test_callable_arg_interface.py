from prolog.interpreter.parsing import parse_file, TermBuilder
from prolog.interpreter.term import Atom, Number, Term
import py

def parse(inp):
    t = parse_file(inp)
    builder = TermBuilder()
    return builder.build(t)
    
atom = parse('a.')[0]
term = parse('t(a, b, c, d, f).')[0]
def test_atom_get_signature():
    r = atom.get_prolog_signature() 
    r.name == '/'
    r._args[0] == Atom('a')
    r._args[1] == Number(0)

def test_atom_get_arguments():
    assert atom.arguments() == []
    
def test_atom_arguemtn_count():
    assert atom.argument_count() == 0
    
def test_atom_get_argument_at():
    assert py.test.raises(IndexError, 'atom.argument_at(0)')
    
def test_term_get_signature():
    r = term.get_prolog_signature()
    print r
    assert r.name == '/'
    assert r._args[0].name == 't'
    assert r._args[1].num == 5
    
def test_term_get_arguments():
    t = term.arguments()
    assert isinstance(t, list)
    assert len(t) == 5
    
def test_term_get_argument_out_of_range():
    py.test.raises(IndexError, 'term.argument_at(5)')

def test_term_get_argument_in_range():
    t =  term.argument_at(2)
    assert t.name == 'c'
    
def test_term_argument_count():
    assert term.argument_count() == 5