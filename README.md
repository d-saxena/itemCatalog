# Book Store Catalog

### Description
It is an application that provides a list of books within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own books.

### Key Features
- Supports CRUD using SQLAlchemy and Flask framework of python.
- HTML/CSS webpages
- Authentication and Authorization using OAuth of Google.

### Pre-requisite for the project
- Install the VM and Vagrant.

- If you don't already have virtual box on your machine, you can download it here: https://www.virtualbox.org/wiki/DownloadOldBuilds51 or for ubuntu type this command: sudo apt-get install virtual box

- Download and install Vagrant (if you do not already have it installed). This is the software that configures the VM and allows the host (your machine) to talk to the VM: https://www.vagrantup.com/ or for ubuntu type this commnad: sudo apt-get install vagrant ->you should be able to run vagrant --version after installation to see the version that was installed.

- Download and unzip this file:https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip This will give you a directory called FSND-Virtual-Machine. It may be located inside your Downloads folder.

Alternately, you can use Github to fork and clone the repository https://github.com/udacity/fullstack-nanodegree-vm.

- cd into this(FSND_Virtual_Machine) directory

- cd into the vagrant/ subdirectory

- Bring the VM up with the command vagrant up

- Log into the VM with vagrant ssh
