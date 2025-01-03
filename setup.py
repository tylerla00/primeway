from setuptools import setup, find_packages

setup(
    name='primeway',
    version='0.1',
    packages=find_packages(),
    scripts=['primeway/cli/entry.py'],  # Point to your script
    install_requires=[
        'click',
        'pyyaml',
        'requests',
        'tabulate',
        'sseclient-py',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'primeway=primeway.cli.entry:primeway_cli',
        ],
    },
)
