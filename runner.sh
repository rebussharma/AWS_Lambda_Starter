#!/bin/bash
# Author      : Ribash Sharma
# Purpose     : Start/stop all aws lambdas for each project: MAS, APCAS, FOIA
# License     : Open
# Update date : 17 Feb 2022
# Change log  : 
# Debug Me:
      # This is a bash script. It doesn't have a main fucntion
      # The execution of this script starts around line 109 !! Change log
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
      #   ./runner.sh start -a                    : start ALL lambdas regardless of project
      #   ./runner.sh start apcas -a              : start ALL lambdas for APCAS
      #   ./runner.sh start apcas lambda1, lambda2: start lambda1, lambda2 for APCAS

      #   starting and stopping is done via setting modifying concurrency of lambdas
      #   Projects, lambdas and thier configurations are stored in JSON format in file: config.json
      #   a seperate library 'jq' is used to retrieve objects from json files


# @function    : all_start
# @parameter/s : 
#               project_name: name of project
#               action : start or stop
# @Purpose     : if user provides '-a' as an arguement this fucntion starts all lambdas
# @references  : main_switch, main function: main fucntion as in main body

all_start(){
  if [ $project_name == "-a" ] # if project name is not supplied
    then
      echo "${action}ing all lambdas"
      #1. Use jq -r (output raw strings, not JSON texts)
      #2. Use @sh (Converts input string to a series of space-separated strings).
          # It removes square brackets[], comma(,) from the string.
      #3. Using tr to remove single quotes from the string output. 
          # To delete specific characters use the -d option in tr.
      #4. decorate the assignement with () around to convert in bash array
      lambda_list=($((<config.json jq -r 'map(keys[])| @sh')| tr -d \'\"))
    else
      echo "${action}ing all $project_name lambdas"
      lambda_list=($((<config.json jq -r '.'$project_name'| keys | @sh')| tr -d \'\"))
  fi
  lambda_length=${#lambda_list[@]}

  for i in $(seq 0 $((lambda_length-1)))
  do
    echo "${action}ing lambda: ${lambda_list[$i]}"
    if [ $action == "start" ]
      then
        concurrency=$(jq -r '.[].'${lambda_list[$i]}'.con | select(. != null)' config.json)
        #aws lambda put-function-concurrency --function-name  ${lambda_list[$i]  --reserved-concurrent-executions $concurrency
      else
        echo ""
        #aws lambda put-function-concurrency --function-name  ${lambda_list[$i]  --reserved-concurrent-executions 0

    fi
  done
}

# @function    : lambda_starter
# @parameter/s : 
#               total_lambdas: total number of lambda fucntions provided
#               lambda_name: list containing all lambda functions
#               project_name: Name of project if provided
#               action: start or stop : has no purpose here other than being passed inside string
# @Purpose     : start / stop given lambdas for provided project
# @references  :
lambda_starter(){
  if [ $total_lambdas -eq "0" ] # if nothing is provided after APCAS eg ./runner.sh start apcas <empty>
    then
      echo -e "start which $1 lambda ?"
    else
      case $lambda_name in  # if provided lambda name has -a to start all i.e 'start apcas -a'
        -a)
          all_start $action $project_name # start all lambdas for the projects
        ;;
        *) 
          for i in $lambda_name # iterate over each lambdas provided
            do
              # -r gets data in raw format
              # .$project_name.$i = .apcas/mas/foia.lambdaname  : to get lambda name
              valid_lambda=$(jq -r .$project_name.$i config.json)
              if [[ $valid_lambda == "null" ]]  # null return indicated certain lambda func is not part of certain project
                then
                  echo "This lambda for $project_name doesn't exist: $i"
                else
                  echo "${action}ing $project_name lambda $i"
                  if [ $action == "start" ]
                    then
                      # -r gets data in raw format
                      # .$project_name.$i.con = .apcas/mas/foia.lambdaname.con  : to get concurrency of lambda                    
                      concurrency=$(jq -r '.'$project_name'.'${i}'.concurrency | select(. != null)' config.json)
                      $(aws lambda put-function-concurrency --function-name  $i  --reserved-concurrent-executions $concurrency)
                    else
                      $(aws lambda put-function-concurrency --function-name  $i  --reserved-concurrent-executions 0)
                  fi
              fi

            done
        ;;
      esac
  fi
}

# @function    : main_switch
# @parameter/s : 
                  # $project_name_size: length of project name string:  apcas:4 mas:3
                  # $project_name : name of ptoject:  mas, apcas
                  # $lambda_name : names of lambda func for project
                  # $total_lambdas : total lambdas supplied
                  # $action: start | stop
# @Purpose     : switch cases between different project bame
# @references  : lambda_starter
main_switch(){
  if [ $project_name_size -eq "0" ]  # if second arguement is empty
    then
      echo -e "bro start/stop what?\n" # ./runner.sh start <empty>
    else
    # switch depending on case
      case $project_name in
      #case APCAS
        apcas|mas|foia)
          lambda_starter $project_name $lambda_name $total_lambdas $action
        ;;

        -a)
          all_start $action
        ;;

        *)
          echo "invalid arguements"
      esac
  fi
}


if [ $# -eq 0 ] || [ -z "$1" ] # $# tells number of input passed, -z will test if $1 is null
  then
    echo "Type '--help', 'copyrights', 'license' for more information."
  else
    first_cmd="$1"
    first_cmd="${first_cmd,,}" # lower case all arguements

    project_name="$2"
    project_name="${project_name,,}"
    project_name_size=${#project_name}
    lambda_name="${@:3}"
    lambda_name=("${lambda_name,,}")
    total_lambdas=${#lambda_name}

    case $first_cmd in
      --help)
        if [ -z "$2" ]  # if seconf arguement is empty, it is valid eg ./runner.sh --help
          then
            v="usage: bash [options] or ./file.sh
            \nstart\t: start lambdas. Can start multiple lambdas.
            \n\t-a\t: start all lambdas
              \n\t[project-name]\t: start lambda for project-name
              \n\tExample:\tstart APCAS -a\t: starts all lambdas for APCAS
              \n\t\t\tstart APCAS test1, test2\t: starts test1 and test2 lambdas for APCAS
              \nstop\t: stop lambdas. Can start multiple lambdas.
              \n\t-a\t: stop all lambdas
              \n\t[project-name]\t: stop lambda project-name
              \n\tExample:\tstop APCAS -a\t: stop all lambdas for APCAS
              \n\t\t\tstop MAS test1, test2\t: stop test1 and test2 lambdas for MAS"
            echo -e $v
          else
            echo "Invalid Argument" # eg ./runner.sh --help <some_other_arguements>
        fi
      ;;
      start | stop)
        action=$1
        main_switch $project_name_size $project_name $lambda_name $total_lambdas $action
      ;;

      license)
        v="some license texts"
        echo $v
      ;;
      *)
        echo "invalid arguement"
      ;;
      # case stop
    esac
fi
