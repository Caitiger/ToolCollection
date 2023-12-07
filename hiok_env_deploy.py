import os
import subprocess
import json
import time
import zipfile
import shutil

WORK_PATH = "./"

J5_IP = "192.168.1.10"

KEY_KARAOKE_APP = "Karaoke"
KILL_KARAOKE_NAME = "com.changba.sd"

# KEY_KARAOKE_APP = "changba"
# KILL_KARAOKE_NAME = "com.tencent.wecar.karaoke"

BSP_VERSION = "Halo5-BSP-1.0.12_Release"
BSP_VERSION_PATH = "/etc/version"

AIMATE_SPEECH_VERSION = "J5-HALO-GUA-AIMATE-RR1-Develop-0.3.0-rc1"
AIMATE_SPEECH_VERSION_PATH = "/userdata/app/halo/etc/version"

VERSION_DICT = dict()

WATCHDOG_CONF_CONTENT = "AVSPEECH|HIOK SENSOR"

KEY_AIMATE_SPEECH = "AIMATE"
KEY_HIOK_CONF = "hiok"
KEY_AIMATE_JARIVS = "antares"
KEY_KARAOKE_KPLUGIN = "kplugin"
KEY_BSP = "BSP"

WATCHDOG_CONF_PATH = "/userdata/app/halo/bin/scripts/"
HIOK_CONF_PATH = "/userdata/app/halo/etc/hiok/algo/hiok/"
HIOK_REF_CONF_PATH = "/userdata/app/halo/etc/std_config/"
KPLUGIN_DIR = "/sdcard/kplugin"
KPLUGIN_FILE = KPLUGIN_DIR + "/kp-HobotPlugin"


def run_shell_cmd(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output)

    process.wait()

    return process.returncode


def get_zip_file_path(zip_file, extract_path, target_file_key):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    for root, dirs, files in os.walk(extract_path):
        for file in files:
            if target_file_key in file:
                target_file_path = os.path.join(root, file)
                break

    return target_file_path


def is_ssh_command_available():
    try:
        # 使用subprocess运行ssh命令，检查返回码
        subprocess.run(['scp', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def transfer_file_to_j5(src_file, target_path):
    cmd = f"scp {src_file} root@{J5_IP}:{target_path}"
    print(cmd)
    run_shell_cmd(cmd)


def transfer_file_from_j5(src_file, target_path):
    # if is_ssh_command_available():
    cmd = f"scp root@{J5_IP}:{src_file} {target_path}"
    run_shell_cmd(cmd)


def update_bsp_version(bsp_file_key):
    print("now update bsp version")
    if os.path.exists(KEY_BSP):
        shutil.rmtree(KEY_BSP)

    os.makedirs(KEY_BSP)

    bsp_path = get_zip_file_path(WORK_PATH + VERSION_DICT[KEY_BSP], KEY_BSP, bsp_file_key)

    print("now scp bsp to J5")
    transfer_file_to_j5(bsp_path, "/userdata/")
    print("now scp bsp to J5 done")
    bsp_filename = bsp_path.strip().split('\\')[-1]
    cmd = f"ssh root@{J5_IP} otaupdate all /userdata/{bsp_filename} -f"
    print(cmd)
    run_shell_cmd(cmd)

    shutil.rmtree(KEY_BSP)


def check_version(target_version, version_path):
    cmd = f"ssh root@{J5_IP} cat {version_path}"
    result = subprocess.run(cmd, capture_output=True, text=True)

    version = str(result.stdout.strip())
    # version = str(result.stdout.strip().split()[0])
    print(version)
    print(target_version)

    if target_version in str(version):
        return True

    return False


def install_bsp_version():
    print("now checking bsp version")

    if check_version(BSP_VERSION, BSP_VERSION_PATH):
        print("bsp version is right")
        return

    print("bsp version is wrong")
    update_bsp_version("all_in_one-secure")
    time.sleep(2)

    if check_version(BSP_VERSION, BSP_VERSION_PATH):
        print("bsp update success")
        return

    print("bsp update failed, try again")
    update_bsp_version("all_in_one_full-secure")

    if check_version(BSP_VERSION, BSP_VERSION_PATH):
        print("bsp update success")
        return
    else:

        print("bsp update failed, please update manually")


def install_aimate_speech():
    print("now install AIMateSpeech")

    print("now scp aimate speech to J5")
    transfer_file_to_j5(WORK_PATH + VERSION_DICT[KEY_AIMATE_SPEECH], "/userdata/")
    print("now scp aimate speech to J5 done")

    cmd = "ssh root@" + J5_IP + " otaupdate app /userdata/" + VERSION_DICT[KEY_AIMATE_SPEECH]
    print("now update aimate")
    run_shell_cmd(cmd)
    print("now update done")

    print("now install AIMateSpeech done")


def modify_conf():
    print("now modify J5 conf")

    print("now modify startup items")
    tmp_conf_file = "./watchdog.conf"
    with open(tmp_conf_file, 'w') as f:
        f.write(WATCHDOG_CONF_CONTENT)

    transfer_file_to_j5(tmp_conf_file, WATCHDOG_CONF_PATH)
    os.remove(tmp_conf_file)
    print("now modify startup items done")

    print("now modify hiok configure file")
    transfer_file_to_j5(WORK_PATH + VERSION_DICT[KEY_HIOK_CONF], HIOK_CONF_PATH)
    print("now modify hiok configure file done")

    print("now modify hiok ref channel")
    hiok_ref_conf_name = "AudioInputModule.json"
    transfer_file_from_j5(HIOK_REF_CONF_PATH + hiok_ref_conf_name, "./")

    with open(hiok_ref_conf_name, 'r') as f:
        hiok_ref_conf = json.load(f)

    hiok_ref_conf["hiok_seat_map_to_record_channel"]["REF1"] = 13
    hiok_ref_conf["hiok_seat_map_to_record_channel"]["REF2"] = 14

    with open(hiok_ref_conf_name, 'w', newline='\n') as f:
        json.dump(hiok_ref_conf, f, indent=4)

    transfer_file_to_j5(hiok_ref_conf_name, HIOK_REF_CONF_PATH)

    os.remove(hiok_ref_conf_name)

    print("now modify hiok ref channel done")


def prepare_j5_env():
    print("now prepare j5 env")

    cmd = f"ssh root@{J5_IP} cat /etc/version"
    run_shell_cmd(cmd)

    install_bsp_version()

    if check_version(AIMATE_SPEECH_VERSION, AIMATE_SPEECH_VERSION_PATH):
        print("aimate speech is right")
    else:
        print("aimate speech is wrong, now update aimate speech version")
        install_aimate_speech()

    modify_conf()

    print("now restart aimate speech")
    cmd = f"ssh root@{J5_IP} bash /userdata/app/deinit.sh"
    run_shell_cmd(cmd)
    time.sleep(1)
    cmd = f"ssh root@{J5_IP} bash /userdata/app/init.sh"
    run_shell_cmd(cmd)
    print("now restart aimate speech done")

    print(">>>>>>>>>>>>>now j5 env ready<<<<<<<<<<<<<<<<")


def get_version_files():
    print("now parse version file")
    files = os.listdir(WORK_PATH)

    for file in files:
        if KEY_AIMATE_SPEECH in file:
            VERSION_DICT[KEY_AIMATE_SPEECH] = file
        elif KEY_HIOK_CONF in file:
            VERSION_DICT[KEY_HIOK_CONF] = file
        elif KEY_KARAOKE_APP in file:
            VERSION_DICT[KEY_KARAOKE_APP] = file
        elif KEY_AIMATE_JARIVS in file:
            VERSION_DICT[KEY_AIMATE_JARIVS] = file
        elif KEY_KARAOKE_KPLUGIN in file:
            VERSION_DICT[KEY_KARAOKE_KPLUGIN] = file
        elif KEY_BSP in file:
            VERSION_DICT[KEY_BSP] = file

    print("now parse version file done")


def install_karaoke_app():
    print("now install karaoke app")

    cmd = f"adb shell am force-stop {KILL_KARAOKE_NAME}"
    run_shell_cmd(cmd)

    cmd = f"adb install -r -t {WORK_PATH}{VERSION_DICT[KEY_KARAOKE_APP]}"  # 首次安装需要在pad上手动授权
    run_shell_cmd(cmd)
    print("now install karaoke app")


def intall_jarivs():
    print("now install aimate jarivs")
    if os.path.exists(KEY_AIMATE_JARIVS):
        shutil.rmtree(KEY_AIMATE_JARIVS)

    os.makedirs(KEY_AIMATE_JARIVS)

    jarivs_path = get_zip_file_path(WORK_PATH + VERSION_DICT[KEY_AIMATE_JARIVS], KEY_AIMATE_JARIVS, "jobs")

    cmd = f"adb install -r -t {jarivs_path}"  # 首次安装需要在pad上手动授权
    run_shell_cmd(cmd)

    shutil.rmtree(KEY_AIMATE_JARIVS)
    print("now install aimate jarivs done")


def install_kplugin():
    print("now install kplugin")

    cmd = f"adb shell \"mkdir {KPLUGIN_DIR}\""
    run_shell_cmd(cmd)

    cmd = f"adb shell \"touch {KPLUGIN_FILE}\""
    run_shell_cmd(cmd)

    cmd = f"adb push {WORK_PATH}{VERSION_DICT[KEY_KARAOKE_KPLUGIN]} {KPLUGIN_DIR}"
    run_shell_cmd(cmd)

    print("now install kplugin done")


def prepare_android_env():
    print("now prepare android env")

    cmd = "adb root"
    run_shell_cmd(cmd)
    cmd = "adb remount"
    run_shell_cmd(cmd)

    install_karaoke_app()
    intall_jarivs()
    if "Karaoke" == KEY_KARAOKE_APP:
        install_kplugin()

    print(">>>>>>>>>>>>>now android env ready<<<<<<<<<<<<<<<<")


def main():
    get_version_files()
    prepare_j5_env()
    prepare_android_env()

    print(">>>>>>>>>>>>>now hiok env ready<<<<<<<<<<<<<<<<")


if __name__ == '__main__':
    main()
