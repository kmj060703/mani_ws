import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    robot_desc_share = FindPackageShare("robot_description")
    robot_bringup_share = FindPackageShare("robot_bringup")
    prefix = LaunchConfiguration("prefix")
    
    # URDF 문자열이 YAML로 파싱되는 것을 방지하기 위해 ParameterValue로 감쌉니다.
    follower_urdf_file = ParameterValue(Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ", PathJoinSubstitution([robot_desc_share, "urdf", "eclipse.xacro"]),
        " ", "prefix:=", prefix, " ", "u2d2_port_name:=/dev/USBfollower",
    ]), value_type=str)

    follower_controllers = PathJoinSubstitution([robot_bringup_share, "config", "controller_manager.yaml"])

    return LaunchDescription([
        DeclareLaunchArgument("prefix", default_value=""),
        
        GroupAction(
            actions=[
                # Follower Hardware & Control
                Node(
                    package="controller_manager",
                    executable="ros2_control_node",
                    parameters=[{'robot_description': follower_urdf_file}, follower_controllers],
                    output='screen',
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["arm_controller", "--controller-manager", "/controller_manager"],
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["gripper_controller", "--controller-manager", "/controller_manager"],
                ),
                
                # Robot State Publisher
                Node(
                    package='robot_state_publisher',
                    executable='robot_state_publisher',
                    name='follower_state_publisher',
                    output='screen',
                    parameters=[{'robot_description': follower_urdf_file}],
                    remappings=[('joint_states', '/joint_states')]
                ),
            ]
        ),
        
        # Static TF
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'world', 'base_link']
        )
    ])