import subprocess
import shlex
import time

def stop(proc:subprocess.Popen):
    proc.terminate()

    try:
        proc.wait(2)
        print("Terminated")
    except subprocess.TimeoutExpired:
        proc.kill()
        print("Killed")
        #outs, errs = proc.communicate()
    
    

def show_folder(folder:str):
    cmd = f"feh -Z -D 2 -F -x -B black -Y -K captions/ --font yudit/30 --draw-tinted {folder}"
    args = shlex.split(cmd)
    proc = subprocess.Popen(args)
    return proc

print('Start')

folder_1 = "/home/fvbakel/tmp/test_foto/1"
folder_2 = "/home/fvbakel/tmp/test_foto/2"

proc_1 = show_folder(folder_1)
time.sleep(7)
stop(proc_1)
print("Changing folder")
proc_2 = show_folder(folder_2)
time.sleep(5)
stop(proc_2)
