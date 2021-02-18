# def main():
#     dir_path, filename = os.path.split(GUI.main_window.__file__)
#     os.chdir(dir_path)
#     num_of_clients = 2
#
#     p = Process(target=GUI.main_window.main)
#     p.start()
#     p.join()
#
#
# if __name__ == '__main__':
#     import os
#     import subprocess
#     import GUI.main_window
#     from multiprocessing import Process
#     main()


import os
import subprocess
import time
import GUI.main_window

dir_path, filename = os.path.split(GUI.main_window.__file__)
os.chdir(dir_path)
num_of_clients = 2

for i in range(num_of_clients):
    print(f'creating client{i}...')
    subprocess.Popen(f'echo client{i} | python {filename}', shell=True,
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(0.1)