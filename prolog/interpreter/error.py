class PrologError(Exception):
    pass

class UncatchableError(PrologError):
    def __init__(self, message):
        self.message = message

class TermedError(PrologError):
    def __init__(self, term):
        self.term = term

    def get_errstr(self, engine):
        from prolog.builtin import formatting
        from prolog.interpreter import term

        f = formatting.TermFormatter(engine, quoted=True, max_depth=20)
        f._make_reverse_op_mapping()

        errorterm = self.term.argument_at(0)

        if isinstance(errorterm, term.Callable):
            if errorterm.name() == "instantiation_error":
                return "arguments not sufficiently instantiated\n"
            elif errorterm.name()== "existence_error":
                if isinstance(errorterm, term.Callable):
                     return "Undefined %s: %s\n" % (
                        f.format(errorterm.argument_at(0)),
                        f.format(errorterm.argument_at(1)))
            elif errorterm.name()== "domain_error":
                if isinstance(errorterm, term.Callable):
                    return "Domain error: '%s' expected, found '%s'\n" % (
                        f.format(errorterm.argument_at(0)),
                        f.format(errorterm.argument_at(1)))
            elif errorterm.name()== "type_error":
                if isinstance(errorterm, term.Callable):
                    return "Type error: '%s' expected, found '%s'\n" % (
                        f.format(errorterm.argument_at(0)),
                        f.format(errorterm.argument_at(1)))
            elif errorterm.name() == "syntax_error":
                if isinstance(errorterm, term.Callable):
                    return "Syntax error: '%s'\n" % \
                    f.format(errorterm.argument_at(0))
            elif errorterm.name() == "permission_error":
                if isinstance(errorterm, term.Callable):
                    return "Permission error: '%s', '%s', '%s'\n" % (
                    f.format(errorterm.argument_at(0)),
                    f.format(errorterm.argument_at(1)),
                    f.format(errorterm.argument_at(2)))
            elif errorterm.name() == "representation_error":
                if isinstance(errorterm, term.Callable):
                    return "%s: Cannot represent: %s\n" % (
                    f.format(errorterm.argument_at(0)),
                    f.format(errorterm.argument_at(1)))
            elif errorterm.name() == "import_error":
                if isinstance(errorterm, term.Callable):
                    return "Exported procedure %s:%s is not defined\n" % (
                    f.format(errorterm.argument_at(0)),
                    f.format(errorterm.argument_at(1)))
            else:
                return "Internal error" # AKA, I have no clue what went wrong.

class CatchableError(TermedError): pass
class UncaughtError(TermedError): pass

def wrap_error(t):
    from prolog.interpreter import term
    t = term.Callable.build("error", [t])
    return CatchableError(t)

class UnificationFailed(PrologError):
    pass

def throw_syntax_error(msg):
    from prolog.interpreter import term
    t = term.Callable.build("syntax_error", [term.Callable.build(msg)])
    raise wrap_error(t)

def throw_import_error(modulename, signature):
    from prolog.interpreter import term
    t = term.Callable.build("import_error", [term.Callable.build(modulename),
            term.Callable.build(signature.string())])
    raise wrap_error(t)

def throw_existence_error(object_type, obj):
    from prolog.interpreter import term
    t = term.Callable.build("existence_error", [term.Callable.build(object_type), obj])
    raise wrap_error(t)

def throw_instantiation_error(obj = None):
    from prolog.interpreter import term
    raise wrap_error(term.Callable.build("instantiation_error"))

def throw_representation_error(signature, msg):
    from prolog.interpreter import term
    t = term.Callable.build("representation_error",
            [term.Callable.build(signature), term.Callable.build(msg)])
    raise wrap_error(t)

def throw_type_error(valid_type, obj):
    # valid types are:
    # atom, atomic, byte, callable, character
    # evaluable, in_byte, in_character, integer, list
    # number, predicate_indicator, variable, text
    from prolog.interpreter import term
    raise wrap_error(
        term.Callable.build("type_error", [term.Callable.build(valid_type), obj]))

def throw_domain_error(valid_domain, obj):
    from prolog.interpreter import term
    # valid domains are:
    # character_code_list, close_option, flag_value, io_mode,
    # not_empty_list, not_less_than_zero, operator_priority,
    # operator_specifier, prolog_flag, read_option, source_sink,
    # stream, stream_option, stream_or_alias, stream_position,
    # stream_property, write_option
    raise wrap_error(
        term.Callable.build("domain_error", [term.Callable.build(valid_domain), obj]))

def throw_permission_error(operation, permission_type, obj):
    from prolog.interpreter import term
    # valid operations are:
    # access, create, input, modify, open, output, reposition 

    # valid permission_types are:
    # binary_stream, flag, operator, past_end_of_stream, private_procedure,
    # static_procedure, source_sink, stream, text_stream. 
    raise wrap_error(
        term.Callable.build("permission_error", [term.Callable.build(operation),
                                       term.Callable.build(permission_type),
                                       obj]))
