import os, subprocess, sys
from datetime import datetime
from status_response import Status_response, StatusType
import git

def parse(data):
    """Parse the json webhook input from github."""
    res = {}
    # branch name
    if 'ref' in data:
        res['branch'] = data['ref'].split('/')[-1]
    else:
        res['error'] = 'Missing key'

    # last commit sha
    if 'head_commit' in data and 'id' in data['head_commit']:
        res['head_commit'] = data['head_commit']['id']
    else:
        res['error'] = 'Missing key'
    return res


# def change_dir(dir):
#     """helper function to change dir"""
#
#     # checking whether folder/directory exists, if not then make one
#     if not os.path.exists(dir):
#         os.mkdir(dir)
#     os.chdir(dir)


def create_env_file():
    """Creates an environment file with a TOKEN constant."""
    file_path = '../src/env.py'
    try:
        with open(file_path, 'w') as f:
            f.write('TOKEN = \'\'\n')
            f.write('BASE_URL = \'\'\n')
    except:
        raise

def clone_git_repo(branch):
    """clone the branch repo"""
    if os.path.isdir('./branch_repo'):
        git.rmtree('./branch_repo')
    os.mkdir('./branch_repo')
    os.chdir('./branch_repo')
    create_env_file()
    repo = git.Repo.clone_from('https://github.com/andnil5/dd2480-grp12-assignment2.git', './branch_repo', progress=None)
    gt = repo.git
    gt.checkout(branch)


# def setup_repo(branch):
#     """clone the branch repo"""
#     change_dir('./git_repo')
#     print(os.getcwd())
#     create_env_file()
#     cmd = [['git', 'fetch'], ['git', 'checkout', branch], ['git', 'pull']]
#     for c in cmd:
#         p = subprocess.Popen(c)
#         if p.wait() != 0:
#             print('Failed!!!')
#             break


def log_to_file(file, branch, sha, p):
    """Logs the content of the stdout of a subprocess to a specific log file
       as well as a timestamp for the logging, and the branch and sha
       corresponding to the subprocess.

    Parameters
    ----------
    file: The path (in relation to the root directory) of the logfile - A string.
    branch: The name of the branch in which the commit is made - A string.
    sha: The commit sha of the repo state which the process was run in - A string.
    p: The completed subprocess which stdout should be logged - A CompletedProcess object.

    Returns
    ----------
    None
    """

    with open('../'+file, 'a+') as log:
        # print meta data about test run to the log
        log.write("\n{date} :: {branch} -- {sha}:\n".format(date=datetime.now(), branch=branch, sha=sha))
        # print the test output to the log
        log.write(p.stdout.decode('utf-8'))


def run_compile(branch, sha):
    """From the `git_repo` directory, run the linter tool flake8 on all the
       files in the directory, ignoring E501 (too long lines). The flake8
       output is logged to a file with the path 'logs_compile/<branch>_<sha>.txt',
       where <branch> and <sha> are substituted to the `branch` and `sha`
       arguments.

    Parameters
    ----------
    branch: The name of the branch in which the commit is made - A string.
    sha: The commit sha of the repo state that should be analysed - A string.

    Returns
    ----------
    Status_response: A Status_response instance representing the result of
                     the analysis.
    """
    os.chdir('./branch_repo')
    sub_proc = subprocess.run(['python{}'.format(sys.version[:3]), '-m', 'flake8', '--ignore=E501', '../branch_repo/'], capture_output=True)
    file = "/logs_compile/{}_{}.txt".format(branch, sha)
    log_to_file(file, branch, sha, sub_proc)
    os.chdir('..')
    return Status_response(sub_proc.returncode, StatusType.compile, sha, file)


def run_test(branch, sha):
    """Run all the tests within the current directory with pytest. The tests
       must be written in files with names on the form 'test*.py' or '*test.py'.
       The pytest output is logged to a file with the path
       'logs_tests/<branch>_<sha>.txt', where <branch> and <sha> are
       substituted to the `branch` and `sha` arguments.

    Parameters
    ----------
    branch: The name of the branch in which the commit is made - A string.
    sha: The commit sha of the repo state that should be tested - A string.

    Returns
    ----------
    Status_response: A Status_response instance representing the result of
                     the test.
    """
    os.chdir('./branch_repo')
    sub_proc = subprocess.run(["python3", "-m", "pytest"], capture_output=True)
    file = "/logs_tests/{}_{}.txt".format(branch, sha)
    log_to_file(file, branch, sha, sub_proc)
    os.chdir('..')
    return Status_response(sub_proc.returncode, StatusType.test, sha, file)
