import argparse
import re


def doc_text(dealer):  # (...) -> str
    text = getattr(dealer, '__doc__', '')
    return text.strip() if text and text.strip() else dealer.__name__


def get_summary(func):
    return doc_text(func).splitlines()[0]


def show_help(func):
    print(doc_text(func))
    print()


def add_subcommand(name, func):
    parser_args = [name]
    parser_kwargs = {
        'help': get_summary(func),
        'description': doc_text(func),
        'formatter_class': argparse.RawDescriptionHelpFormatter
    }
    parser_item = parser_args, parser_kwargs, func

    def f(g):
        if not hasattr(g, '__argparse_parsers__'):
            setattr(g, '__argparse_parsers__', [])
        getattr(g, '__argparse_parsers__').insert(0, parser_item)
        return g
    return f


def add_positional_argument(name, *, type=None, default=None, help='', required=True, choices=None, nargs=None, dest=''):
    """
    Add a positional argument to a function.

    Parameters
    ----------
    name : str
        The name of the argument. The name must be a valid identifier.
    type : type, optional
        The type of the argument.
    default : object, optional
        The default value of the argument.
    help : str, optional
        The help string for the argument.
    required : bool, optional
        True if the argument is required, False if it is optional. If the
        argument is optional and does not have a default value, the user must
        provide a value for it.
    choices : list, optional
        A list of valid values for the argument.
    nargs : int or str, optional
        The number of arguments for the argument.
        If nargs is '*', the argument is a list of values.
        refer to https://docs.python.org/3/library/argparse.html#nargs
    dest : str, optional
        The name of the attribute to be added to the object returned by
        parse_args().

    Returns
    -------
    f : callable
        A function that takes one argument, a function, and adds the argument to
        the function's argparse arguments.
    """
    assert re.match(
        r'\w+', name) is not None, 'Argument name must be a valid identifier'
    return add_argument(name, type=type, default=default, help=help, required=required, choices=choices, nargs=nargs, dest=dest)


def add_option_argument(name, *, short='', type=None, default=None, help='', required=True, choices=None, nargs=None, dest=''):
    """
    Add an optional argument to a function.

    Parameters
    ----------
    name : str
        The name of the argument. The name must be a valid identifier.
    short : str, optional
        The short name must be one character.
    type : type, optional
        The type of the argument. If the type is bool, the argument is a flag.
    default : object, optional
        The default value of the argument.
    help : str, optional
        The help string for the argument.
    required : bool, optional
        True if the argument is required, False if it is optional. If the
        argument is optional and does not have a default value, the user must
        provide a value for it.
    choices : list, optional
        A list of valid values for the argument.
    nargs : int or str, optional
        The number of arguments for the argument.
        If nargs is '*', the argument is a list of values.
        refer to https://docs.python.org/3/library/argparse.html#nargs
    dest : str, optional
        The name of the attribute to be added to the object returned by
        parse_args().

    Returns
    -------
    f : callable
        A function that takes one argument, a function, and adds the argument to
        the function's argparse arguments.
    """
    assert re.match(
        r'\w+', name) is not None, 'Argument name must be a valid identifier'
    return add_argument(f'--{name}', short=short, type=type, default=default, help=help, required=required, choices=choices, nargs=nargs, dest=dest)


def add_argument(name, *, short='', type=None, default=None, help='', required=True, choices=None, nargs=None, dest=''):
    """
    Add a positional or optional argument to a function.

    Parameters
    ----------
    name : str
        The name of the argument. If the name starts with '--', the argument is
        an option; otherwise, it is a positional argument.
    short : str, optional
        The short name of the argument, if the name does not start with '--'.
        The short name must be one character.
    type : type, optional
        The type of the argument. If the type is bool, the argument is a flag.
    default : object, optional
        The default value of the argument.
    help : str, optional
        The help string for the argument.
    required : bool, optional
        True if the argument is required, False if it is optional. If the
        argument is optional and does not have a default value, the user must
        provide a value for it.
    choices : list, optional
        A list of valid values for the argument.
    nargs : int or str, optional
        The number of arguments for the argument.
        If nargs is '*', the argument is a list of values.
        refer to https://docs.python.org/3/library/argparse.html#nargs
    dest : str, optional
        The name of the attribute to be added to the object returned by
        parse_args().

    Returns
    -------
    f : callable
        A function that takes one argument, a function, and adds the argument to
        the function's argparse arguments.
    """
    opt_args, opt_kwargs = [], {}
    assert re.match(
        r'(--)?\w+', name) is not None, 'Argument name must be a valid identifier'
    if short:
        assert re.match(
            r'\w', short) is not None, 'Argument short must be one-character'
        if name.startswith('--'):
            opt_args.append('-' + short)
        else:
            opt_kwargs['metavar'] = short

    opt_args.append(name)
    if type == bool:
        opt_kwargs['action'] = 'store_true'
    elif type is not None:
        opt_kwargs['type'] = type
    if default is not None:
        opt_kwargs['default'] = default
    opt_kwargs['help'] = help
    if required and name.startswith('--'):
        opt_kwargs['required'] = True
    elif not required and not name.startswith('--') and not nargs:
        opt_kwargs['nargs'] = '?'
    if choices is not None:
        assert isinstance(choices, list), 'choices must be a list'
        opt_kwargs['choices'] = choices
    if nargs:  # https://docs.python.org/3/library/argparse.html#nargs
        opt_kwargs['nargs'] = nargs
    if dest:
        opt_kwargs['dest'] = dest
    opt_item = opt_args, opt_kwargs

    def f(g):
        if not hasattr(g, '__argparse_args__'):
            setattr(g, '__argparse_args__', [])
        getattr(g, '__argparse_args__').insert(0, opt_item)
        return g
    return f


def run(dealer):
    def bind(parser, func):
        if hasattr(func, '__argparse_parsers__'):
            parsers = parser.add_subparsers()
            for parser_args, parser_kwargs, sub_func in getattr(func, '__argparse_parsers__'):
                sub_parser = parsers.add_parser(*parser_args, **parser_kwargs)
                sub_parser.set_defaults(_func=sub_func)
                bind(sub_parser, sub_func)
        if hasattr(func, '__argparse_args__'):
            for opt_args, opt_kwargs in getattr(func, '__argparse_args__'):
                parser.add_argument(*opt_args, **opt_kwargs)
        parser.set_defaults(_func=func)
        parser.set_defaults(_parser=parser)

    root_parser = argparse.ArgumentParser(description=doc_text(
        dealer), formatter_class=argparse.RawDescriptionHelpFormatter)
    bind(root_parser, dealer)
    args = root_parser.parse_args()
    cur_parser = getattr(args, '_parser')
    cur_func = getattr(args, '_func')
    if hasattr(cur_func, '__argparse_args__') or not hasattr(cur_func, '__argparse_parsers__'):
        try:
            cur_func(**{k: v for k, v in args.__dict__.items() if k[0] != '_'})
        except AssertionError as e:
            if str(e):
                cur_parser.error(str(e) + '!\n')
            else:
                cur_parser.error('-h or --help for help!')
    else:
        cur_parser.print_help()


def main():
    text = """
    
    Boilerplate of Installable Project:
        git clone https://github.com/qorzj/lesscli.git

    Documentation of "Writing the Setup Script":
        https://docs.python.org/2/distutils/setupscript.html
        https://docs.python.org/3/distutils/setupscript.html
        
    Argparse Tutorial:
        https://docs.python.org/3/howto/argparse.html
        https://docs.python.org/3/library/argparse.html

    Documentation of lesscli.run:
        >>> import lesscli
        >>> help(lesscli.run)

    """
    print(text)
