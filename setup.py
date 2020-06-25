from setuptools import setup
import os
import platform
import subprocess
from setuptools.command.install import install

try:
    from post_setup import main as post_install
except ImportError:
    post_install = lambda: None


class MyInstall(install):
    def run(self):
        install.run(self)
        post_install()


if platform.system() == 'Windows':
    vboxDest = os.environ.get("VBOX_INSTALL_PATH", None)
    if vboxDest is None:
        raise Exception("No VBOX_INSTALL_PATH defined, exiting")
    old_path = os.getcwd()
    os.chdir(os.path.join(vboxDest, 'sdk', 'install'))
    subprocess.call(['py', '-2', 'vboxapisetup.py', 'install'])
    os.chdir(old_path)

setup(name='mits',
      version='2.0.0',
      description='Testing integration system for Medusa security system',
      url='https://github.com/medusa-team/medusa-testing-environment',
      author='Team Medusa',
      author_email='roderik.ploszek@gmail.com',
      license='MIT',
      packages=['mits'],
      install_requires=['paramiko==1.16.0', 'scp==0.10.2', 'pyyaml'],
      zip_safe=True,
      include_package_data=True,
      cmdclass={'install': MyInstall})
