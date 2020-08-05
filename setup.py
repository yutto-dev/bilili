import os
import sys
from shutil import rmtree

from bilili.__version__ import __version__
from setuptools import setup, find_packages, Command

here = os.path.abspath(os.path.dirname(__file__))

class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(__version__))
        os.system('git push --tags')

        sys.exit()

def get_long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        desc = f.read()
    return desc

setup(
    name='bilili',
    version=__version__,
    description="🍻 bilibili video and danmaku downloader | B站视频、弹幕下载器",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    keywords='python bilibili video download spider danmaku',
    author='SigureMo',
    author_email='sigure.qaq@gmail.com',
    url='https://github.com/SigureMo/bilili',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    python_requires='>=3.6.0',
    setup_requires=[
        'wheel'
    ],
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts':[
            'bilili = bilili.__main__:main'
        ]
    },
    cmdclass={
        'upload': UploadCommand,
    },
)
