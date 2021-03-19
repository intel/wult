Use the 'argparse-manpage' tool to generate man pages. It can be
installed with 'pip' or from the OS package. For example, Fedora comes
with the 'python3-argparse-manpage' package.

Change directory to 'wult' git repository clone directrory. To build
'wult' tool man page, run:

  argparse-manpage --pyfile ./wult --function build_arguments_parser \
                   --project-name 'wult' --author 'Artem Bityutskiy' \
		   --author-email 'dedekind1@gmail.com' \
		   --output docs/man1/wult.1

To build 'ndl' tool man page, run:

  argparse-manpage --pyfile ./ndl --function build_arguments_parser \
                   --project-name 'wult' --author 'Artem Bityutskiy' \
		   --author-email 'dedekind1@gmail.com' \
		   --output docs/man1/ndl.1
