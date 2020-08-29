import os
import sys
import subprocess


def getPackageInfo(packageName):
    packageInfo = {}
    packageInfoProc = subprocess.run(
        ["pip3", "show", packageName],
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if packageInfoProc.stderr == "":
        for line in packageInfoProc.stdout.split("\n"):
            splitStr = line.split(": ")
            if len(splitStr) >= 2:
                key = splitStr[0].lower()
                val = splitStr[1]
                packageInfo[key] = val
    return packageInfo
