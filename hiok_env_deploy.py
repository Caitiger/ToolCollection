import os
import subprocess
import json
import time

WORK_PATH = "./test_data/"

J5_IP = "10.64.134.84"
BSP_VERSION = "Halo5-BSP-1.0.12_Release"
VERSION_DICT = dict()

WATCHDOG_CONF_CONTENT = "AVSPEECH|HIOK SENSOR"

KEY_AIMATE_SPEECH = "aimate_speech"
KEY_HIOK_CONF = "hiok_conf"
KEY_KARAOKE_APP = "karaoke_app"
KEY_AIMATE_JARIVS = "aimate_jarivs"
KEY_KARAOKE_KPLUGIN = "karaoke_kplugin"

WATCHDOG_CONF_PATH = "/userdata/app/halo/bin/scripts/"
HIOK_CONF_PATH = "/userdata/app/halo/etc/hiok/algo/hiok/"
HIOK_REF_CONF_PATH = "/userdata/app/halo/etc/std_config/"


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


def check_bsp_version():
    print("now checking bsp version")
    cmd = "ssh root@" + J5_IP + " cat /etc/version"
    result = subprocess.run(cmd, capture_output=True, text=True)

    bsp_version = str(result.stdout.strip().split()[0])

    print(result.returncode)
    print(bsp_version)

    if bsp_version != BSP_VERSION:
        print("bsp version is wrong, please use right bsp version")
        exit(1)

    print("bsp version is right")


def install_aimate_speech():
    print("now install AIMateSpeech")

    cmd = "scp " + WORK_PATH + VERSION_DICT[KEY_AIMATE_SPEECH] + " root@" + J5_IP + ":/userdata/"
    print("now scp aimate speech to J5")
    run_shell_cmd(cmd)
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

    cmd = f"scp {tmp_conf_file} root@{J5_IP}:{WATCHDOG_CONF_PATH}"
    run_shell_cmd(cmd)
    os.remove(tmp_conf_file)
    print("now modify startup items done")

    print("now modify hiok configure file")
    cmd = f"scp {WORK_PATH}{VERSION_DICT[KEY_HIOK_CONF]} root@{J5_IP}:{HIOK_CONF_PATH}"
    run_shell_cmd(cmd)
    print("now modify hiok configure file done")

    print("now modify hiok ref channel")
    hiok_ref_conf_name = "AudioInputModule.json"
    cmd = f"scp root@{J5_IP}:{HIOK_REF_CONF_PATH}{hiok_ref_conf_name} ."
    run_shell_cmd(cmd)

    with open(hiok_ref_conf_name, 'r') as f:
        hiok_ref_conf = json.load(f)

    hiok_ref_conf["hiok_seat_map_to_record_channel"]["REF1"] = 13
    hiok_ref_conf["hiok_seat_map_to_record_channel"]["REF2"] = 14

    with open(hiok_ref_conf_name, 'w', newline='\n') as f:
        json.dump(hiok_ref_conf, f, indent=4)

    cmd = f"scp {hiok_ref_conf_name} root@{J5_IP}:{HIOK_REF_CONF_PATH}"
    run_shell_cmd(cmd)

    os.remove(hiok_ref_conf_name)

    print("now modify hiok ref channel done")

def prepare_j5_env():
    print("now prepare j5 env")

    check_bsp_version()

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
        if "AIMATE" in file:
            VERSION_DICT[KEY_AIMATE_SPEECH] = file
        elif "hiok" in file:
            VERSION_DICT[KEY_HIOK_CONF] = file
        elif "Karaoke" in file:
            VERSION_DICT[KEY_KARAOKE_APP] = file
        elif "antares" in file:
            VERSION_DICT[KEY_AIMATE_JARIVS] = file
        elif "kplugin" in file:
            VERSION_DICT["karaoke_kplugin"] = file

    print("now parse version file done")


def prepare_android_env():
    print("now prepare android env")

    print(">>>>>>>>>>>>>now android env ready<<<<<<<<<<<<<<<<")

def main():
    get_version_files()
    prepare_j5_env()
    prepare_android_env()

    print(">>>>>>>>>>>>>now hiok env ready<<<<<<<<<<<<<<<<")

if __name__ == '__main__':
    main()
