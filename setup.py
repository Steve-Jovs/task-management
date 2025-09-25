from setuptools import setup, find_packages

setup(
    name="task_manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyMySQL>=1.0.0",
        "python-dateutil>=2.8.0"
    ],
    entry_points={
        'console_scripts': [
            'task-manager=src.cli:main',
        ],
    },
    python_requires='>=3.8',
)