from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    prefix = LaunchConfiguration("prefix")
    use_gui = LaunchConfiguration("use_gui")

    urdf_file = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("robot_description"), "urdf", "eclipse.xacro"]
            ),
            " ",
            "prefix:=",
            prefix,
        ]
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("robot_description"), "config", "eclipse.rviz"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "prefix",
                default_value="",
                description="prefix of the joint and link names",
            ),
            DeclareLaunchArgument(
                "use_gui",
                default_value="true",
                description="Run joint state publisher gui node",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": urdf_file}],
                output="screen",
            ),
            Node(
                package="joint_state_publisher_gui",
                executable="joint_state_publisher_gui",
                parameters=[{"robot_description": urdf_file}],
                condition=IfCondition(use_gui),
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                arguments=["-d", rviz_config_file],
                output="screen",
            ),
        ]
    )
