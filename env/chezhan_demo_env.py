import os
import subprocess
import json
import sys
import time
# import paramiko

WORK_PATH = "./"

# IC_USER = "aaa"

# IC_PASSWORD = "Vlm@1234"  # 工控机登陆密码
# AVSPEECH_IP = "10.64.134.23"  # 10.103.134.13 语音Pac板IP地址
# VP_IP = "10.64.134.22"  # 10.103.134.12 VP Pac板IP地址
# VG_IP = "10.64.134.24"  # 10.103.134.11 VG Pac板IP地址
# IC_IP = "10.64.134.112"  # "10.64.134.112"  # 10.103.134.10 工控机IP地址
# PAD_NET_IP = "10.64.134.72/24"  # 10.103.134.47/24 PAD有线IP

# IC_PASSWORD = "haloBJbench01"  # 工控机登陆密码
AVSPEECH_IP = "10.103.134.13"  # 语音Pac板IP地址
VP_IP = "10.103.134.12"  # VP Pac板IP地址
VG_IP = "10.103.134.11"  # VG Pac板IP地址
IC_IP = "10.103.134.10"  # 工控机IP地址
PAD_NET_IP = "10.103.134.47/24"  # PAD有线IP

AVSPEECH_RUN_PATH = "/mnt/halo/"  # 语音感知运行路径
VP_RUN_PATH = "/mnt/halo/"  # VP感知运行路径
VG_RUN_PATH = "/mnt/halo/"  # VG感知运行路径
# IC_RUN_PATH = "/home/" + IC_USER + "/vlm_workspace/"  # 工控机运行路径

VLM_SRC_RUN_PATH = "src/"
ROS2_BRIDGE_RUN_PATH = "ros2bridge/ros2_bridge/"
CUT_SCREEN_RUN_PATH = "cut_screen/"
YOLO_RUN_PATH = "yolo-world/"
IC_VG_RUN_PATH = "visual_grounding/modelscope-agent/"

VERSION_DICT = dict()
IP_DICT = dict()
RUN_PATH_DICT = dict()

KEY_AVSPEECH = "DEMO-Develop"  # AIMateSpeech感知软件包关键字
KEY_VP = "app_vp"  # VP感知软件包关键字
KEY_VG = "app_vg"  # VG感知软件包关键字
KEY_AIAGENT = "melo"  # AIAgent quick build包关键字
KEY_VP_APK = "VisionPro"  # VP APK 关键字
KEY_ROS_BRIDGE = "ros2bridge"  # ros 2 bridge 关键字
KEY_VLM_SRC = "vlm_src"  # vlm src 关键字
KEY_CUT_SCREEN = "cut_screen"  # cut screen 关键字
KEY_IC = "Ic"  # 工控机关键字

AIAGENT_CONF_PATH = "/data/user/0/com.gua.car.speech/files/perception/"
VP_APK_CONF_PATH = "/mnt/user/10/emulated/10/Android/data/com.gua.halo.vision.pro/files/perception/"
PAD_CONF_FILE = "commu_config.json"

ROS2_BRIDGE_CONF_PATH = "ros2bridge/ros2_bridge/etc/"
VLM_SRC_CONF_PATH = "src/front_vision_unit/vlm_process/vlm_process/"

PAC_COMMU_CONF_FILE = "communication_all.json"
ROS2_BRIDGE_COMMU_CONF_FILE = "communication.json"
VLM_SRM_CONF_FILE = "vlm_node.json"

def run_shell_cmd(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output)

    process.wait(5000)

    return process.returncode


def get_file_path(root_path, target_file_key):
    target_file_path = ""

    for root, dirs, files in os.walk(root_path):
        for file in files:
            if target_file_key in file:
                target_file_path = os.path.join(root, file)
                break

    return target_file_path


def restart_pac_perception(env_type):
    print("now restart....")

    cmd = f"ssh root@{IP_DICT[env_type]} \"chmod -R 777 {RUN_PATH_DICT[env_type]}/../*\""
    print(cmd)
    run_shell_cmd(cmd)

    cmd = f"ssh root@{IP_DICT[env_type]} \"/sbin/reboot &\""
    print(cmd)
    run_shell_cmd(cmd)

def flash_pac_env(env_type):
    cmd = f"scp {WORK_PATH}/{VERSION_DICT[env_type]} root@{IP_DICT[env_type]}:/userdata/"
    print(cmd)
    run_shell_cmd(cmd)

    cmd = f"ssh root@{IP_DICT[env_type]} otaupdate app /userdata/{VERSION_DICT[env_type]}"
    print(cmd)
    run_shell_cmd(cmd)

    if KEY_AVSPEECH == env_type or KEY_VG == env_type:
        modify_commu_conf(env_type)

    if KEY_AVSPEECH == env_type:
        cmd = f"scp root@{IP_DICT[env_type]}:{RUN_PATH_DICT[env_type]}/etc/hr_timesync.cfg {WORK_PATH}"
        run_shell_cmd(cmd)

        with open(WORK_PATH + '/hr_timesync.cfg', 'r') as ts_f:
            lines = ts_f.readlines()

        with open(WORK_PATH + '/hr_timesync.cfg', 'w') as ts_f:
            for line in lines:
                if line.startswith("NET_IP"):
                    line = line.replace("*", VG_IP)
                ts_f.write(line)

        cmd = f"scp {WORK_PATH}/hr_timesync.cfg root@{IP_DICT[env_type]}:{RUN_PATH_DICT[env_type]}/etc/"
        run_shell_cmd(cmd)
        cmd = f"rm {WORK_PATH}/hr_timesync.cfg"
        run_shell_cmd(cmd)

        cmd = f"scp root@{IP_DICT[env_type]}:{RUN_PATH_DICT[env_type]}/etc/car_type/DemoCar_config/AudioInputModule.json {WORK_PATH}"
        run_shell_cmd(cmd)

        with open(WORK_PATH + "/AudioInputModule.json", 'r') as f:
            audio_input_conf = json.load(f)

        audio_input_conf["device"] = 1
        audio_input_conf["enable_hb_pcm_interface"] = 0

        audio_input_conf["seat_map_to_record_channel"]["FL"] = 5
        audio_input_conf["seat_map_to_record_channel"]["FR"] = 6
        audio_input_conf["seat_map_to_record_channel"]["BL"] = 7
        audio_input_conf["seat_map_to_record_channel"]["BR"] = 8

        with open(WORK_PATH + "/AudioInputModule.json", 'w', newline='\n') as f:
            json.dump(audio_input_conf, f, indent=4)

        cmd = f"scp {WORK_PATH}/AudioInputModule.json root@{IP_DICT[env_type]}:{RUN_PATH_DICT[env_type]}/etc/car_type/DemoCar_config"
        run_shell_cmd(cmd)
        cmd = f"rm {WORK_PATH}/AudioInputModule.json"
        run_shell_cmd(cmd)

    restart_pac_perception(env_type)

def wait_android_device():
    print("now wait android devices...")
    time.sleep(45)
    # cmd = "adb devices"
    #
    # while True:
    #     time.sleep(1)
    #     process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
    #
    #     need_ret = False
    #     while True:
    #         output = process.stdout.readline()
    #         if output == '' and process.poll() is not None:
    #             break
    #         if output:
    #             print(output)
    #             output_split = output.strip().split()
    #             if 0 != len(output_split) and "device" == output_split[-1]:
    #                 need_ret = True
    #
    #     if need_ret:
    #         break
    return


def replace_commu_ip(commu_file_name, env_type):
    with open(commu_file_name, 'r') as f:
        commu_conf = json.load(f)

    for participant in commu_conf["participants"]:
        link_info = participant["link_info"].strip().split(":")
        if env_type == KEY_AIAGENT:
            if len(link_info[0].strip().split(".")) == 4:
                participant["link_info"] = AVSPEECH_IP + ":" + link_info[-1]
        elif env_type == KEY_VP_APK:
            if participant["id"] == 101 or participant["id"] == 102 or participant["id"] == 201:
                participant["link_info"] = VG_IP + ":" + link_info[-1]
            elif participant["id"] == 105:
                participant["link_info"] = AVSPEECH_IP + ":" + link_info[-1]
            elif participant["id"] == 107 or participant["id"] == 109 or participant["id"] == 206:
                participant["link_info"] = VP_IP + ":" + link_info[-1]
        if env_type == KEY_AVSPEECH:
            if participant["id"] == 260 or participant["id"] == 516:
                participant["link_info"] = VG_IP + ":" + link_info[-1]
        if env_type == KEY_VG:
            if participant["id"] == 260 or participant["id"] == 516:
                participant["link_info"] = "0.0.0.0:" + link_info[-1]
        if env_type == KEY_ROS_BRIDGE:
            if participant["id"] == 1 or participant["id"] == 2 or participant["id"] == 3:
                participant["link_info"] = VG_IP + ":" + link_info[-1]

    with open(commu_file_name, 'w', newline='\n') as f:
        json.dump(commu_conf, f, indent=4)


def modify_commu_conf(env_type):
    conf_path = ''
    commu_file = ''
    cmd = ''

    # 拉取配置文件
    if env_type == KEY_AIAGENT:
        conf_path = AIAGENT_CONF_PATH
        commu_file = PAD_CONF_FILE
        cmd = "adb pull " + conf_path + "/" + commu_file + " " + WORK_PATH
    elif env_type == KEY_VP_APK:
        conf_path = VP_APK_CONF_PATH
        commu_file = PAD_CONF_FILE
        cmd = "adb pull " + conf_path + "/" + commu_file + " " + WORK_PATH
    elif env_type == KEY_AVSPEECH:
        conf_path = AVSPEECH_RUN_PATH
        commu_file = PAC_COMMU_CONF_FILE
        cmd = f"scp root@{AVSPEECH_IP}:{conf_path}/etc/{commu_file} {WORK_PATH}"
    elif env_type == KEY_VG:
        conf_path = VG_RUN_PATH
        commu_file = PAC_COMMU_CONF_FILE
        cmd = f"scp root@{VG_IP}:{conf_path}/etc/{commu_file} {WORK_PATH}"
    # elif env_type == KEY_ROS_BRIDGE:
    #     conf_path = IC_RUN_PATH + "/" + ROS2_BRIDGE_CONF_PATH
    #     commu_file = ROS2_BRIDGE_COMMU_CONF_FILE
    #     cmd = f"scp root@{IC_IP}:{conf_path}/{commu_file} {WORK_PATH}"

    print(cmd)
    run_shell_cmd(cmd)

    # 修改配置文件
    commu_file_name = WORK_PATH + '/' + commu_file
    replace_commu_ip(commu_file_name, env_type)

    # 替换配置文件
    if env_type == KEY_AIAGENT or env_type == KEY_VP_APK:
        cmd = "adb push " + WORK_PATH + "/" + commu_file + " " + conf_path
    elif env_type == KEY_AVSPEECH:
        cmd = f"scp {WORK_PATH}/{commu_file} root@{AVSPEECH_IP}:{conf_path}/etc/"
    elif env_type == KEY_VG:
        cmd = f"scp {WORK_PATH}/{commu_file} root@{VG_IP}:{conf_path}/etc/"
    elif env_type == KEY_ROS_BRIDGE:
        cmd = f"scp {WORK_PATH}/{commu_file} root@{IC_IP}:{conf_path}/"

    print(cmd)
    run_shell_cmd(cmd)

    cmd = "rm " + WORK_PATH + "/" + commu_file
    run_shell_cmd(cmd)


def flash_pad_env():
    # AI Agent刷机
    cmd = "tar -zxvf " + WORK_PATH + "/" + VERSION_DICT[KEY_AIAGENT] + " -C" + WORK_PATH
    print(cmd)
    run_shell_cmd(cmd)

    flash_file_path = get_file_path(WORK_PATH, "flash_all.sh")
    print("flash_file_path is " + str(flash_file_path))

    cmd = "adb root"
    run_shell_cmd(cmd)
    cmd = "adb remount"
    run_shell_cmd(cmd)

    cmd = "bash " + str(flash_file_path)
    print("now flashing pad.....")
    run_shell_cmd(cmd)

    wait_android_device()

    cmd = "adb root"
    run_shell_cmd(cmd)
    cmd = "adb remount"
    run_shell_cmd(cmd)

    cmd = "adb shell setprop persist.gua.eth0.ipaddress " + PAD_NET_IP
    run_shell_cmd(cmd)

    # AI Agent配置文件修改
    print("now modify ai agent config")
    modify_commu_conf(KEY_AIAGENT)
    cmd = "rm -rf " + WORK_PATH + "/" + VERSION_DICT[KEY_AIAGENT].strip().split(".")[0]
    run_shell_cmd(cmd)

    # 安装version pro apk
    print("now install version pro apk")
    cmd = "adb install -r -t -d " + WORK_PATH + "/" + VERSION_DICT[KEY_VP_APK]
    run_shell_cmd(cmd)

    print("now modify version pro apk config")
    cmd = "adb shell am startservice -n com.gua.halo.vision.pro/com.gua.halo.aimate.AiService"
    run_shell_cmd(cmd)
    time.sleep(2)

    modify_commu_conf(KEY_VP_APK)

    cmd = "adb reboot"
    run_shell_cmd(cmd)

    time.sleep(45)

    cmd = "adb tcpip 5555"
    run_shell_cmd(cmd)


def get_version_files():
    print("now parse version file")
    files = os.listdir(WORK_PATH)

    for file in files:
        if KEY_AVSPEECH in file:
            VERSION_DICT[KEY_AVSPEECH] = file
        elif KEY_VP in file:
            VERSION_DICT[KEY_VP] = file
        elif KEY_VG in file:
            VERSION_DICT[KEY_VG] = file
        elif KEY_AIAGENT in file:
            VERSION_DICT[KEY_AIAGENT] = file
        elif KEY_VP_APK in file:
            VERSION_DICT[KEY_VP_APK] = file
        elif KEY_ROS_BRIDGE in file:
            VERSION_DICT[KEY_ROS_BRIDGE] = file
        elif KEY_VLM_SRC in file:
            VERSION_DICT[KEY_VLM_SRC] = file
        elif KEY_CUT_SCREEN in file:
            VERSION_DICT[KEY_CUT_SCREEN] = file

    print("now parse version file done ")
    print(VERSION_DICT)


def init():
    print("init ip")
    IP_DICT[KEY_AVSPEECH] = AVSPEECH_IP
    IP_DICT[KEY_VG] = VG_IP
    IP_DICT[KEY_VP] = VP_IP
    IP_DICT[KEY_IC] = IC_IP
    IP_DICT[KEY_VLM_SRC] = IC_IP
    IP_DICT[KEY_ROS_BRIDGE] = IC_IP

    print("init run path")
    RUN_PATH_DICT[KEY_AVSPEECH] = AVSPEECH_RUN_PATH
    RUN_PATH_DICT[KEY_VG] = VG_RUN_PATH
    RUN_PATH_DICT[KEY_VP] = VP_RUN_PATH
    # RUN_PATH_DICT[KEY_IC] = IC_RUN_PATH


def copy_unzip(ssh, sftp, ic_env_type):
    sftp.put(VERSION_DICT[ic_env_type], RUN_PATH_DICT[KEY_IC] + "/" + VERSION_DICT[ic_env_type])
    cmd = f"unzip {RUN_PATH_DICT[KEY_IC]}/{VERSION_DICT[ic_env_type]} -d {RUN_PATH_DICT[KEY_IC]}/"
    run_ssh_cmd(ssh, cmd)
    cmd = f"rm {RUN_PATH_DICT[KEY_IC]}/{VERSION_DICT[ic_env_type]}"
    run_ssh_cmd(ssh, cmd)


# def start_vlm():
#     # cmd = f"cd {RUN_PATH_DICT[KEY_IC]}/{YOLO_RUN_PATH} ; sh run_demo.sh"
#     # run_shell_cmd(cmd)
#     #
#     # cmd = f"cd {RUN_PATH_DICT[KEY_IC]}/{IC_VG_RUN_PATH} ; sh run_api.sh"
#     # run_shell_cmd(cmd)
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(hostname=IP_DICT[KEY_IC], username=IC_USER, password=IC_PASSWORD)
#
#     cmd = f"cd {RUN_PATH_DICT[KEY_IC]}/{ROS2_BRIDGE_RUN_PATH} ; chmod -R 777 * ; sh run.sh &"
#     run_ssh_cmd(ssh, cmd)
#
#     cmd = f"cd {RUN_PATH_DICT[KEY_IC]}/{VLM_SRC_RUN_PATH} ; chmod -R 777 * ; sh run_ros2_pkg.sh &"
#     run_ssh_cmd(ssh, cmd)
#
#     cmd = f"cd {RUN_PATH_DICT[KEY_IC]}/{CUT_SCREEN_RUN_PATH} ; chmod -R 777 * ; sh run_pad_llm.sh &；sh run_cut_screen.sh &"
#     run_ssh_cmd(ssh, cmd)
#
#     ssh.close()


def run_ssh_cmd(ssh, cmd):
    print(cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode('utf-8')
    print(result)


def modify_ic_conf(sftp, env_type):
    local_conf = ""
    remote_conf = ""

    if KEY_ROS_BRIDGE == env_type:
        local_conf = WORK_PATH + "/" + ROS2_BRIDGE_COMMU_CONF_FILE
        remote_conf = RUN_PATH_DICT[KEY_IC] + "/" + ROS2_BRIDGE_CONF_PATH + "/" + ROS2_BRIDGE_COMMU_CONF_FILE
    elif KEY_VLM_SRC == env_type:
        local_conf = WORK_PATH + "/" + VLM_SRM_CONF_FILE
        remote_conf = RUN_PATH_DICT[KEY_IC] + "/" + VLM_SRC_CONF_PATH + "/" + VLM_SRM_CONF_FILE

    sftp.get(remote_conf, local_conf)

    if KEY_ROS_BRIDGE == env_type:
        replace_commu_ip(local_conf, env_type)
    if KEY_VLM_SRC == env_type:
        vlm_node_file_name = local_conf
        with open(vlm_node_file_name, 'r') as f:
            vlm_node_conf = json.load(f)

        vlm_node_conf["vlm_ip"] = IP_DICT[KEY_IC]

        with open(vlm_node_file_name, 'w', newline='\n') as f:
            json.dump(vlm_node_conf, f, indent=4)

    sftp.put(local_conf, remote_conf)

    cmd = f"rm {local_conf}"
    run_shell_cmd(cmd)


# def flash_ic_env():
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(hostname=IP_DICT[KEY_IC], username=IC_USER, password=IC_PASSWORD)
#
#     # cmd = f"mkdir -p {RUN_PATH_DICT[KEY_IC]}"
#     # run_ssh_cmd(ssh, cmd)
#
#     sftp = ssh.open_sftp()
#
#     # copy_unzip(ssh, sftp, KEY_ROS_BRIDGE)
#     # copy_unzip(ssh, sftp, KEY_VLM_SRC)
#     # copy_unzip(ssh, sftp, KEY_CUT_SCREEN)
#
#     # modify_ic_conf(sftp, KEY_ROS_BRIDGE)
#     # modify_ic_conf(sftp, KEY_VLM_SRC)
#
#     sftp.close()
#     ssh.close()
#
#     start_vlm()


def flash_demo_env():
    get_version_files()

    print(">>>>>>>>>>>>>now flash pad<<<<<<<<<<<<<<<<")
    flash_pad_env()
    print(">>>>>>>>>>>>>now pad ready<<<<<<<<<<<<<<<<")

    print(">>>>>>>>>>>>>now flash avspeecch pac<<<<<<<<<<<<<<<<")
    flash_pac_env(KEY_AVSPEECH)
    print(">>>>>>>>>>>>>now avspeecch pac ready<<<<<<<<<<<<<<<<")

    print(">>>>>>>>>>>>>now flash VP pac<<<<<<<<<<<<<<<<")
    flash_pac_env(KEY_VP)
    print(">>>>>>>>>>>>>now VP pac ready<<<<<<<<<<<<<<<<")

    print(">>>>>>>>>>>>>now flash VG pac<<<<<<<<<<<<<<<<")
    flash_pac_env(KEY_VG)
    print(">>>>>>>>>>>>>now avspeecch VG ready<<<<<<<<<<<<<<<<")

    # print(">>>>>>>>>>>>>now flash IC pac<<<<<<<<<<<<<<<<")
    # flash_ic_env()
    # print(">>>>>>>>>>>>>now avspeecch IC ready<<<<<<<<<<<<<<<<")

    time.sleep(3)

    print(">>>>>>>>>>>>>now demo all env ready<<<<<<<<<<<<<<<<")


def reset():
    print(">>>>>>>>>>>>>now reset demo env<<<<<<<<<<<<<<<<")
    modify_commu_conf(KEY_AVSPEECH)
    restart_pac_perception(KEY_AVSPEECH)

    modify_commu_conf(KEY_VG)
    restart_pac_perception(KEY_VG)

    restart_pac_perception(KEY_VP)

    modify_commu_conf(KEY_AIAGENT)
    modify_commu_conf(KEY_VP_APK)
    cmd = "adb reboot"
    run_shell_cmd(cmd)

    time.sleep(45)

    cmd = "adb root"
    run_shell_cmd(cmd)
    cmd = "adb remount"
    run_shell_cmd(cmd)

    cmd = "adb tcpip 5555"
    run_shell_cmd(cmd)

    # kill_vlm()
    # start_vlm()
    # time.sleep(3)
    print(">>>>>>>>>>>>>now reset demo finish<<<<<<<<<<<<<<<<")


def main(cmd):
    init()

    print(cmd)

    if "flash" == cmd:
        flash_demo_env()
    elif "reset" == cmd:
        reset()
    else:
        print("please use python chezhan_demo_env.py [flash|reset]")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("please use python chezhan_demo_env.py [flash|reset]")
        exit()

    main(sys.argv[1])
