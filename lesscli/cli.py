import sys


def doc_text(dealer):  # (...) -> str
    text = getattr(dealer, '__doc__', '')
    return text.strip() if text and text.strip() else dealer.__name__


def show_help(dealer):
    print(doc_text(dealer))
    print()


class Application:
    def __init__(self, doc=''):
        self.doc = doc
        self.mapping = []

    # 获取最长匹配到path的dealer函数
    # arg_list是不含减号的argv前缀部分
    # 返回path, dealer, level
    def _match_dealer(self, arg_list):
        cur_app = self
        cur_level = 0
        cur_path = ()
        if not arg_list:
            return cur_path, cur_app, cur_level
        while True:
            quit = True
            for path, dealer in cur_app.mapping:
                if arg_list[cur_level] == path:
                    cur_level += 1
                    cur_path += (path,)
                    cur_app = dealer
                    if isinstance(dealer, Application):
                        quit = cur_level == len(arg_list)
                    break
            if quit:
                return cur_path, cur_app, cur_level


    # 获取path的下一级列表即帮助文本
    def _sub_help_doc(self, path, app):  # type: (...) -> str
        cmd = sys.argv[0]
        if '/' in cmd:
            cmd = cmd.rsplit('/', 1)[-1]
        ret = ''
        if app is None:
            app = self
        if not isinstance(app, Application):
            raise ValueError('app must be Application')
        ret += app.doc + '\n'
        for sub_path, dealer in app.mapping:
            ret += '  ' + cmd + ' ' + ' '.join(list(path)) + ' ' + sub_path + '\t\t'
            if isinstance(dealer, Application):
                ret += dealer.doc.strip().splitlines()[0].strip() + '\n'
            else:
                ret += doc_text(dealer).strip().splitlines()[0].strip() + '\n'
        return ret

    def add(self,
            path,  # type: str
            dealer_or_app):
        # type: (...) -> 'Application'
        self.mapping.append((path.strip('/'), dealer_or_app))
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
        if dealer is None or isinstance(dealer, Application):
            print(self._sub_help_doc(path, dealer))
            print()
            return
        if 'h' in dict_params or 'help' in dict_params:
            show_help(dealer)
        else:
            try:
                dealer(*list_params[level:], **dict_params)
            except TypeError as e:
                if str(e).startswith(dealer.__name__ + '() '):
                    show_help(dealer)
                else:
                    raise
            except AssertionError as e:
                print(str(e) + '!\n')
                show_help(dealer)


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
