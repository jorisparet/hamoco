import os
import glob
from setuptools import setup

with open('README.md', 'r') as fh:
    readme = fh.read()

with open('hamoco/core/_version.py') as f:
    exec(f.read())
    
args = dict(name='hamoco',
            version=__version__,
            description='Mouse control via webcam-recorded hand gestures',
            long_description=readme,
            long_description_content_type='text/markdown',
            author='Joris Paret',
            author_email='joris.paret@gmail.com',
            maintainer='Joris Paret',
            url='https://github.com/jorisparet/hamoco',
            keywords=['mouse', 'controller', 'webcam', 'hand',
                      'deep learning', 'neural network'],
            packages=['hamoco',
                      'hamoco/cli',
                      'hamoco/config',
                      'hamoco/core',
                      'hamoco/models',
                      'hamoco/utils'],
            include_package_data=True,
            entry_points={'console_scripts':
                          ['hamoco-run = hamoco.cli.hamoco_run:main',
                           'hamoco-data = hamoco.cli.hamoco_data:main',
                           'hamoco-train = hamoco.cli.hamoco_train:main']},
            install_requires=['pyautogui', 'numpy', 'opencv-python', 'mediapipe', 'tensorflow'],
            license='GPLv3',
            classifiers=[
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Development Status :: 5 - Production/Stable',
                'Topic :: Scientific/Engineering :: Human Machine Interfaces',
                'Topic :: Scientific/Engineering :: Image Recognition',
                'Programming Language :: Python :: 3',
                'Operating System :: POSIX :: Linux',
                'Operating System :: Microsoft :: Windows',
                'Intended Audience :: End Users/Desktop',
                'Natural Language :: English']
)

setup(**args)
