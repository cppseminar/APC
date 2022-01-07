#!/bin/bash
# Check @Q - quote variable

if [[  $(  printf "%s\n" $@ | grep -A 1 -- "--directory" | wc -l )  -ne 2 ]]; then
    echo "Reuired parameter is --directory <path to new root>"
    exit 1
fi

PRIVATE_ROOT=$( printf "%s\n" $@ | grep -A 1 -- "--directory" | tail -n 1 | xargs realpath )
NS_ROOT="$PRIVATE_ROOT/namespaces/"
CONTAINER_PATH="$PRIVATE_ROOT"/privateroot/

if [ ! -d "$PRIVATE_ROOT/s6" ]; then
    echo "s6 directory doesn't exist in given --directory"
    exit 1
fi

# if [ "$( whoami )" != "root" ]; then
#     echo "Script must run as root"
#     exit 2
# fi
#

set -e

TEMP_PATH=/tmp/prepare_container.sh


function cleanns {
    umount -R "$NS_ROOT"
    rm "$NS_ROOT"/mnt
}


function act1 {
    mkdir -p "$PRIVATE_ROOT/nsroot"
    prepare

    set +e
    #cleanns
    set -e

    # echo "Creating namespace structure"
    # mkdir -p "$NS_ROOT"
    # mount --bind --make-private "$NS_ROOT" "$NS_ROOT"
    # touch "$NS_ROOT/mnt"



    echo Unsharing mount+user
    unshare  -Urm  "/bin/bash" -c "$TEMP_PATH 2 --directory \"$PRIVATE_ROOT\""
    echo End of first act
}

function act2 {
    echo "Makin dirs for mountpoints"
    mkdir  -p $CONTAINER_PATH/bin
    mkdir  -p $CONTAINER_PATH/dev
    mkdir  -p $CONTAINER_PATH/home
    mkdir  -p $CONTAINER_PATH/lib
    mkdir  -p $CONTAINER_PATH/lib64
    mkdir  -p $CONTAINER_PATH/root
    mkdir  -p $CONTAINER_PATH/etc
    mkdir  -p $CONTAINER_PATH/proc
    mkdir  -p $CONTAINER_PATH/usr
    mkdir  -p $CONTAINER_PATH/tmp
    mkdir  -p $CONTAINER_PATH/var
    mkdir  -p $CONTAINER_PATH/oldroot

    mount --bind $CONTAINER_PATH $CONTAINER_PATH
    mount --bind -o ro /bin $CONTAINER_PATH/bin
    mount --rbind -o ro /dev $CONTAINER_PATH/dev
    mount --bind -o ro /usr $CONTAINER_PATH/usr
    mount --bind -o ro /lib $CONTAINER_PATH/lib
    mount --bind -o ro /lib64 $CONTAINER_PATH/lib64
    mount --bind -o ro /etc $CONTAINER_PATH/etc
    mount --bind -o ro /var $CONTAINER_PATH/var
    mount --bind $CONTAINER_PATH/oldroot $CONTAINER_PATH/oldroot ## Check me!
    # What about home?
    # TODO: Size!!!!
    mount -t tmpfs swap $CONTAINER_PATH/tmp
    mount -t tmpfs swap $CONTAINER_PATH/home
    mkdir  -p "$CONTAINER_PATH/home/s6"
    mount -t tmpfs swap $CONTAINER_PATH/root
    # https://stackoverflow.com/questions/8148715/how-to-set-limit-on-directory-size-in-linux
    echo "Filesystem created"
    cp "$(realpath $0)" $CONTAINER_PATH/tmp/nss.sh
    pivot_root "$CONTAINER_PATH" "$CONTAINER_PATH"/oldroot
    # For umount to work, we need /proc
    mount --rbind /oldroot/proc /proc
    umount -l /oldroot
    echo "Unmounted root, from now on, we are in limited mountpoint"
    act3
}

function act3 {
    unshare -p --mount-proc --fork /usr/bin/s6-svscan /home/s6
    #unshare --mount-proc -p --fork /usr/bin/bash
    #unshare -m /bin/bash
}

function prepare {
    path=$(realpath $0)
    echo copying $path to $TEMP_PATH
    cp "$path"  $TEMP_PATH
    chmod 0755 $TEMP_PATH
}

if [ $# -ne 3 ]; then
    echo "Requires 3 args, <act number> --directory <script root>"
elif [ $1 -eq "1" ]; then
    act1
elif [ $1 -eq "2" ]; then
    act2
else
    echo "Bad argument 1"
fi
