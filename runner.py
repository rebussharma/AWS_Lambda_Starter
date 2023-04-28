# @Author      : Ribash Sharma
# @Purpose     : Start/stop all aws lambdas for each project: MAS, APCAS, FOIA
# @License     : Open
# @Update date : 17 Feb 2022
# @Prereq      : Python 3.10
# @Change log  :
# @Debug Me:
# This is a python script to automate start/stop of lambdas.
# User must provide arguements to run the script.
# The script checks if any arguement is provided, if a VALID arguement is provided. The script works.
# Valid arguements are --help, license, start, stop
# For --help and licnece, just some lines are shown      For start, stop: we dive deeper.
# Assume user provides 'start' as an arguement. Then the user must provide more arguements
#   -a  : To start ALL lambdas regardless of project OR
#   porject_name: If a user provides a project name. Then the user must provide more arguements
#     -a : To start ALL lambdas regardless of project OR
#     lambda_name: User can provide multiple lambda function names
# Example:
#   python runner.py start -a                    : start ALL lambdas regardless of project
#   python runner.py start apcas -a              : start ALL lambdas for APCAS
#   python runner.py start apcas lambda1, lambda2: start lambda1, lambda2 for APCAS

#   starting and stopping is done via setting modifying concurrency of lambdas
#   Projects, lambdas and thier configurations are stored in JSON format in file: config.json

import boto3
import sys
import json


# @function    : start_stop_all
# @parameter/s :
#               lambda_list: list of lambdas
#               action : start or stop
#               clinet : boto client
# @Purpose     : if user provides '-a' as an arguement this fucntion starts all lambdas
# @references  :
def start_stop_all(lambda_list, action, client):
    stop_concurrency = 0
    for ll in lambda_list:
        # get concurrency from json file for given lambda
        start_concurrency = [sublist.get(ll).get('concurrency') for sublist in data.values() if
                             sublist.get(ll) is not None]

        if action != "start":
            print(f'{action}ing all')
            # boto 3 functionality to set concurrency
            res = client.put_function_concurrency(FunctionName=ll,
                                                  ReservedConcurrentExecutions=stop_concurrency)
        else:
            print(f'{action}ing all')
            res = client.put_function_concurrency(FunctionName=ll,
                                                  ReservedConcurrentExecutions=start_concurrency)


# @function    : start_stop
# @parameter/s :
#               action : start or stop
#               clinet : boto client
# @Purpose     : start / stop given lambdas for provided project
# @references  :
def start_stop(action, client):
    if len(sys.argv) >= 3:
        match str(sys.argv[2]).lower():
            case "-a":
                print(f"{action}ing all lambdas")
                # get list of all lambdas, in this case regardless of the project
                lambda_list = [item for sublist in data.values() for item in sublist]
                start_stop_all(lambda_list, action, client)

            case "apcas" | "mas" | "foia":
                if len(sys.argv) > 3:
                    project_name = str(sys.argv[2]).lower()
                    match str(sys.argv[3]).lower():
                        case '-a':
                            # get list of all lambdas for given project
                            lambda_list = list(data.get(project_name).keys())
                            print(f'{action}ing all {project_name} lambdas')
                            start_stop_all(lambda_list, action, client)
                        case _:
                            lambda_list = list(data.get(project_name).keys())
                            for i in range(3, len(sys.argv)):
                                lambda_name = str(sys.argv[i]).lower()
                                start_concurrency = data.get(project_name).get(lambda_name).get("concurrency")
                                stop_concurrency = 0
                                if lambda_name in lambda_list:
                                    print(f'{action}ing {sys.argv[i]}')
                                    if action == "start":
                                        res = client.put_function_concurrency(FunctionName=lambda_name,
                                                                              ReservedConcurrentExecutions=start_concurrency)
                                    else:
                                        res = client.put_function_concurrency(FunctionName=lambda_name,
                                                                              ReservedConcurrentExecutions=stop_concurrency)
                                else:
                                    print(f"{sys.argv[i]} doesn't exist for {project_name}")
                else:
                    print(f"please provide a valid lambda name")
            case _:
                print("Invalid argument. Type --help for more info")
    else:
        print(f"Error: {action} what ?")


if __name__ == '__main__':

    if sys.version_info.major != 3 and sys.version_info.minor != 10:
        print("Python version 3.10 or later required to run")
    else:
        file = open('config.json')
        data = json.load(file)

        client = boto3.client('lambda')

        if len(sys.argv) == 1:
            print("Type '--help', 'copyrights', 'license' for more information.")
        else:
            match_str = str(sys.argv[1]).lower()

            match match_str:
                case "--help":
                    if len(sys.argv) == 2:
                        print("usage: python runner.py [options]\n"
                              "start\t: start lambdas. Can start multiple lambdas. Provide lambda names comma separated\n\t"
                              "-a\t: start all lambdas\n\t"
                              "[project-name]\t: start lambda/s for certain project\n\t\t\t"
                              "-a\t: start all lambdas for certain project\n\t\t\t"
                              "[lambda_names]\t: start certain lambda/s for project specified\n\t\t\t"
                              "Examples:\n\t\t\t\tstart mas -a\t: starts all lambdas\n\t\t\t\t"
                              "start mas test1, test2\t: starts test1 and test2 lambdas for mas project\n"
                              "stop\t: stop lambdas. Can start multiple lambdas. Provide lambda names comma separated\n\t"
                              "-a\t: stop all lambdas\n\t"
                              "[project-name]\t: stop lambda/s for certain project\n\t\t\t"
                              "-a\t: stop all lambdas for certain project\n\t\t\t"
                              "[lambda_names]\t: stop certain lambda/s for project specified\n\t\t\t"
                              "Examples:\n\t\t\t\tstop -a\t: stop all lambdas\n\t\t\t\t"
                              "stop apcas test1, test2\t: stop test1 and test2 lambdas for apcas project\n")
                    else:
                        print("Error: Unexpected argument after --help")

                case "start" | "stop":
                    start_stop(str(sys.argv[1]), client)
                case "license" | "copyright" | "copyrights":
                    print("Aptive Resources")
                case "author":
                    print("Ribash Sharma")
                case _:
                    print("Error: Invalid command")
