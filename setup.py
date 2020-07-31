from setuptools import setup, find_packages

VERSION = '0.0.9'

def get_long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        desc = f.read()
    return desc

setup(
    name='bilili',
    version=VERSION,
    description=":beers: bilibili video and danmaku downloader | B站视频、弹幕下载器",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
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
    install_requires=[
        'requests',
        'opencv-python'
    ],
    entry_points={
        'console_scripts':[
            'bilili = bilili.bilili_dl:main'
        ]
    },
)
