import py
from prolog.interpreter.continuation import *
from prolog.interpreter.parsing import parse_query_term, get_engine
from prolog.interpreter.parsing import get_query_and_vars
from prolog.interpreter.error import UnificationFailed
from prolog.interpreter.test.tool import collect_all, assert_true, assert_false
from prolog.interpreter.term import Number

class CheckContinuation(Continuation):
    rule = None
    def __init__(self, engine, seen=10):
        self.engine = engine
        self.nextcont = None
        self._candiscard = True
        self.seen = seen
    def is_done(self):
        return False
    def activate(self, fcont, heap):
        # hack: use _dot to count size of tree
        seen = set()

        list(fcont._dot(seen))
        assert len(seen) < self.seen
        depth = 0
        while fcont.nextcont:
            depth += 1
            fcont = fcont.nextcont
        assert depth < self.seen
        depth = 0
        numvars = 0
        while heap:
            depth += 1
            numvars += heap.i
            heap = heap.prev
        assert depth < self.seen
        assert numvars < self.seen
        return DoneContinuation(self.engine), DoneContinuation(self.engine), heap

def test_cut():
    e = get_engine("""
        f(0).
        f(X) :- X>0, X0 is X - 1, !, f(X0).
        f(_).""")
    query = Callable.build("f", [Number(100)])
    e.run_query(query, CheckContinuation(e))

def test_call():
    e = get_engine("""
        g(0).
        g(X) :- X > 0, X0 is X - 1, call(g(X0)).""")
    query = Callable.build("g", [Number(100)])
    e.run_query(query, CheckContinuation(e))

def test_map():
    e = get_engine("""
        add1(X, X1) :- X1 is X + 1.
        map(_, [], []).
        map(Pred, [H1 | T1], [H2 | T2]) :-
            C =.. [Pred, H1, H2],
            call(C),
            map(Pred, T1, T2).
        map(X) :- !.
        h(X) :- map(add1, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 5, 6, 7, 8, 9, 10, 11, 12, 13], [X | _]).
    """)
    query = Callable.build("h", [Number(2)])
    e.run_query(query, CheckContinuation(e))

def test_partition():
    e = get_engine("""
    partition([],_,[],[]).
    partition([X|L],Y,[X|L1],L2) :-
        X =< Y, !,
        partition(L,Y,L1,L2).
    partition([X|L],Y,L1,[X|L2]) :-
        partition(L,Y,L1,L2).
    i(X) :- partition([6, 6, 6, 6, 6, 6, 6, 1, 5, 1, 5, 7, 9,2,4, 3, 7, 9, 0, 10], 5, [X | _], _).
    """)
    query = Callable.build("i", [Number(1)])
    e.run_query(query, CheckContinuation(e))

def test_tak():
    e = get_engine("""
    tak(X,Y,Z,A) :-
            write(tak(X, Y, Z, A)), nl,
            X =< Y, !,
            write('succeeded'), nl,
            Z = A.
    tak(X,Y,Z,A) :-
            % X > Y,
            X1 is X - 1,
            tak(X1,Y,Z,A1),
            Y1 is Y - 1,
            tak(Y1,Z,X,A2),
            Z1 is Z - 1,
            tak(Z1,X,Y,A3),
            tak(A1,A2,A3,A).

    j(1) :- tak(18, 5, 5, _).
    """)
    query = Callable.build("j", [Number(1)])
    e.run_query(query, CheckContinuation(e))

def test_recurse_with_if():
    e = get_engine("""
    equal(0, 0). equal(X, X).
    f(X) :- equal(X, 0) -> true ; Y is X - 1, f(Y).
    """)
    query = Callable.build("f", [Number(100)])
    e.run_query(query, CheckContinuation(e))

def test_recurse_with_many_base_cases():
    e = get_engine("""
    f(X) :- X = 0.
    f(X) :- X = 0.
    f(X) :- X = 0.
    f(X) :- X = 0.
    f(X) :- X = 0.
    f(X) :- Y is X - 1, f(Y).
    """)
    query = Callable.build("f", [Number(100)])
    e.run_query(query, CheckContinuation(e))