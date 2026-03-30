from setuptools import find_packages, setup
from glob import glob


package_name = 'lidar_test'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + "/launch", glob("launch/*")),
        ('share/' + package_name + "/config", glob("config/*")),
        ('share/' + package_name + "/rviz", glob("rviz/*")),

    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='shouvik',
    maintainer_email='shouvik350@gmail.com',
    description='LiDAR test package for RP LiDAR A1m8',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'lidar_subscriber = lidar_test.test_lidar:main',
        ],
    },
)
