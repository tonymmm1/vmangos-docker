#!/usr/bin/env python3
#This file will serve as the setup for this project

import os
import shutil
import subprocess

#Variable declaration
debug = 0           #Debug toggle: 0. Disable,1. Enable
path = os.getcwd()  #Sets defaults path to project directory

print('Beginning VMaNGOS setup')

while True:
    try:
        mode = int(input('\nSelect mode\nmode 0: website\nmode 1: no website\nmode 2: update\nmode 3: reset all files\ninput: '))

        #modes:
        #0. website
        #1. no website
        #2. update
        #3. reset

        break
    except KeyboardInterrupt:   #Exit program with keyboard interrupt
        print('\n')
        exit()
    except TypeError:   #Error if not integer
        print ('\nInput is invalid')
        continue

if (mode != 3):
    while True:
        try:
            threads = int(input('Input number of threads to use for compiling\nRecommended values 1-2 for <4GB ram\nInput: '))
            break
        except KeyboardInterrupt:   #Exit program with keyboard interrupt
            print('\n')
            exit()
        except TypeError:   #Error if not integer
            print ('\nInput is invalid')
            continue

if (debug == 1):
    print("\ndebug:>input:",mode)

def git_submodules():
    global debug    #Global debug variable

    #Initializes git submodules
    subprocess.run(['git','submodule','init'])                              #git submodule init

    #Fetches updates from git submodules head
    subprocess.run(['git','submodule','update','--remote','--recursive'])   #git submodule update --remote --recursive
    if(debug == 1):
        #Displays git submodule status
        print("\nGit submodules:")
        subprocess.run(['git','submodule','status'])                            #git submodule status

def docker_build():
    global mode     #Global mode variable 
    global threads  #Global threads variable
    global debug    #Global debug variable

    #Builds vmangos_build,compiles vmangos src, and outputs binaries
    subprocess.run(['docker','build','-t','vmangos_build','-f','docker/build/Dockerfile','.'])
    subprocess.run( 
            ['docker','run',                                        #docker run \
                '-v',os.path.join(path,'vmangos:/vmangos'),         #   -v $(pwd)/vmangos:/vmangos \
                '-v',os.path.join(path,'src/database:/database'),   #   -v $(pwd)/src/database:/database \
                '-v',os.path.join(path,'src/ccache:/ccache'),       #   -v $(pwd)/src/ccache:/ccache \
                '-e','CCACHE_DIR=/ccache',                          #   -e CCACHE_DIR=/ccache \
                '-e','threads=' + str(threads),                      #   -e threads=$(nprocs) \
                '--rm',                                             #   --rm \
                'vmangos_build'])                                   #   vmangos_build
            
    if(mode == 0):

        with open(path + '/docker/database/generate-db-1.sql',"a+") as file:
            #Creates user and database for website
            file.write("CREATE DATABASE fusiongen;\n")
            file.write("create user 'fusiongen'@'localhost' identified by 'fusiongen';\n")
            file.write("SET PASSWORD FOR 'fusiongen'@'localhost' = PASSWORD('fusiongen');\n")
            file.write("grant all on fusiongen.* to fusiongen@'localhost' with grant option;\n")
            file.write("flush privileges;")
            file.close()
         
    elif(mode == 1):
        
        #Copies docker-compose.yml to web-docker.compose.yml
        shutil.copyfile('docker-compose.yml','web-docker-compose.yml')          #cp docker-compose.yml web-docker-compose.yml

        #Replaces docker-compose.yml with contents of noweb-docker-compose.yml
        shutil.copyfile('noweb-docker-compose.yml','docker-compose.yml')        #cp noweb-docker-compose.yml docker-compose.yml

        if(debug == 1):
            print(os.lsdir())

def setup():
    global debug
    global mode
    
    print("Beginning setup")

    #Merging all sql migrations
    os.chdir("src/core/sql/migrations")        #cd /src/core/sql/migrations
    subprocess.run(["chmod","+x","merge.sh"])   #chmod +x merge.sh
    subprocess.run(["./merge.sh"])              #./merge.sh
    os.chdir(path)                              #cd path 

    #Starts database container in the background
    subprocess.run(['docker-compose','up','-d'])             #docker-compose up -d 

    exit()

def update():
    global debug    #Global debug variable

    print ('Beginning updates')

    #destroys all containers without harming volumes
    subprocess.run(['docker-compose','down'])   #docker-compose down

    subprocess.run(['git','pull'])      #git pull
    subprocess.run(['git','status'])    #git status
    git_submodules()    #updates git_submodules
    docker_build()      #builds vmangos
   
    #Merging all sql migrations
    os.chdir("src/core/sql/migrations")        #cd /src/core/sql/migrations
    subprocess.run(["chmod","+x","merge.sh"])   #chmod +x merge.sh
    subprocess.run(["./merge.sh"])              #./merge.sh
    os.chdir(path)                              #cd path 

    #Builds new containers without cached image layers
    subprocess.run(['docker-compose','build','--no-cache',])    #docker-compose build --no-cache

    #Builds vmangos_database
    subprocess.run(['docker-compose','up','-d','vmangos_database']) #docker-compose up -d vmangos_database

    print('Updating mangos database')
    #docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql'
    subprocess.run(['docker-compose','exec','vmangos_database','sh','-c',"'mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql'"])
    
    print('Updating characters database')
    #docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/migrations/characters_db_updates.sql'
    subprocess.run(['docker-compose','exec','vmangos_database','sh','-c',"'mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql'"])
    
    #updates mysql syntax to mariadb
    #docker-compose exec vmangos_database sh -c 'mysql_upgrade -u root -p$MYSQL_ROOT_PASSWORD'
    subprocess.run(['docker-compose','exec','sh','-c',"'mysql_upgrade -u root -p$MYSQL_ROOT_PASSWORD'"])
   
    #rebuilds containers with any new changes
    subprocess.run(['docker-compose','up','-d'])    #docker-compose up -d

    exit()              #exits program

def reset():

    print('\nBeginning reset')
    subprocess.run(['git','clean','-fd'])               #git clean -fd
    subprocess.run(['git','checkout','master'])         #git checkout master
    subprocess.run(['git','reset','--hard','master'])   #git reset --hard master
    print('\nReset complete')
    
    exit()  #exists program

#Calls functions

#Modes 0
if (mode == 0):
    git_submodules()
    docker_build()
    setup()

#Mode 1
if (mode == 1):
    git_submodules()
    docker_build()
    setup()

#Mode 2
elif (mode == 2):
    update()

#Mode 3
elif (mode == 3):
    reset()






