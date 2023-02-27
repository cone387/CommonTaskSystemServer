from setuptools import setup, find_packages

setup(
    name='common-task-system-server',
    packages=find_packages(exclude=['local_tests']),
    version='1.0.1',
    install_requires=[
        "django>=3.2.18",
        "croniter>=1.3.8",
        "djangorestframework>=3.14.0",
        "PyMySQL>=1.0.2"
    ],
    # extras_require={
    # },
    author='cone387',
    maintainer_email='1183008540@qq.com',
    license='MIT',
    url='https://github.com/cone387/CommonTaskSystemServer',
    python_requires='>=3.7, <4',
)