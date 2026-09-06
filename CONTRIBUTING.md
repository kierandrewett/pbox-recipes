# Contributing recipes

[User guide and catalogue](README.md)

## Layout

| Path | Purpose |
| --- | --- |
| `pbox.yml` | Recipe IDs, descriptions, supported guests and capabilities |
| `playbooks/` | User-facing recipes grouped by purpose |
| `roles/software/` | Package installation, npm tools and command checks |
| `roles/desktop-vnc/` | Shared desktop installation and persistent VNC launcher |

Add the playbook, update the manifest and catalogue, and document prerequisites.
Keep declared guest support consistent with package-family checks. Run relevant
installation tests in a disposable environment before adding a supported guest.

Desktop recipes supply `desktop_session`, `desktop_packages`,
`desktop_arch_packages` and `desktop_argv`. Apply the named desktop playbooks;
the shared role is not a standalone desktop recipe.

## Tests

The integration scripts require Docker and network access. They install
software into disposable Debian containers, run recipes twice and check that
the second run reports no changes.

```sh
sh scripts/test-desktops.sh
sh scripts/test-software.sh
```

The desktop script also checks repeat startup and reconnection. The software
script covers its listed baseline, language and editor recipes, not every
browser or coding agent. Neither script proves support on other distributions
or in a real Proxmox LXC.

For desktop changes, also verify through `pbox desktop` in a disposable box:
opening, closing/reconnecting, logout and stop/start. The VNC backend binds guest
loopback and relies on pbox's authenticated tunnel for remote access.

## Scope

Recipes configure software after pbox has established guest access. The
`agent/health` recipe checks pbox-agent; agent installation and upgrades remain
part of pbox itself.

When working through pbox's `recipes/` submodule, commit and push recipe changes
here first, then update the submodule pointer in the parent repository.
