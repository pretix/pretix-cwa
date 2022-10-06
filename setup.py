import os
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

from pretix_cwa import __version__


try:
    with open(
        os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except Exception:
    long_description = ""


class CustomBuild(build):
    def run(self):
        management.call_command("compilemessages", verbosity=1)
        build.run(self)


cmdclass = {"build": CustomBuild}


setup(
    name="pretix-cwa",
    version=__version__,
    description="pretix integration for the Corona Warn App (CWA)",
    long_description=long_description,
    url="https://github.com/pretix/pretix-cwa",
    author="pretix team",
    author_email="support@pretix.eu",
    license="Apache",
    install_requires=[
        "qrcode",
        "cwa-qr>=1.2.2",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_cwa=pretix_cwa:PretixPluginMeta
""",
)
