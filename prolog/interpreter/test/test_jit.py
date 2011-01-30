import sys
from pypy.jit.metainterp.test.test_basic import LLJitMixin
from pypy.rlib.jit import OPTIMIZER_FULL, OPTIMIZER_SIMPLE

from prolog.interpreter.parsing import parse_query_term, get_engine
from prolog.interpreter.parsing import get_query_and_vars
from prolog.interpreter.continuation import jitdriver

class TestLLtype(LLJitMixin):
    def test_append(self):
        e = get_engine("""
        app([], X, X).
        app([H | T1], T2, [H | T3]) :-
            app(T1, T2, T3).
        loop(0).
        loop(X) :- X > 0, X0 is X - 1, call(loop(X0)).
        nrev([],[]).
        nrev([X|Y],Z) :- nrev(Y,Z1),
                         app(Z1,[X],Z).

        run(X) :- solve([X]).
        solve([]).
        solve([A | T]) :-
            my_pred(A, T, T1),
            solve(T1).

        my_pred(app([], X, X), T, T).
        my_pred(app([H | T1], T2, [H | T3]), T, [app(T1, T2, T3) | T]).
        my_pred(nrev([], []), T, T).
        my_pred(nrev([X | Y], Z), Rest, [nrev(Y, Z1), app(Z1, [X], Z) | Rest]).

        add1(X, X1) :- X1 is X + 1.
        map(_, [], []).
        map(Pred, [H1 | T1], [H2 | T2]) :-
            C =.. [Pred, H1, H2],
            call(C),
            map(Pred, T1, T2).

        partition([],_,[],[]).
        partition([X|L],Y,[X|L1],L2) :-
            X =< Y, !,
            partition(L,Y,L1,L2).
        partition([X|L],Y,L1,[X|L2]) :-
            partition(L,Y,L1,L2).
        """)

        t1 = parse_query_term("app([1, 2, 3, 4, 5, 6], [8, 9], X), X == [1, 2, 3, 4, 5, 6, 8, 9].")
        t2 = parse_query_term("loop(100).")
        t3 = parse_query_term("nrev([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], X), X == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1].")
        t4 = parse_query_term("run(app([1, 2, 3, 4, 5, 6, 7], [8, 9], X)), X == [1, 2, 3, 4, 5, 6, 7, 8, 9].")
        t5 = parse_query_term("map(add1, [1, 2, 3, 4, 5, 6, 7], X), X == [2, 3, 4, 5, 6, 7, 8].")
        t6 = parse_query_term("partition([6, 6, 6, 6, 6, 6, 66, 3, 6, 1, 2, 6, 8, 9, 0,4, 2, 5, 1, 106, 3, 6, 1, 2, 6, 8, 9, 0,4, 2, 5, 1, 10, 3, 6, 1, 2, 6, 8, 9, 0,4, 2, 5, 1, 10], 5, X, Y).")
        t7 = parse_query_term("findall(X+Y, app([X|_], [Y|_], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]), L).")
        def interp_w(c):
            jitdriver.set_param("inlining", True)
            if c == 1:
                t = t1
            elif c == 2:
                t = t2
            elif c == 3:
                t = t3
            elif c == 4:
                t = t4
            elif c == 5:
                t = t5
            elif c == 6:
                t = t6
            elif c == 7:
                t = t7
            else:
                raise ValueError
            e.run(t)
        # XXX
        from pypy.conftest import option
        interp_w(1)
        option.view = False
        option.viewloops = True
        self.meta_interp(interp_w, [6], listcomp=True, backendopt=True,
                         listops=True, optimizer=OPTIMIZER_FULL, view=True)
