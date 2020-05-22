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

setup(name='mte',
      version='0.1.0',
      description='Testing environment for Medusa security system',
      url='https://github.com/Programator2/medusa-testing-environment',
      author='Roderik Ploszek',
      author_email='roderik.ploszek@gmail.com',
      license='MIT',
      packages=['mte'],
      install_requires=['paramiko==1.16.0', 'scp==0.10.2'],
      zip_safe=True,
      include_package_data=True,
      cmdclass={'install': MyInstall})
