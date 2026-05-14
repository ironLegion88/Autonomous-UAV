import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # Paths to Gazebo and Drone models
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_uav_desc = get_package_share_directory('uav_description')
    
    drone_sdf_path = os.path.join(pkg_uav_desc, 'urdf', 'drone.sdf')

    # 1. Launch Gazebo Harmonic (Ignition) with a default empty world
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # 2. Spawn the custom 6-inch drone into the Gazebo world
    spawn_drone = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', drone_sdf_path,
            '-name', 'endurance_quadcopter',
            '-x', '0.0', '-y', '0.0', '-z', '0.2'
        ],
        output='screen'
    )

    # 3. Bridge the Gazebo Camera topic to ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image'],
        output='screen'
    )

    # 4. Start MAVROS to connect ArduPilot SITL to ROS 2
    mavros_node = Node(
        package='mavros',
        executable='mavros_node',
        parameters=[{'fcu_url': 'udp://127.0.0.1:14550@14555'}],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        spawn_drone,
        bridge,
        mavros_node
    ])