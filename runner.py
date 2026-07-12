# import os
# import subprocess
# import time
# import json

# # ---------- CONFIG ---------- #
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# INPUT_DIR = os.path.join(BASE_DIR, "input")
# OUTPUT_DIR = os.path.join(BASE_DIR, "dataset")
# FRIDA_SCRIPT = os.path.join(BASE_DIR, "script.js")

# os.makedirs(OUTPUT_DIR, exist_ok=True)


# # ---------- HELPERS ---------- #

# def get_package(apk):
#     try:
#         out = subprocess.check_output(
#             f'aapt dump badging "{apk}"',
#             shell=True,
#             stderr=subprocess.DEVNULL
#         ).decode()

#         for line in out.split("\n"):
#             if "package: name=" in line:
#                 return line.split("'")[1]
#     except:
#         return None


# def install_apk(apk):
#     subprocess.run(f'adb install -r "{apk}"', shell=True)


# def uninstall_apk(pkg):
#     subprocess.run(f'adb uninstall {pkg}', shell=True)


# # ---------- CORE PIPELINE ---------- #

# def process_apk(apk_path, label):
#     print(f"\n📦 Processing: {apk_path}")

#     pkg = get_package(apk_path)

#     if not pkg:
#         print("❌ Package not found")
#         return

#     install_apk(apk_path)

#     # ---------- START FRIDA ---------- #
#     proc = subprocess.Popen(
#         f'frida -U -f {pkg} -l "{FRIDA_SCRIPT}" > output.txt',
#         shell=True
#     )

#     # ---------- TRIGGER BEHAVIOR ---------- #
#     time.sleep(5)  # wait for app to start

#     subprocess.run(f'adb shell monkey -p {pkg} -v 300', shell=True)

#     time.sleep(20)  # allow background activity

#     # ---------- STOP FRIDA ---------- #
#     proc.terminate()

#     # ---------- PARSE ---------- #
#     subprocess.run("python parser.py", shell=True)

#     # ---------- VALIDATE OUTPUT ---------- #
#     if not os.path.exists("output.json"):
#         print("❌ output.json not generated")
#         uninstall_apk(pkg)
#         return

#     with open("output.json") as f:
#         data = json.load(f)

#     # ---------- FILTER LOW ACTIVITY ---------- #
#     if data.get("event_density", 0) < 2:
#         print("⚠️ Low activity sample — skipping")
#         uninstall_apk(pkg)
#         return

#     # ---------- SAVE ---------- #
#     name = os.path.basename(apk_path).replace(".apk", ".json")
#     output_path = os.path.join(OUTPUT_DIR, f"{label}_{name}")

#     os.replace("output.json", output_path)

#     uninstall_apk(pkg)

#     time.sleep(3)

#     print(f"✅ Saved: {output_path}")


# # ---------- MAIN ---------- #

# def run_all():
#     if not os.path.exists(INPUT_DIR):
#         print("❌ input folder not found")
#         return

#     labels = os.listdir(INPUT_DIR)

#     for label in labels:
#         folder = os.path.join(INPUT_DIR, label)

#         if not os.path.isdir(folder):
#             continue

#         print(f"\n📂 Processing category: {label}")

#         for apk in os.listdir(folder):
#             if apk.endswith(".apk"):
#                 apk_path = os.path.join(folder, apk)
#                 process_apk(apk_path, label)

#     print("\n🚀 DONE")


# # ---------- ENTRY ---------- #

# if __name__ == "__main__":
#     run_all()


import os
import subprocess
import time
import json

# ---------- CONFIG ---------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset")
FRIDA_SCRIPT = os.path.join(BASE_DIR, "script.js")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------- HELPERS ---------- #

def get_package(apk):
    try:
        out = subprocess.check_output(
            f'aapt dump badging "{apk}"',
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode()

        for line in out.split("\n"):
            if "package: name=" in line:
                return line.split("'")[1]
    except:
        return None


def install_apk(apk):
    subprocess.run(f'adb install -r "{apk}"', shell=True)


def uninstall_apk(pkg):
    subprocess.run(f'adb uninstall {pkg}', shell=True)


# ---------- CORE PIPELINE ---------- #

def process_apk(apk_path, label):
    print(f"\n📦 Processing: {apk_path}")

    pkg = get_package(apk_path)

    if not pkg:
        print("❌ Package not found")
        return

    install_apk(apk_path)

    # ---------- START FRIDA ---------- #
    proc = subprocess.Popen(
        f'frida -U -f {pkg} -l "{FRIDA_SCRIPT}" > output.txt',
        shell=True
    )

    # ---------- TRIGGER BEHAVIOR ---------- #
    time.sleep(5)

    subprocess.run(f'adb shell monkey -p {pkg} -v 100', shell=True)

    time.sleep(25)

    # ---------- STOP FRIDA ---------- #
    proc.terminate()

    # ---------- PARSE ---------- #
    subprocess.run("python parser.py", shell=True)

    # ---------- VALIDATE OUTPUT ---------- #
    if not os.path.exists("output.json"):
        print("❌ output.json not generated")
        uninstall_apk(pkg)
        return

    with open("output.json") as f:
        data = json.load(f)

    # ---------- NEW FILTER (RAW EVENTS) ---------- #

    if not isinstance(data, list):
        print("❌ Invalid JSON format")
        uninstall_apk(pkg)
        return

    event_count = len(data)

    print(f"📊 Events captured: {event_count}")

    if event_count == 0:
        print("⚠️ No events — skipping")
        uninstall_apk(pkg)
        return

    if event_count < 5:
        print("⚠️ Too few events — skipping")
        uninstall_apk(pkg)
        return

    # ---------- SAVE ---------- #
    name = os.path.basename(apk_path).replace(".apk", ".json")
    output_path = os.path.join(OUTPUT_DIR, f"{label}_{name}")

    os.replace("output.json", output_path)

    uninstall_apk(pkg)

    time.sleep(3)

    print(f"✅ Saved: {output_path}")


# ---------- MAIN ---------- #

def run_all():
    if not os.path.exists(INPUT_DIR):
        print("❌ input folder not found")
        return

    labels = os.listdir(INPUT_DIR)

    for label in labels:
        folder = os.path.join(INPUT_DIR, label)

        if not os.path.isdir(folder):
            continue

        print(f"\n📂 Processing category: {label}")

        for apk in os.listdir(folder):
            if apk.endswith(".apk"):
                apk_path = os.path.join(folder, apk)
                process_apk(apk_path, label)

    print("\n🚀 DONE")


# ---------- ENTRY ---------- #

if __name__ == "__main__":
    run_all()