#!/usr/bin/bash

exit_with_error() {
    >&2 echo "$1"
    exit 1
}

export_no_proxy() {
    export NO_PROXY="127.0.0.1,localhost,\
172.10.0.3,172.10.0.2,172.11.0.3,172.11.0.2,172.12.0.3,172.12.0.2,172.13.0.3,172.13.0.2,172.14.0.3,\
172.14.0.2,172.15.0.3,172.15.0.2,172.16.0.3,172.16.0.2,172.17.0.3,172.17.0.2,172.18.0.3,172.18.0.2,\
172.19.0.3,172.19.0.2,172.20.0.3,172.20.0.2,172.21.0.3,172.21.0.2,172.22.0.3,172.22.0.2,172.23.0.3,\
172.23.0.2,172.24.0.3,172.24.0.2,172.25.0.3,172.25.0.2,172.26.0.3,172.26.0.2,172.27.0.3,172.27.0.2,\
172.28.0.3,172.28.0.2,172.29.0.3,172.29.0.2,172.30.0.3,172.30.0.2,172.31.0.3,172.31.0.2,172.32.0.3,\
172.32.0.2,172.33.0.3,172.33.0.2,172.34.0.3,172.34.0.2,172.35.0.3,172.35.0.2,172.36.0.3,172.36.0.2,\
172.37.0.3,172.37.0.2,172.38.0.3,172.38.0.2,172.39.0.3,172.39.0.2,172.40.0.3,172.40.0.2,172.41.0.3,\
172.41.0.2,172.42.0.3,172.42.0.2,172.43.0.3,172.43.0.2,172.44.0.3,172.44.0.2,172.45.0.3,172.45.0.2,\
172.46.0.3,172.46.0.2,172.47.0.3,172.47.0.2,172.48.0.3,172.48.0.2,172.49.0.3,172.49.0.2,172.50.0.3,\
172.50.0.2"
}

apply_storage_class() {
    echo "Creating custom storage class local-path-retain"
    kubectl apply -f storage_class.yaml || exit_with_error
}

to_int() {
    local -i num="10#${1}"
    echo "${num}"
}

port_is_ok() {
    local port="$1"
    local -i port_num=$(to_int "${port}" 2>/dev/null)

    if (( $port_num < 1 || $port_num > 65535 )) ; then
        exit_with_error "${port} is not a valid port or is missing"
        return
    fi

    echo "Using ${port} as application port"
}

port_is_ok $1

sudo sysctl -w vm.max_map_count=262144 || exit_with_error "Unable to change max_map_count. \`sysctl\` returned non-zero exit code $?"

export_no_proxy

certs_bundle_file='/etc/ssl/certs/ca-certificates.crt'

[ -f "$certs_bundle_file" ] || exit_with_error "Cannot find OS certificate bundle file at \`$certs_bundle_file\`. Is this machine Debian-based?"

k3d cluster create traffic-monitoring -p "${1}:80@loadbalancer" --api-port 127.0.0.1:6446 \
    --env "HTTP_PROXY=$HTTP_PROXY@all:*" \
    --env "HTTPS_PROXY=$HTTPS_PROXY@all:*" \
    --env "NO_PROXY=$NO_PROXY@all:*" \
    --volume "$certs_bundle_file":/etc/ssl/certs/host_certs.crt:ro \
    --k3s-arg '--kubelet-arg=eviction-hard=imagefs.available<1%,nodefs.available<1%@agent:*' \
    --k3s-arg '--kubelet-arg=eviction-minimum-reclaim=imagefs.available=1%,nodefs.available=1%@agent:*' \
    --k3s-arg '--kubelet-arg=eviction-hard=imagefs.available<1%,nodefs.available<1%@server:0' \
    --k3s-arg '--kubelet-arg=eviction-minimum-reclaim=imagefs.available=1%,nodefs.available=1%@server:0' \
    $k3d_extra_args \
    || exit_with_error "Unable to start cluster. \`k3d cluster create\` returned non-zero exit code $?"

apply_storage_class