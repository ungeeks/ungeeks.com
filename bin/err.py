import sys


def errline(line_num, line, err_msg):
    msg1 = 'error: line {}: {}'.format(line_num, line)
    msg2 = 'error: {}'.format(err_msg)
    print(msg1, file=sys.stderr)
    print(msg2, file=sys.stderr)
    sys.exit(1)


def err(msg):
    print('error: ' + msg, file=sys.stderr)
    sys.exit(1)


def log(*msg):
    print(' '.join(msg), file=sys.stderr)
