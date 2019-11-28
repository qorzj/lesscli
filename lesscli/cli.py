import sys


def run(callback, single=''):
    """
    $ cat index.py:
        import lesscli
        def work(*a, **b):
            print(a, b)
        lesscli.run(work, single='ab')

    $ python index.py a b
        ('a', 'b') {}

    $ python index.py -a 1 -b
        ('1',) {'a': '✓', 'b': '✓'}

    $ python index.py -a 1 --bob=2 c.txt
        ('1', 'c.txt') {'a': '✓', 'bob': '2'}

    $ python index.py --bob -o c.txt d.txt
        ('d.txt',) {'bob': '✓', 'o': 'c.txt'}

    $ python index.py -a 1 -c 2 -d -e
        ('1',) {'a': '✓', 'c': '2', 'd': '✓', 'e': '✓'}

    $ python index.py --bob='1 2' -c " 3 " ''
        ('',) {'bob': '1 2', 'c': ' 3 '}
    """
    a = []
    b = {}
    arg_list = sys.argv[1:]
    L = len(arg_list)
    i = 0
    while i < L:
        arg = arg_list[i]
        if arg.startswith('--'):
            assert len(arg) >= 3 and arg[:3] != '---', arg
            arg = arg[2:]
            if '=' in arg:
                key, value = arg.split('=', 1)
                b[key] = value
            else:
                b[arg] = '✓'
        elif arg.startswith('-'):
            assert len(arg) == 2, arg
            arg = arg[1:]
            if arg in single or i + 1 >= L or arg_list[i + 1].startswith('-'):
                b[arg] = '✓'
            else:
                b[arg] = arg_list[i + 1]
                i += 1
        else:
            a.append(arg)
        i += 1
    callback(*a, **b)


def main():
    text = """
    
    Boilerplate of Installable Project:
        git clone https://github.com/qorzj/lesscli.git

    Documentation of "Writing the Setup Script":
        https://docs.python.org/2/distutils/setupscript.html
        https://docs.python.org/3/distutils/setupscript.html

    Documentation of lesscli.run:
        >>> import lesscli
        >>> help(lesscli.run)

    """
    print(text)
