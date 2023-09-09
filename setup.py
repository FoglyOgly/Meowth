from setuptools import setup

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
    name='Meowth',
    version='3.0.0b',
    author='FoglyOgly, Scragly',
    url='https://github.com/FoglyOgly/Meowth',
    license='GPLv3',
    description='A Discord Bot for Pokemon Go Communities.',
    long_description=readme,
    include_package_data=True,

    install_requires=requirements,

    # this will be dead next month with the new pip version
    dependency_links=[
        'discord.py @ '
        'https://github.com/Rapptz/discord.py@rewrite#egg=discord.py-1'
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Communications :: Chat',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='pokemon pokemongo community discord bot',

    entry_points={
        'console_scripts': [
            'meowth=meowth.launcher:main',
            'meowth-bot=meowth.__main__:main'
        ],
    },
)
