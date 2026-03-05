from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "prefix", default_value="", description="Prefix for joint/link names"
        ),
        DeclareLaunchArgument(
            "use_sim", default_value="false", description="Use simulation mode"
        ),
        DeclareLaunchArgument(
            "base_only", default_value="true", description="Use the robot base"
        ),
        DeclareLaunchArgument(
            "arm_only", default_value="true", description="Use the robot arm"
        ),
        DeclareLaunchArgument(
            "use_mock_hardware", default_value="true", description="Use mock hardware"
        ),
        DeclareLaunchArgument(
            "mock_sensor_commands",
            default_value="false",
            description="Enable mock sensor commands.",
        ),
        DeclareLaunchArgument(
            "can_port_name",
            default_value="can0",
            description="CAN port name for motor controllers",
        ),
        DeclareLaunchArgument(
            "u2d2_port_name",
            default_value="/dev/ttyUSB0",
            description="U2D2 port name for arm controllers",
        ),
    ]

    prefix = LaunchConfiguration("prefix")
    use_sim = LaunchConfiguration("use_sim")
    base_only = LaunchConfiguration("base_only")
    arm_only = LaunchConfiguration("arm_only")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    mock_sensor_commands = LaunchConfiguration("mock_sensor_commands")
    can_port_name = LaunchConfiguration("can_port_name")
    u2d2_port_name = LaunchConfiguration("u2d2_port_name")

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
            " ",
            "use_sim:=",
            use_sim,
            " ",
            "use_mock_hardware:=",
            use_mock_hardware,
            " ",
            "mock_sensor_commands:=",
            mock_sensor_commands,
            " ",
            "can_port_name:=",
            can_port_name,
            " ",
            "u2d2_port_name:=",
            u2d2_port_name,
        ]
    )

    controller_manager_config = PathJoinSubstitution(
        [FindPackageShare("robot_bringup"), "config", "controller_manager.yaml"]
    )

    rviz_config = PathJoinSubstitution(
        [FindPackageShare("robot_bringup"), "config", "eclipse.rviz"]
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": urdf_file, "use_sim_time": use_sim}],
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{"robot_description": urdf_file}, controller_manager_config],
        output="screen",
    )

    spawner_jsb = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    spawner_diff = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
        condition=IfCondition(base_only),
    )

    spawner_flipper = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "flipper_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
        condition=IfCondition(base_only),
    )

    spawner_arm = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "arm_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
        condition=IfCondition(arm_only),
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
    )

    delay_rviz = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawner_jsb,
            on_exit=[rviz_node],
        )
    )

    ld = LaunchDescription(declared_arguments)
    # nodes
    ld.add_action(robot_state_publisher_node)
    ld.add_action(control_node)

    # spawn order
    ld.add_action(spawner_jsb)
    ld.add_action(spawner_diff)
    ld.add_action(spawner_flipper)
    ld.add_action(spawner_arm)

    # event handler
    ld.add_action(delay_rviz)

    return ld
