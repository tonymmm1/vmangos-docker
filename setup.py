#!/usr/bin/env python3
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Description:
#This file will serve as the setup for this project
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import fileinput
import os
import shutil
import subprocess

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Variable declaration
debug = 0           #Debug toggle: 0. Disable,1. Enable
path = os.getcwd()  #Sets defaults path to project directory

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
print('Beginning VMaNGOS setup')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Mode prompt
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

if(debug == 1):
    print("debug> mode:",mode)

#Run if not reset mode
if (mode != 3):

    #User prompt
    while True:
        try:
            user_input = int(input('Use user:group 1000:1000 for permissions\n0. No\n1. Yes\nInput: '))
            break
        except KeyboardInterrupt:   #Exit program with keyboard interrupt
            print('\n')
            exit()
        except TypeError:   #Error if not integer
            print ('\nInput is invalid')
            continue
    
    if (user_input == 0):
        user = input('Input user:group string for permissions')

        if(debug == 1):
            print('debug> user:group =',user)

    #Threads prompt
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

    if(debug == 1):
        print ('debug> threads:',threads)

    #Client build prompt
    while True:
        try:
            client = int(input('Input Client version to compile\n0. Client Build 1.2.4 4222\n1. Client Build 1.3.1 4297\n2. Client Build 1.4.2 4375\n3. Client Build 1.5.1 4449\n4. Client Build 1.6.1 4544\n5. Client Build 1.7.1 4695\n6. Client Build 1.8.4 4878\n7. Client Build 1.9.4 5086\n8. Client Build 1.10.2 5302\n9. Client Build 1.11.2 5464\n10. Client Build 1.12.1 5875\n11. Custom\nInput: '))
            break
        except KeyboardInterrupt:   #Exit program with keyboard interrupt
            print('\n')
            exit()
        except TypeError:   #Error if not integer
            print ('\nInput is invalid')
            continue

    if (debug == 1):
        print('debug> client',client)

    #Matches input to appropriate client string
    if(client == 0):
        client_build = "4222"
    elif(client == 1):
        client_build = "4297"
    elif(client == 2):
        client_build = "4375"
    elif(client == 3):
        client_build = "4449"
    elif(client == 4):
        client_build = "4544"
    elif(client == 5):
        client_build = "4695"
    elif(client == 6):
        client_build = "4878"
    elif(client == 7):
        client_build = "5086"
    elif(client == 8):
        client_build = "5302"
    elif(client == 9):
        client_build = "5464"
    elif(client == 10):
        client_build = "5875"
    elif(client == 11):
        client_build = input('Input Client Builds separated by commas\nInput: ')

    if(debug == 1):
        print ("debug> client build:",client_build)


    #Anticheat prompt
    while True:
        try:
            anticheat = int(input('Enable anticheat\n0. Disabled\n1.Enabled\nInput: '))
            break
        except KeyboardInterrupt:   #Exit program with keyboard interrupt
            print('\n')
            exit()
        except TypeError:   #Error if not integer
            print ('\nInput is invalid')
            continue

    if (debug == 1):
    print("\ndebug> anticheat:",anticheat)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def git_submodules():
    global debug    #Global debug variable

    #Initializes git submodules
    subprocess.run(['git','submodule','init'])                              #git submodule init

    #Fetches updates from git submodules head
    subprocess.run(['git','submodule','update','--remote','--recursive'])   #git submodule update --remote --recursive
    if(debug == 1):
        #Displays git submodule status
        print("debug> git submodule status")
        subprocess.run(['git','submodule','status'])                            #git submodule status

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def docker_build():
    global debug        #Global debug variable
    global mode         #Global mode variable 
    global threads      #Global threads variable
    global client       #Global client variable
    global client_build #Global client_build variable
    global anticheat    #Global anticheat variable

    #Builds vmangos_build,compiles vmangos src, and outputs binaries
    subprocess.run(['docker','build','-t','vmangos_build','-f','docker/build/Dockerfile','.'])
    subprocess.run( 
            ['docker','run',                                        #docker run \
                '-v',os.path.join(path,'vmangos:/vmangos'),         #   -v $(pwd)/vmangos:/vmangos \
                '-v',os.path.join(path,'src/database:/database'),   #   -v $(pwd)/src/database:/database \
                '-v',os.path.join(path,'src/ccache:/ccache'),       #   -v $(pwd)/src/ccache:/ccache \
                '-e','CCACHE_DIR=/ccache',                          #   -e CCACHE_DIR=/ccache \
                '-e','threads=' + str(threads),                     #   -e threads=$(nprocs) \
                '-e','CLIENT=' + client_build,                      #   -e CLIENT=5875 \
                '-e','ANTICHEAT=' + str(anticheat),                 #   -e ANTICHEAT=0 \
                '--rm',                                             #   --rm \
                'vmangos_build'])                                   #   vmangos_build
         
    #Web
    if(mode == 0):
        with open(path + '/docker/database/generate-db-1.sql',"a+") as file:
            #Creates user and database for website
            file.write("CREATE DATABASE fusiongen;\n")
            file.write("create user 'fusiongen'@'localhost' identified by 'fusiongen';\n")
            file.write("SET PASSWORD FOR 'fusiongen'@'localhost' = PASSWORD('fusiongen');\n")
            file.write("grant all on fusiongen.* to fusiongen@'localhost' with grant option;\n")
            file.write("flush privileges;")
            file.close()

    #Non-web 
    elif(mode == 1):
        
        #Copies docker-compose.yml to web-docker.compose.yml
        shutil.copyfile('docker-compose.yml','web-docker-compose.yml')          #cp docker-compose.yml web-docker-compose.yml

        #Replaces docker-compose.yml with contents of noweb-docker-compose.yml
        shutil.copyfile('noweb-docker-compose.yml','docker-compose.yml')        #cp noweb-docker-compose.yml docker-compose.yml
      
        #Disables php-soap in /config/mangosd.conf
        with fileinput.FileInput('config/mangosd.conf', inplace=True) as file:
              for line in file:
                  print(line.replace('SOAP.Enabled = 1','SOAP.Enabled = 0'),end='')

        if(debug == 1):
            print(os.lsdir())

    #Adjusts filepath in docker-compose depending on client version
    if (client != 10 and client != 11):
        with filinput.FileInput('docker-compose.yml', inplace=True) as file:
            for line in file:
                print(line.replace('- ./src/data/5875:/opt/vmangos/bin/5875:ro','- ./src/data/' + client_build + ':/opt/vmangos/bin/' + client + ':ro'),end='')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setup():
    global debug
    global mode
    
    print("Beginning setup")

    #Setting permissions 
    with fileinput.FileInput('docker-compose.yml', inplace=True) as file:
        for line in file:
            print(line.replace('1000:1000',user),end='')

    subprocess.run(['chown','-R',user,'.']) #chown 1000:1000
    
    #Merging all sql migrations
    os.chdir("src/core/sql/migrations")         #cd /src/core/sql/migrations
    subprocess.run(["chmod","+x","merge.sh"])   #chmod +x merge.sh
    subprocess.run(["./merge.sh"])              #./merge.sh
    os.chdir(path)                              #cd path 

    #Starts database container in the background
    subprocess.run(['docker-compose','up','-d'])    #docker-compose up -d 
    
    print("Setup is complete"\n"Please wait a few minutes while database is being built")

    subprocess.run(['docker-compose','ps'])

    exit()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
    subprocess.call(['docker-compose','exec','vmangos_database','sh','-c','mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql'])
    
    print('Updating characters database')
    #docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/migrations/characters_db_updates.sql'
    subprocess.run(['docker-compose','exec','vmangos_database','sh','-c','mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/migrations/world_db_updates.sql'])
    
    #updates mysql syntax to mariadb
    #docker-compose exec vmangos_database sh -c 'mysql_upgrade -u root -p$MYSQL_ROOT_PASSWORD'
    subprocess.run(['docker-compose','exec','sh','-c','mysql_upgrade -u root -p$MYSQL_ROOT_PASSWORD'])
   
    #rebuilds containers with any new changes
    subprocess.run(['docker-compose','up','-d'])    #docker-compose up -d

    print ("\nExiting")
    exit()              #exits program

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def reset():
    if (debug == 1):
        print('debug> Before git status')
        subprocess.run(['git','status'])

    print('\nBeginning reset')
    subprocess.run(['git','clean','-fd'])               #git clean -fd
    subprocess.run(['git','checkout','master'])         #git checkout master
    subprocess.run(['git','reset','--hard','master'])   #git reset --hard master
    print('\nReset complete')
   
    if (debug == 1):
    print ("\nExiting")
    exit()  #exists program
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Mode declarations

#Modes 0: website
if (mode == 0):
    git_submodules()
    docker_build()
    setup()

#Mode 1: no-website
if (mode == 1):
    git_submodules()
    docker_build()
    setup()

#Mode 2: update
elif (mode == 2):
    update()

#Mode 3: reset
elif (mode == 3):
    reset()
