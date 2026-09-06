#!/bin/sh
# Install the language and editor recipes in a disposable Debian guest twice.
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
container=$(docker run -d --label pbox.test=software-recipes debian:13 sleep infinity)
cleanup() {
    docker rm -f "$container" >/dev/null 2>&1 || true
}
trap cleanup EXIT HUP INT TERM

docker exec "$container" sh -c \
    'apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends ansible-core'
docker cp "$root/." "$container:/recipes"

for pass in 1 2; do
    docker exec -e ANSIBLE_ROLES_PATH=/recipes/roles "$container" \
        ansible-playbook -i localhost, -c local \
        /recipes/playbooks/dev/base.yml \
        /recipes/playbooks/language/python.yml \
        /recipes/playbooks/language/node.yml \
        /recipes/playbooks/language/rust.yml \
        /recipes/playbooks/language/go.yml \
        /recipes/playbooks/language/java.yml \
        /recipes/playbooks/ide/neovim.yml \
        >"/tmp/pbox-software-pass-$pass.log"
    tail -3 "/tmp/pbox-software-pass-$pass.log"
done

grep 'changed=0 ' /tmp/pbox-software-pass-2.log
