import os
from distutils.command.build import build

from django.core import management
from setuptools import setup, find_packages


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''


class CustomBuild(build):
    def run(self):
        management.call_command('compilemessages', verbosity=1)
        build.run(self)


cmdclass = {
    'build': CustomBuild
}


setup(
    name='pretix-additional-links',
    version='1.2.0',
    description='This is a plugin for `pretix`_ that allows you to add additional Links to the event page.',
    long_description=long_description,
    url='https://github.com/HannesEURESA/pretix-additional-links',
    author='Hannes',
    author_email='hannes@euresa.reisen',

    install_requires=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_additional_links=pretix_additional_links:PretixPluginMeta
""",
)
