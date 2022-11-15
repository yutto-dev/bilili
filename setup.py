import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

BILILI_VERSION = "1.4.13"

here = os.path.abspath(os.path.dirname(__file__))


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(BILILI_VERSION))
        os.system("git push --tags")

        sys.exit()


def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        desc = f.read()
    return desc


setup(
    name="bilili",
    version=BILILI_VERSION,
    description="🍻 bilibili video and danmaku downloader | B站视频、弹幕下载器",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Environment :: Console",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords="python bilibili video download spider danmaku",
    author="Nyakku Shigure",
    author_email="sigure.qaq@gmail.com",
    url="https://github.com/yutto-dev/bilili",
    license="GPLv3",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    python_requires=">=3.8.0",
    setup_requires=["wheel"],
    install_requires=["requests", "biliass==1.3.7"],
    entry_points={"console_scripts": ["bilili = bilili.__main__:main"]},
    cmdclass={
        "upload": UploadCommand,
    },
)
