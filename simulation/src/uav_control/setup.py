from setuptools import setup
import os

package_name = 'uav_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=['scripts'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@university.edu',
    description='Computer Vision tracking and PID velocity control nodes',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yolo_tracker = scripts.yolo_tracker:main',
            'velocity_pub = scripts.velocity_pub:main'
        ],
    },
)