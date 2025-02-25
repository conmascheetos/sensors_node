import os

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    PathJoinSubstitution,
)


def generate_launch_description():
    pkg_simulator = get_package_share_directory("simulator")

    # bridge for ros 2 <---> gazebo
    bridge_params: str = os.path.join(
        pkg_simulator,
        "params",
        "bridge.yaml",
    )
    imu_bridge: Node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "--ros-args",
            "-p",
            f"config_file:={bridge_params}",
        ],
        output="screen",
    )

    # a custom bridge to use our message types.
    #
    # yea... it's goin through three layers lol
    soro_bridge: Node = Node(package="simulator", executable="simulator")

    # spawn the gazebo server
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    gz_launch_path = PathJoinSubstitution(
        [pkg_ros_gz_sim, "launch", "gz_sim.launch.py"]
    )
    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch_path),
        launch_arguments={
            "gz_args": [
                PathJoinSubstitution(
                    [pkg_simulator, "resource", "world.sdf.xml"]
                ),
            ],
            "on_exit_shutdown": "True",
        }.items(),
    )

    # make an instance of the navigator node!
    navigator: Node = Node(
        executable="navigator_node",
        package="navigator_node",
        name="navigator",
        # parameters=[
        #     {
        #         "navigator_parameters": LaunchConfiguration(
        #             "navigator_parameters"
        #         )
        #     }
        # ],
    )

    return LaunchDescription(
        [imu_bridge, navigator, gz_server, soro_bridge],
    )
