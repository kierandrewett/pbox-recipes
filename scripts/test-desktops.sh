#!/bin/sh
# Real Ansible installation, startup, reconnect and idempotence in a disposable guest.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
container=$(docker run -d --label pbox.test=desktop-recipes debian:13 sleep infinity)
cleanup() {
    if [ "$(docker inspect -f '{{ index .Config.Labels "pbox.test" }}' "$container")" = desktop-recipes ]; then
        docker rm -f "$container" >/dev/null
    fi
}
trap cleanup EXIT HUP INT TERM
docker exec "$container" sh -c 'apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends ansible-core && useradd -m pbox'
docker cp "$root/." "$container:/recipes"
for pass in 1 2; do
    result=$(docker exec -e ANSIBLE_ROLES_PATH=/recipes/roles "$container" ansible-playbook -i localhost, -c local \
        /recipes/playbooks/desktop/xfce.yml /recipes/playbooks/desktop/mate.yml /recipes/playbooks/desktop/lxqt.yml)
    printf '%s\n' "$result"
    if [ "$pass" = 2 ]; then
        printf '%s\n' "$result" | tail -3 | grep 'changed=0 '
    fi
done
for session in xfce mate lxqt; do
    first=$(docker exec "$container" /usr/local/bin/pbox-desktop --session "$session")
    second=$(docker exec "$container" /usr/local/bin/pbox-desktop --session "$session")
    test "$first" = "$second"
    printf '%s\n' "$first"
done
