# lambda-scripts
Scripts in this repo are used to start/stop lambdas used in each projects

## Contents
1. config.json
2. runner.py
3. runner.sh
---

**config.json** <br>
    &emsp;&ensp;This file contains details of all lambda functions in used in Java Script Object Notation (JSON)
        format.
<br>&emsp;&ensp;The structure of this file must be preserved during any modification for other scripts to 
function correctly.<br>&emsp;&ensp;The structure to be followed is: Project name (parent), lambda names (child) and details of lambda names
<br><br><br>
**runner.py**<br>
&emsp;&ensp;This is a python script used to start and stop lambda functions. <br>
&emsp;&ensp;The file gets its data: project names, lambda names and their details from config.json file.
<br>&emsp;&ensp;It requires python **_version 3.10_** or later to run.To start the script use `python runner.py --help`
<br><br><br>
**runner.sh**<br>
&emsp;&ensp;This is a bash file to start and stop lambda functions.
<br>&emsp;&ensp;It serves similar purpose to previous python file. To start the script use `./runner.sh --help`
<br><br>


