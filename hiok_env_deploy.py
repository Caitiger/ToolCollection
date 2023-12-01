import os
import subprocess

WORK_PATH = "./test_data/"

J5_IP = "10.64.134.83"
BSP_VERSION = "Halo5-BSP-1.0.12_Release"
VERSION_DICT = dict()

KEY_AIMATE_SPEECH = "aimate_speech"
KEY_HIOK_CONF = "hiok_conf"
KEY_KARAOKE_APP = "karaoke_app"
KEY_AIMATE_JARIVS = "aimate_jarivs"
KEY_KARAOKE_KPLUGIN = "karaoke_kplugin"


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
    # subprocess.run(cmd, capture_output=True)

def prepare_j5_env():
    print("now prepare j5 env")

    check_bsp_version()
    # install_aimate_speech()

    print("prepare j5 env done")


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


def main():
    get_version_files()
    prepare_j5_env()


if __name__ == '__main__':
    main()
