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
            author='Joris Paret',
            author_email='joris.paret@gmail.com',
            packages=['hamoco',
                      'hamoco/core',
                      'hamoco/models'],
            include_package_data=True,
            scripts=glob.glob(os.path.join('bin', 'hamoco-*')),
            install_requires=['pyautogui', 'numpy', 'opencv-python', 'mediapipe', 'keras'],
            license='GPLv3',
            classifiers=[
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Development Status :: 3 - Alpha',
                'Topic :: Scientific/Engineering :: Human Machine Interfaces',
                'Topic :: Scientific/Engineering :: Image Recognition',
                'Programming Language :: Python :: 3']
)

setup(**args)
