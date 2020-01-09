import sys


def is_sub_path(sub_path, path):  # type: (str, str) -> bool
    path_list = path.split('/') if path else []
    sub_path_list = sub_path.split('/') if sub_path else []
    return sub_path_list[:len(path_list)] == path_list and len(path_list) + 1 == len(sub_path_list)


def doc_text(dealer):  # (...) -> str
    if not dealer.__doc__:
        return ''
    return dealer.__doc__


def show_help(dealer, sub_help_doc):
    print(doc_text(dealer))
    print()
    if sub_help_doc:
        print(sub_help_doc)
    print()


class Application:
    def __init__(self, doc):
        self.doc = doc
        self.mapping = []

    # 获取最长匹配到path的dealer
    def _match_dealer(self, arg_list):  # type: ('Application', list) -> tuple
        arg_path = '/'.join(arg_list)
        for path, dealer in sorted(self.mapping, key=lambda x: x[0], reverse=True):
            if arg_path == path or arg_path.startswith(path + '/'):
                return path, dealer, path.count('/') + 1
        return None, None, None

    # 获取path的下一级列表即帮助文本
    def _sub_help_doc(self, path):  # type: ('Application', str) -> str
        cmd = sys.argv[0]
        ret = ''
        if not path:
            ret += self.doc + '\n'
        for sub_path, dealer in self.mapping:
            if is_sub_path(sub_path, path):
                ret += '  ' + cmd + ' ' + sub_path.replace('/', ' ') + '\t\t' \
                       + doc_text(dealer).strip().splitlines()[0].strip() + '\n'
        return ret

    def add(self,
            path,  # type: str
            dealer):
        # type: (...) -> 'Application'
        self.mapping.append((path.strip('/'), dealer))
        return self

    def run(self):  # type: ('Application') -> None
        list_params = []
        dict_params = {}
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
                    dict_params[key] = value
                else:
                    dict_params[arg] = ''
            elif arg.startswith('-'):
                assert len(arg) == 2, arg
                arg = arg[1:]
                if i + 1 >= L or arg_list[i + 1].startswith('-'):
                    dict_params[arg] = ''
                else:
                    dict_params[arg] = arg_list[i + 1]
                    i += 1
            else:
                list_params.append(arg)
            i += 1
        path, dealer, level = self._match_dealer(arg_list)   # 最长匹配
        if dealer is None:
            print(self._sub_help_doc(''))
            print()
        elif 'h' in dict_params or 'help' in dict_params:
            show_help(dealer, self._sub_help_doc(path))
        else:
            try:
                dealer(*list_params[level:], **dict_params)
            except TypeError as e:
                if str(e).startswith(dealer.__name__ + '() '):
                    show_help(dealer, self._sub_help_doc(path))
                else:
                    raise
            except AssertionError:
                show_help(dealer, self._sub_help_doc(path))


def run(callback):
    """
    $ cat index.py:
        import lesscli
        def work(*a, **b):
            print(a, b)
        lesscli.run(work, single='ab')

    $ python index.py a b
        ('a', 'b') {}

    $ python index.py -a 1 -b
        () {'a': '1', 'b': ''}

    $ python index.py -a 1 --bob=2 c.txt
        ('c.txt',) {'a': '1', 'bob': '2'}

    $ python index.py --bob -o c.txt d.txt
        ('d.txt',) {'bob': '', 'o': 'c.txt'}

    $ python index.py -a 1 -c 2 -d -e
        () {'a': '1', 'c': '2', 'd': '', 'e': ''}

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
                b[arg] = ''
        elif arg.startswith('-'):
            assert len(arg) == 2, arg
            arg = arg[1:]
            if i + 1 >= L or arg_list[i + 1].startswith('-'):
                b[arg] = ''
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
