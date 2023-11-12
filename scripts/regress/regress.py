#!/usr/bin/python3

from subprocess import Popen, PIPE
import threading
import os
import argparse
import re

# ------------------------
# Fields
# ------------------------

# Path to test list folder
tl_path = "./"

# Test list name
tl_name =  "test list name"
tc_name = "test case name"

# Sets single_run for runing single test case
single_run = 0 

# Run test structure
tests_list = []

# Common options
comn_make_opts = ''
comn_run_opts = ''

# Jobs
# Set this for limit jobs (use license)
job_max = 50
job_num = 1
 
no_comp = 0

# ------------------------
# Args
# ------------------------
parser = argparse.ArgumentParser()

parser.add_argument("tl_name", type=str, help="Tests list name")
parser.add_argument("--opts", type=str, help="Make file options")
parser.add_argument("--job_num", type=int, default=1, help="Number of parallel jobs")
parser.add_argument("--no_comp", type=int, default=0, help="Use this opts for run regression without compilation")

args = parser.parse_args()

# ------------------------
# Metods
# ------------------------

# Loading test list 
def test_list_load(file_path):
    file = open(file_path, 'r')
    line = file.readline()
    while line:
        pars_test_list_line(line)
        line = file.readline()
    file.close()

# Test list line parsing process (Testname, plusargs etc.)
def pars_test_list_line(line):
    sub_line = re.split(r'\s*:\s*', line)
    if sub_line.__len__() == 2 and sub_line[0]!="":
        list_item = {}
        list_item ['name'] = sub_line[0]
        pattern = r'^.*RUN_OPTS\+?=[\"|\'](?P<run_opts>.*)[\"|\']\s+.*$'
        match = re.match(pattern, sub_line[1])
        if match:
            sub_line[1] = re.sub(r'\s*RUN_OPTS\+?=[\"|\'].*[\"|\']\s*','',sub_line[1])
            list_item ['run_opts'] = match.group('run_opts')
        else:
            list_item ['run_opts'] = ''
        # TODO: Add check iterations
        sub_line[1] = re.sub(r'\n*','',sub_line[1])
        list_item ['make_opts'] = sub_line[1]
        # print(list_item ['make_opts'])
        tests_list.append(list_item)


# Parsing common options from command line
def pars_common_opts(line):
    global comn_make_opts
    global comn_run_opts
    pattern = r'^.*RUN_OPTS\+?=[\"|\'](?P<run_opts>.*)[\"|\']\s*.*$'
    match = re.match(pattern, line)
    if match:
        line = re.sub(r'\s*RUN_OPTS\+?=[\"|\'].*[\"|\']\s*','',line)
        comn_run_opts = match.group('run_opts')
        # print(comn_run_opts)
    comn_make_opts = line
    # TODO: Add check iterations    

# Creating command run line
def create_run_line():
    for test in tests_list:
        test['sim_dir'] = test['name'] + '_sim'
        test['cmd'] = 'make run '
        test['cmd'] += 'RUN_OPTS+=\'' +  comn_run_opts + ' ' + test['run_opts'] + '\' '
        test['cmd'] += comn_make_opts + ' ' + test['make_opts']
        test['cmd'] += ' SIM_DIR=' + test['sim_dir']
        # print(test['cmd'])

# Compile tests command to terminal
def compile():
    os.system('make comp')

# Run test command to terminal
def run_test(cmd_line):
    semaphore.acquire()
    process = Popen(['bash'], stdin=PIPE, stderr=PIPE, stdout=PIPE)
    try:
        output, error = process.communicate(cmd_line.encode())
        if error:
            print(error.decode())
        else:
            print(output.decode())
        semaphore.release()
        
        # process.stdin.write(b'source ./sourceme\n')
        # process.stdin.write(cmd_line.encode())
        # process.stdin.flush()
        # process.stdin.close()
        # print(process.stdout.read().decode())
        # process.stdout.close()
        # process.wait()
    finally:
        semaphore.release()
    process.terminate()

def start_regression():
    global semaphore 
    semaphore = threading.Semaphore(job_num)
    treads = []
    for test in tests_list:
        tread = threading.Thread(target=run_test, args=(test['cmd'],))
        treads.append(tread)
        tread.start()
    for tread in treads:
        tread.join()

def pars_args():
    # ------------------------
    # Parsing run command line args
    # ------------------------

    # Regres list or single run 
    global tl_name, tc_name, job_num, no_comp, single_run

    tl_name = args.tl_name
    match = re.match(r'^(?P<tl_name>\w*)\.(?P<tc_name>\w*)',tl_name)
    if match:
        tl_name = match.group('tl_name')
        tc_name = match.group('tc_name')
        single_run = 1

    # Getting common options 
    if args.opts != None:
        pars_common_opts(args.opts)

    # Getting jobs num
    job_num = args.job_num
    if job_num > job_max:
        job_num = job_max

    # Regress opts
    no_comp = args.no_comp


def main():
    # ------------------------
    # Main script
    # ------------------------
    # Pars input args 
    pars_args()

    # Loading the List and parsing
    test_list_load(tl_path + tl_name + '.list')

    # Creating make command line
    # if iteration = 1
    create_run_line()

    # Compile projekt
    if not no_comp:
        compile()

    # Run tests coomand
    if not single_run:
        start_regression()
    # else: TODO: Run single test like <list>.test "mini.uart_test"
    #     start_singl_test()

    # TODO: Log file parsing  and create summury table
    print("Regression complete")

if __name__ == "__main__":
    main()
