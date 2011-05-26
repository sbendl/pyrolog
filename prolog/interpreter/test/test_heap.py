import py
from prolog.interpreter.heap import Heap, HookChain
from prolog.interpreter.term import AttVar, Var, Callable, Number, Atom, AttMap

def test_heap():
    h1 = Heap()
    v1 = h1.newvar()
    v2 = h1.newvar()
    h1.add_trail(v1)
    v1.binding = 1
    h2 = h1.branch()
    h2.add_trail(v1)
    v1.binding = 2
    h2.add_trail(v2)
    v2.binding = 3

    h3 = h2.revert_upto(h1)
    assert v1.binding == 1
    assert v2.binding is None
    assert h3 is h2

    h1 = Heap()
    h2 = h1.revert_upto(h1)
    assert h2 is h1

    h1 = Heap()
    h2 = h1.branch()
    h3 = h2.revert_upto(h1, discard_choicepoint=True)
    assert h3 is h1

def test_heap_dont_trail_new():
    h1 = Heap()
    v1 = h1.newvar()
    h1.add_trail(v1)
    v1.binding = 1
    h2 = h1.branch()
    v2 = h2.newvar()
    h2.add_trail(v1)
    v1.binding = 2
    h2.add_trail(v2)
    v2.binding = 3

    h3 = h2.revert_upto(h1)
    assert v1.binding == 1
    assert v2.binding == 3 # wasn't undone, because v2 dies
    assert h3 is h2

def test_heap_discard():
    h1 = Heap()
    h2 = h1.branch()
    h3 = h2.branch()
    h = h2.discard(h3)
    assert h3.prev is h1
    assert h3 is h

    h0 = Heap()
    v0 = h0.newvar()

    h1 = h0.branch()
    v1 = h1.newvar()

    h2 = h1.branch()
    v2 = h2.newvar()

    h2.add_trail(v0)
    v0.binding = 1
    h2.add_trail(v1)
    v1.binding = 2

    h3 = h2.branch()
    h3.add_trail(v2)
    v2.binding = 3

    h = h2.discard(h3)
    assert h3.prev is h1
    assert h3 is h

    assert h3.revert_upto(h0)
    assert v0.binding is None
    assert v1.binding is None
    assert v2.binding == 3 # not backtracked, because it goes away

def test_heap_discard_variable_shunting():
    h0 = Heap()
    v0 = h0.newvar()

    h1 = h0.branch()
    v1a = h1.newvar()
    v1b = h1.newvar()

    h2 = h1.branch()
    v2 = h1.newvar()

    h2.add_trail(v0)
    v0.binding = 1
    h2.add_trail(v1a)
    v1a.binding = 2

    h = h1.discard(h2)
    assert h2.prev is h0
    assert h2 is h
    assert h1.discarded
    assert h1.prev is h2                                                                                                                                

    h2.add_trail(v1b)
    v1b.binding = 3

    assert h2.revert_upto(h0)

    assert v0.binding is None
    assert v1a.binding == 2 # not backtracked, because it goes away
    assert v1b.binding == 3 # not backtracked, because it goes away

def test_new_attvar():
    h = Heap()
    v = h.new_attvar()
    assert isinstance(v, AttVar)
    assert v.created_after_choice_point is h

def test_add_trail_atts():
    hp = Heap()
    a = hp.new_attvar()
    assert a.created_after_choice_point is hp
    hp.trail_attrs == []
    ma = AttMap()
    ma.indexes = {"a": 0}
    a.value_list = [10]
    a.attmap = ma

    hp.add_trail_atts(a, "a", ma)
    assert hp.trail_attrs == []
    hp2 = hp.branch()
    hp2.add_trail_atts(a, "a", ma)
    assert hp2.trail_attrs == [(a, 0, 10, ma)]
    a.add_attribute("a", 20)
    assert a.value_list == [20]
    hp2._revert()
    assert a.value_list == [10]

    hp3 = hp2.branch()
    hp3.add_trail_atts(a, "b", ma)
    a.add_attribute("b", 30)
    assert a.value_list == [10, 30]
    assert a.attmap.indexes == {"a": 0, "b": 1}
    assert a.attmap is not ma
    hp3._revert()
    assert a.value_list == [10, None]

def test_heap_dont_trail_new_attvars():
    h1 = Heap()
    v1 = h1.new_attvar()
    h1.add_trail_atts(v1, "m")
    v1.add_attribute("m", 1)
    h2 = h1.branch()
    v2 = h2.new_attvar()
    h2.add_trail_atts(v1, "m")
    v1.add_attribute("m", 2)
    h2.add_trail_atts(v2, "m")
    v2.add_attribute("m", 3)

    h3 = h2.revert_upto(h1)
    t1 = v1.get_attribute("m")
    assert t1[0] == 1
    assert t1[1] == 0
    t2 = v2.get_attribute("m") # wasn't undone, because v2 dies
    assert t2[0] == 3
    assert t2[1] == 0
    assert h3 is h2
    
def test_discard_with_attvars():
    py.test.skip("not implemented yet")
    h0 = Heap()
    v0 = h0.new_attvar()

    h1 = h0.branch()
    v1 = h1.new_attvar()

    h2 = h1.branch()
    v2 = h2.new_attvar()

    h2.add_trail_atts(v0, "m")
    v0.atts = {"m": 1}
    h2.add_trail_atts(v1, "n")
    v1.atts = {"n": 2}

    h3 = h2.branch()
    h3.add_trail_atts(v2, "a")
    v2.atts = {"a": 3}

    h = h2.discard(h3)
    assert h3.prev is h1
    assert h3 is h
    assert h3.revert_upto(h0)
    assert v0.atts == {}
    assert v1.atts == {}
    assert v2.atts == {"a": 3}

def test_hookchain():
    hc = HookChain()
    assert hc.last is None
    hc.add_hook(1)
    hc.add_hook(2)
    hc.add_hook(3)
    assert hc.last.hook == 3
    assert hc.last.next.hook == 2
    assert hc.last.next.next.hook == 1
    assert hc.last.next.next.next is None

def test_simple_hooks():
    hp = Heap()
    v = Var()
    a = AttVar()
    v.unify(a, hp)
    assert hp.hooks.last is None 
    v.unify(Number(1), hp)
    assert hp.hooks.last.hook == a

    hp = Heap()
    v1 = Var()
    v2 = Var()
    a1 = AttVar()
    a2 = AttVar()
    v1.unify(a1, hp)
    assert hp.hooks.last is None
    v2.unify(a2, hp)
    assert hp.hooks.last is None
    v1.unify(v2, hp)
    assert hp.hooks.last.hook == a1

    hp = Heap()
    v1 = Var()
    v2 = Var()
    v3 = Var()
    a1 = AttVar()
    a2 = AttVar()
    a3 = AttVar()
    v1.unify(a1, hp)
    v2.unify(a2, hp)
    v3.unify(a3, hp)

    v1.unify(v2, hp)
    v2.unify(v3, hp)
    assert hp.hooks.last.hook == a2
    assert hp.hooks.last.next.hook == a1
    assert hp.hooks.last.next.next is None

    hp = Heap()
    v1 = Var()
    v2 = Var()
    a1 = AttVar()
    a2 = AttVar()
    v1.unify(a1, hp)
    v2.unify(a2, hp)
    assert hp.hooks.last is None
    v1.unify(v2, hp)
    assert hp.hooks.last.hook == a1
    v1.unify(Number(1), hp)
    assert hp.hooks.last.hook == a2
    assert hp.hooks.last.next.hook == a1
    assert hp.hooks.last.next.next is None

    hp = Heap()
    v1 = Var()
    v2 = Var()
    a1 = AttVar()
    a2 = AttVar()
    v1.unify(a1, hp)
    v2.unify(a2, hp)
    t1 = Callable.build("f", [v1, v2])
    t2 = Callable.build("f", [Atom("a"), Atom("b")])
    t1.unify(t2, hp)
    assert hp.hooks.last.hook == a2
    assert hp.hooks.last.next.hook == a1
    assert hp.hooks.last.next.next is None

    hp = Heap()
    v = Var()
    av = AttVar()
    v.unify(av, hp)
    assert hp.hooks.last is None
    a = Callable.build("a")
    v.unify(a, hp)
    assert hp.hooks.last.hook == av
    v.unify(a, hp)
    assert hp.hooks.last.hook == av
    assert hp.hooks.last.next is None

def test_hookchain_size():
    h = HookChain()
    assert h._size() == 0
    h.add_hook(1)
    assert h._size() == 1
    h.add_hook(2)
    assert h._size() == 2
    h.clear()
    assert h._size() == 0


