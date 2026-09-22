import json
from pathlib import Path

def write_json(data,file_path):
    """ Write python dictionary to json file """

    file_path=Path(file_path)

    #create a folder if doesnt exists
    file_path.parent.mkdir(parents=True,exist_ok=True) #create missing folder before opening file

    with open(file_path,"w") as f:
        json.dump(data,f,indent=4) #python dic to json

    return str(file_path) #he DAG can pass this path to the next task using XCom:
