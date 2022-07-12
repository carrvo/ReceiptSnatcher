"""CommandLine Interface (CLI) Entry Point.
"""

import argparse
import io
import pdb
import logging
from os import path
import warnings

import receiptsnatcher
from receiptsnatcher import (
    __common__ as common,
    __cmd__ as cmd,
    __gui__ as gui,
)

class StringStream(io.StringIO):
    """
    Helper class for creating a stream to pass to cmd.
    """

    def __init__(self, newline: str = '\n'):
        """
        Initializes.
        :param newline: Character to use to indicate a new line
        """
        super().__init__()
        self.newline = newline

    def writeline(self, text: str or object) -> int:
        """
        Writes a single line to stream.
        :param text: String to write
        :return: Number of bytes written
        """
        return self.write(text+self.newline)

    @property
    def reset(self) -> io.StringIO:
        """
        Resets the position of the stream so that ready for reading.
        :return: self
        """
        self.seek(0, io.SEEK_SET)
        return self

    def seek_from_current(self, offset) -> int:
        """
        Helper function for negative offset.
        See self.seek for underlying functionality.
        :param offset:
        :return:
        """
        return self.seek(self.tell() + offset)

    @property
    def remove_last_character_from_last_line(self) -> None:
        """
        Helper function.
        """
        self.seek_from_current(-2)
        self.writeline('')

    def __del__(self):
        self.close()
        super().__del__()

DESCRIPTION = '\n'.join((
    # CLI
    __doc__.split('\n')[0],
    ''.join(['='] * len(__doc__.split('\n')[0])),
    '',
    # skip the __init__.__doc__ USAGE section
    *receiptsnatcher.__doc__.split('------')[0].split('\n')[2:-2],
))

parser = argparse.ArgumentParser(
    prog=common.APP_DATA.appname,
    description='''
    ''',
    epilog=DESCRIPTION,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

# ARGUMENTS ####
# ========= ####
parser.add_argument(
    '-L',
    '--log-file',
    help='specifies a file to redirect logs to',
    nargs='?',
    type=argparse.FileType(mode='wt', encoding='utf-8'),
    const='%(prog)s.log',
)

log_group = parser.add_mutually_exclusive_group()
log_group.add_argument(
    '-v',
    '--verbosity',
    help='sets the log level',
    dest='log_depth',
    action='count',
    default=0,
)
log_group.add_argument(
    '-D',
    '--log-depth',
    metavar='DEPTH',
    help='sets the log level',
    dest='log_depth',
    type=int,
    default=0,
    choices=range(0, 5),
)

parser.add_argument(
    '-x',
    '-X',
    '--example',
    help='Report an example of using the CLI and exit.'
         ' Accepts the name of an example,'
         ' or "list" for all examples of the subcommand.',
    nargs='?',
    const='list',
)

parser.add_argument(
    '--newline',
    help='specifies the newline character to use',
    type=str,
    default='\n',
    # choices={'\n', '\r', '\r\n'},  # not sure why but breaks -h option...
)

parser.add_argument(
    '--pdb',
    help='start a pdb session before execute commands',
    action='store_true',
)

parser.set_defaults(
    examples={
        'interactive-example': '{} interactive'.format(common.APP_DATA.appname),
        'automate-examples': '{} -x automate'.format(common.APP_DATA.appname),
        'commandline-examples': '{} -x commandline'.format(common.APP_DATA.appname),
    },
)

# SUBCOMMANDS ####
# ----------- ####
subcommands = parser.add_subparsers(
    title='Entry Options',
    description='usage available from the commandline',
    dest='subcommand',
    # required=True,
)

# GUI ####
gui_parser = subcommands.add_parser(
    name='gui',
    help='FUTURE -- starts the GUI',
)

gui_parser.set_defaults(
    func=lambda args: gui.GUI(),
)

# Interactive ####
interactive_parser = subcommands.add_parser(
    name='interactive',
    help='starts an interactive session',
)

interactive_parser.set_defaults(
    func=lambda args: cmd.InteractiveReceiptSnatcher(
        completekey=args.completekey,
        newline=args.newline,
    ),
)

interactive_parser.add_argument(
    '-K',
    '--complete-key',
    metavar='KEY',
    help='passed to interactive session for auto-complete support',
    dest='completekey',
    default='tab',
)

# Automated Configuration File ####
config_parser = subcommands.add_parser(
    name='automate',
    help='automated through a configuration file',
)

config_parser.set_defaults(
    func=lambda args: cmd.InteractiveReceiptSnatcher(
        stdin=args.config,
        newline=args.newline,
    ),
)

config_parser.add_argument(
    'config',
    help='specifies an input file to read commands from'
         ' (default is %(default)s)',
    nargs='?',
    type=argparse.FileType(mode='rt', encoding='utf-8'),
    default=common.APP_DATA.default_config,
)

config_parser.set_defaults(
    examples={
        'default-file': '{} automate'.format(common.APP_DATA.appname),
        'file': '{} automate {}'.format(common.APP_DATA.appname, common.APP_DATA.default_config),
    },
)

# Commandline Configuration ####
commandline_parser = subcommands.add_parser(
    name='commandline',
    help='configuration through commandline arguments',
)

commandline_parser.add_argument(
    '-F',
    '--file',
    help='Store commandline arguments in a file to automate'
         ' -- typically %(const)s',
    nargs='?',
    const=common.APP_DATA.default_config,
)

commandline_parser.set_defaults(
    func=lambda args: cmd.InteractiveReceiptSnatcher(
        stdin=args.common_configuration(
            args,
            args.commandline_configuration(args)
        ).reset,
        newline=args.newline,
    ),
)

# env
def commandline_env_configuration(args: argparse.Namespace) -> StringStream:
    """
    :param args:
    :return:
    """
    stream = StringStream(newline=args.newline)
    stream.writeline('')
    return stream

commandline_env_parser.set_defaults(
    commandline_configuration=commandline_env_configuration,
)

def commandline_configuration(args: argparse.Namespace,
                              stream: StringStream,
                              ) -> StringStream:
    """
    :param args:
    :param stream:
    :return:
    """
    stream.writeline('')
    #
    if args.file:
        try:
            with open(args.file, 'xt', encoding='utf-8') as file:
                file.write(stream.getvalue())
        except IOError as error:
            warnings.warn(error)
    return stream

commandline_parser.set_defaults(
    common_configuration=commandline_configuration,
    examples={
        'env-simple': '{} commandline'
                      ''.format(common.APP_DATA.appname),
    }
)

# Other Options ####
# ------------- ####
# Destroy ####
destroy_parser = subcommands.add_parser(
    name='destroy',
    help='destroys configuration',
)

destroy_parser.set_defaults(
    func=lambda args: cmd.InteractiveReceiptSnatcher(
        stdin=args.destroy_configuration(args).reset,
        newline=args.newline,
    ),
)

# env
def destroy_env_configuration(args: argparse.Namespace) -> StringStream:
    """
    :param args:
    :return:
    """
    stream = StringStream(newline=args.newline)
    stream.writeline('')
    return stream

destroy_libvirt_parser.set_defaults(
    destroy_configuration=destroy_env_configuration,
    examples={
        'env-simple': '{} destroy'
                           ''.format(common.APP_DATA.appname),
    },
)

# ####
def run(args: argparse.Namespace) -> None:
    """
    :param args:
    :return:
    """
    # logging
    if args.log_depth > 4:
        args.log_depth = 4
    logging.basicConfig(
        filename=args.log_file,
        level=(
            common.WARNING,
            common.CONFIGURATION,
            common.INFO,
            common.DEBUG,
            common.TRACE,
        )[args.log_depth],
    )
    # examples
    if args.example:
        if args.example == 'list':
            for name, example in args.examples.items():
                print(name)
                print(''.join(['-']*len(name)))
                print(example)
        else:
            print(args.examples.get(args.example, 'Not Found!'))
        return
    # subcommands
    session = args.func(args)
    if args.pdb:
        pdb.set_trace()
        pass  # set breakpoints before execution
    if args.subcommand == 'gui':
        raise NotImplementedError('Advanced Feature!')
    else:
        session.cmdloop()

if __name__ == '__main__':
    run(parser.parse_args())
