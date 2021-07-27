import optparse
from lesscli import Application, add_option


if __name__ == '__main__?':
    parser = optparse.OptionParser(usage='usage: %prog [options] arg1 arg2')
    parser.add_option('--start', dest='verbose', help='')
    parser.add_option('--end', type='int', help='write output to FILE')
    # parser.print_help()
    (options, args) = parser.parse_args()
    print(options)
    print(args)


@add_option('file', short='-f', help='read data from FILENAME')
@add_option('verbose', short='-v', type='bool', help='make lots of noise')
def start(*args, **kwargs):
    """
    开始运行
    scaffold.py start [options] args...
    """
    print(args)
    print(kwargs)
    assert kwargs['verbose'], 'verbose cannot be empty'


if __name__ == '__main__':
    Application('my tool').add('start', start).run()
