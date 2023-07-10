#!/usr/bin/env python3

from distutils.core import setup
from sys import version_info

from src.lib import opsconf

suffix = "py{}{}".format(version_info.major, version_info.minor)

setup(name='opsconf-{}'.format(suffix),
      version=opsconf.OPSCONFVERSION,
      description='File-centric Version Control System. Thought for operational data',
      author='Olivier Churlaud',
      author_email='olivier.churlaud@cnes.fr',
      url='https://gitlab.cnes.fr/DNO-OP/opsconf',
      license='MIT',
      package_dir={ '': 'src/lib' },
      packages=['opsconf', 'opsconf.subcommand'],
      scripts=['src/bin/opsconf'],
      data_files=[ ('share/opsconf/githooks', ['src/share/githooks/pre-commit',
                                               'src/share/githooks/post-commit',
                                               'src/share/githooks/commit-msg']
                                               ) ],
     )
