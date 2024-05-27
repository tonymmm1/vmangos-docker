#!/usr/bin/env python3
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Description:
#This file will serve as the setup for this project
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import argparse
import fileinput
import os
import platform
import re
import shutil
import subprocess
import sys
import time

from argparse import RawTextHelpFormatter

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Variable declaration
debug = 0           #Debug toggle: 0. Disable,1. Enable
path = os.getcwd()  #Sets defaults path to project directory
mode = 0            #Mode variable

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
print('Beginning VMaNGOS setup')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Dependency checks

#Check if OS is 64bit
if (platform.architecture()[0] != '64bit'):
	print ("Operating system is not 64bit", platform.architecture()[0])
	quit()

#Check if Git version is 1.8.3+
git_version = subprocess.run(["git","version"],encoding="utf-8",stdout=subprocess.PIPE,universal_newlines=True).stdout
git_parse = re.findall(r'\d+',git_version)
if (git_parse[0] < '1' and git_parse[1] < '8' and git_parse[2] < '3'):
    print ("Git version is not 1.8.3+",git_version)
    quit()
		
#Check if Python is 3.5.0+
if (sys.version_info.major < 3 and sys.version_info.minor < 5):
	print ("\nERROR: Python version",platform.python_version(),"is not 3.5+")
	quit()

#Check for docker version 18.06.0+
docker_version = subprocess.run(["docker","version","--format","'{{.Server.Version}}'"],encoding="utf-8",stdout=subprocess.PIPE,universal_newlines=True).stdout
docker_parse = re.findall(r'\d+',docker_version)
if (docker_parse[0] < '18' and docker_parse[1] < '06' and docker_parse[2] < '00'):
	print("Docker engine is older than 18.06.00",docker_version)

#Check for docker-compose version 1.22.0+
compose_version = subprocess.run(["docker-compose","version","--short"],stdout=subprocess.PIPE,encoding="utf-8").stdout
if (compose_version < "1.22.0"):
	print("Docker Compose is older than 1.22.0",compose_version)
	quit()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Mode prompt

parser = argparse.ArgumentParser(description="Vmangos-Docker cli", formatter_class=RawTextHelpFormatter)

parser.add_argument("-m", help="Select mode\n\t0 = default(default)\n\t3 = reset all files\n\t4 = ccache clean\n\t5 = Docker clean", default="0", type=int)
parser.add_argument("--update", help="Use update mode", action="store_true")
parser.add_argument("-t", help="Input number of threads to use for compiling, values 1-2(2 default) for <4GB ram", default="2", type=int)
parser.add_argument("-c", default = "5875",
    help="Input Client version to compile\n"
       "\t4222 = 1.2.4\n"  
       "\t4297 = 1.3.1\n"
       "\t4375 = 1.4.2\n"
       "\t4449 = 1.5.1\n"
       "\t4544 = 1.6.1\n"
       "\t4695 = 1.7.1\n"
       "\t4878 = 1.8.4\n"
       "\t5086 = 1.9.4\n"
       "\t5302 = 1.10.2\n"
       "\t5464 = 1.11.2\n"
       "\t5875 = 1.12.1(default)\n"
        ,type=int)
parser.add_argument("-a", help="Enable anticheat\n\t0 = Disable Anticheat(default)\n\t1 = Enable Anticheat", default="1", type=int)
parser.add_argument("--ccache", help="Clean CCache(exclusive)", action="store_true")
parser.add_argument("--docker", help="Docker Clean(exclusive)", action="store_true")
parser.add_argument("-v", help="Increase output verbosity", action="store_true")

args = parser.parse_args()

#args.v
if args.v:
    debug = 1
    print('debug> verbose mode on')
else:
    debug = 0

#args.m
if (args.m == 0):
    mode = 0
    if (args.update):
        mode = 2
elif (args.m == 3):
    mode = 3
else:
    print("Invalid mode")
    quit()

#args.t
if args.t:
    threads = args.t
    if(debug == 1):
        print('debug> threads =', args.t)

#args.c
if (args.c == 4222):
    client = 0
    client_build = args.c
elif (args.c == 4297):
    client = 1
    client_build = args.c
elif (args.c == 4375):
    client = 2
    client_build = args.c
elif (args.c == 4449):
    client = 3
    client_build = args.c
elif (args.c == 4544):
    client = 4
    client_build = args.c
elif (args.c == 4695):
    client = 5
    client_build = args.c
elif (args.c == 4878):
    client = 6
    client_build = args.c
elif (args.c == 5086):
    client = 7
    client_build = args.c
elif (args.c == 5302):
    client = 8
    client_build = args.c
elif (args.c == 5464):
    client = 9
    client_build = args.c
elif (args.c == 5875):
    client = 10
    client_build = args.c
else:
    print("Client version is incorrect")
    quit()

#args.a
if args.a:
    anticheat = args.a
    if(debug == 1):
        print('debug> anticheat =', args.a)

#args.ccache-cleaner
if args.ccache:
    mode = 4
    if(debug == 1):
        print('debug> ccache cleaner =',args.ccache-cleaner)

#args.docker-cleaner
if args.docker:
    mode = 5
    if(debug == 1):
        print('debug> docker cleaner =',args.docker-cleaner)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def git_submodules():
    global debug    #Global debug variable
    global threads  #Global threads variable
    #Fetches updates from git submodules head
    subprocess.run(['git','submodule','update','--init','--remote','--recursive'],check=True)   #git submodule update --init --remote --recursive -j $(nprocs)
    if(debug == 1):
        #Displays git submodule status
        print("debug> git submodule status")
        subprocess.run(['git','submodule','status'],check=True) #git submodule status

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def docker_build():
    global debug        #Global debug variable
    global mode         #Global mode variable 
    global threads      #Global threads variable
    global client       #Global client variable
    global client_build #Global client_build variable
    global anticheat    #Global anticheat variable
    global compose      #Global compose variable

    #Builds vmangos_build,compiles vmangos src, and outputs binaries
    subprocess.run(['docker','build','-t','vmangos_build','-f','docker/build/Dockerfile','.'])

    subprocess.run( 
            ['docker','run',                                        #docker run \
                '-v',os.path.join(path,'vmangos:/vmangos'),         #   -v $(pwd)/vmangos:/vmangos \
                '-v',os.path.join(path,'src/database:/database'),   #   -v $(pwd)/src/database:/database \
                '-v',os.path.join(path,'src/ccache:/ccache'),       #   -v $(pwd)/src/ccache:/ccache \
                '-e','CCACHE_DIR=/ccache',                          #   -e CCACHE_DIR=/ccache \
                '-e','threads=' + str(threads),                     #   -e threads=$(nprocs) \
                '-e','CLIENT=' + str(client_build),                      #   -e CLIENT=5875 \
                '-e','ANTICHEAT=' + str(anticheat),                 #   -e ANTICHEAT=0 \
                '--rm',                                             #   --rm \
                'vmangos_build'],                                   #   vmangos_build
                )
         
    #Adjusts filepath in docker-compose depending on client version
    if (client_build != 5875):
        with fileinput.FileInput(compose, inplace=True) as file:
            for line in file:
                print(line.replace('./src/data/5875','./src/data/' + str(client_build) + ':ro'),end='')
        with fileinput.FileInput('config/mangosd.conf',inplace=True) as file: 
            for line in file:
                print(line.replace('WowPatch = 10','WowPatch = ' + str(client)),end='')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setup():
    global debug        #Global debug variable
    global mode         #Global mode variable
    global compose      #Global compose variable
    
    print("Beginning setup")

    #Merging all sql migrations
    os.chdir("src/core/sql/migrations")         #cd /src/core/sql/migrations
    subprocess.run(["chmod","+x","merge.sh"])   #chmod +x merge.sh
    subprocess.run(["./merge.sh"])              #./merge.sh
    os.chdir(path)                              #cd path 

    #Starts database container in the background
    subprocess.run(['docker-compose','up','-d'])   #docker-compose -f docker-compose.yml up -d

    print("\nSetup is complete\n\nPlease wait a few minutes while database is being built\n")

    subprocess.run(['docker-compose','ps'])    #docker-compose -f docker-compose.yml/noweb-docker-compose.yml ps

    exit()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def update():
    global debug    #Global debug variable
    global mode     #Global mode variable
    global compose

    print ('Beginning updates')

    #destroys all containers without harming volumes
    subprocess.run(['docker-compose','down'])   #docker-compose -f docker-compose.yml/noweb-docker-compose.yml down

    subprocess.run(['git','pull'],check=True)      #git pull
    subprocess.run(['git','status'],check=True)    #git status
    git_submodules()    #updates git_submodules
    docker_build()      #builds vmangos
   
    #Merging all sql migrations
    os.chdir("src/core/sql/migrations")             #cd /src/core/sql/migrations
    subprocess.run(["chmod","+x","merge.sh"])       #chmod +x merge.sh
    subprocess.run(["./merge.sh"])                  #./merge.sh
    os.chdir(path)                                  #cd path 

    #Builds new containers without cached image layers
    subprocess.run(['docker-compose','build'])    #docker-compose build --no-cache

    #Builds vmangos_database
    subprocess.run(['docker-compose','up','-d','vmangos_database']) #docker-compose up -d vmangos_database

    time.sleep(30)

    print('Updating mangos database')
    #docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql'
    subprocess.run("docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql'",shell=True)

    print('Updating characters database')
    #docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/migrations/characters_db_updates.sql'
    subprocess.run("docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/migrations/characters_db_updates.sql'",shell=True) 

    print('Updating realmd database')
    #docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD realmd < /opt/vmangos/sql/migrations/logon_db_updates.sql'
    subprocess.run("docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD realmd < /opt/vmangos/sql/migrations/logon_db_updates.sql'",shell=True)

    print('Updating logs database')
    #docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/vmangos/sql/migrations/logon_db_updates.sql'
    subprocess.run("docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/vmangos/sql/migrations/logs_db_updates.sql'",shell=True)

    #rebuilds containers with any new changes
    subprocess.run(['docker-compose','up','-d'])    #docker-compose up -d

    #Run docker system prune
    subprocess.run(['docker','ps'],check=True)
    
    print ("\nExiting")
    exit()              #exits program

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def reset():
    if (debug == 1):
        print('debug> Before git status')
        subprocess.run(['git','status'],check=True)

    print('\nBeginning reset')
#    subprocess.run(['git','clean','-fd'],check=True)               #git clean -fd
    subprocess.run(['git','reset','--hard','master'],check=True)   #git reset --hard master
    subprocess.run(['git','checkout','master'],check=True)         #git checkout master
    print('\nReset complete')
   
    if (debug == 1):
        print ("\nExiting")
    exit()  #exists program

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Ccache clean
def ccache_clean():
    ccache_size = subprocess.run(['du','-sh','src/ccache'],stdout=subprocess.PIPE,encoding="utf-8")
    print ('Ccache size:', ccache_size.stdout.strip())
    shutil.rmtree('src/ccache') #rm -rf src/ccache

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Docker clean
def docker_clean():
    subprocess.run(['docker','system','prune'],check=True)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Mode declarations

#Mode 1: default 
if (mode == 0):
    git_submodules()
    docker_build()
    setup()

#Mode 2: update
elif (mode == 2):
    update()

#Mode 3: reset
elif (mode == 3):
    reset()

#Mode 4: ccache_clean
elif (mode == 4):
    ccache_clean()

#Mode 5: docker_clean
elif (mode == 5):
    docker_clean()
