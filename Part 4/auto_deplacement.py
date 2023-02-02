import os
import json
import shutil
import json

path_to_gns3_project = None
path_to_dynamips = None

def initialize(path):
    global path_to_gns3_project
    global path_to_dynamips
    path_to_gns3_project = path
    path_to_dynamips = path+"/project-files/dynamips"


def correspondance_hostname_nodeid():
    liste_fichiers = os.listdir(path_to_gns3_project)
    project_file = ""
    correspondance_dict = {}
    for file in liste_fichiers:
        if (".gns3" in file) and not ("backup" in file):
            project_file = path_to_gns3_project+"/"+file
    with open(project_file) as file:
        data = json.load(file)
        nodes = data["topology"]["nodes"]
        for node in nodes:
            hostname = node["name"][1:]
            id = node["node_id"]
            correspondance_dict[hostname] = id
    return correspondance_dict


def new_dynamips(correspondances):
    new_config_files_names = os.listdir("./autoconfig-result")
    os.mkdir("./autoconfig-result/dynamips")
    for filename in new_config_files_names:
        pos_underscore = filename.index("_")
        hostname = filename[1:pos_underscore]
        try:
            routeur_dossier = "./autoconfig-result/dynamips/" + correspondances[hostname]
            os.mkdir(routeur_dossier)
            os.mkdir(routeur_dossier + "/configs")
            shutil.move("./autoconfig-result/" + filename, routeur_dossier + "/configs")
        except KeyError:
            print("ERREUR DANS AUTO_DEPLACEMENT (mais qui a sûrement sa source dans la définition des routeurs)")
            print("Dans le projet GNS3 existant, il n'y a pas de routeur "+hostname)


