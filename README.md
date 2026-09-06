# pbox recipes

Ansible recipes for installing tools in [pbox](https://github.com/kierandrewett/pbox)
environments.

[Get started](#get-started) · [Catalogue](#catalogue) ·
[Guest support](#guest-support) · [Troubleshooting](#troubleshooting) ·
[Contributing](CONTRIBUTING.md)

## Get started

Start with a [running box](https://github.com/kierandrewett/pbox#quick-start)
and a reachable agent, plus
[Ansible](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html)
and [Git](https://git-scm.com/downloads) installed on the machine running the CLI.

```sh
pbox recipe list
pbox recipe info language/rust
pbox recipe apply --box-id current dev/base language/rust
pbox ssh current
```

`current` selects the only box. With several boxes, use its ID or unique name.
Pbox downloads this repository automatically; no manual clone or Ansible
inventory is needed.

Recipes run in the order given. After installing tools, open a new shell to pick
up any added environment settings.

### Example setups

| Setup | Apply |
| --- | --- |
| Rust with a terminal editor | `pbox recipe apply --box-id current dev/base language/rust ide/neovim` |
| Node.js with a coding agent | `pbox recipe apply --box-id current dev/base language/node agent/codex` |
| Desktop with browser and IDE | `pbox recipe apply --box-id current desktop/xfce browser/firefox ide/vscode` |

For the desktop setup, install [TigerVNC viewer](https://tigervnc.org/) locally,
then run:

```sh
pbox desktop current
```

Coding-agent recipes install the programs and their runtime dependencies.
Complete the provider's authentication inside the box when you first run the
agent. Graphical IDEs and browsers need a running desktop session.

## Catalogue

Recipe IDs link to their playbooks so you can see what each installs.

### Development tools and languages

| Recipe | Installs |
| --- | --- |
| [dev/base](playbooks/dev/base.yml) | Git, curl, ripgrep, tmux, archive tools, compilers and build dependencies |
| [language/python](playbooks/language/python.yml) | Python, pip and distribution-specific development packages |
| [language/node](playbooks/language/node.yml) | Node.js and npm |
| [language/rust](playbooks/language/rust.yml) | rustup, stable Rust, Cargo, rustfmt and Clippy |
| [language/go](playbooks/language/go.yml) | Go |
| [language/java](playbooks/language/java.yml) | JDK with java and javac |

Most languages use the guest distribution's packages, so versions depend on its
repositories. Rust uses rustup and a shared, root-owned installation under
`/opt/pbox/rustup` and `/opt/pbox/cargo`. It is not a per-user rustup installation.

### Editors and IDEs

| Recipe | Installs |
| --- | --- |
| [ide/vscode](playbooks/ide/vscode.yml) | Visual Studio Code vendor packages; the Arch path uses its distribution `code` package |
| [ide/zed](playbooks/ide/zed.yml) | Zed; Arch package or upstream installer for the `pbox` user |
| [ide/neovim](playbooks/ide/neovim.yml) | Neovim |
| [ide/emacs](playbooks/ide/emacs.yml) | Emacs |
| [ide/helix](playbooks/ide/helix.yml) | Helix (`hx`) |

### Coding agents

| Recipe | Command |
| --- | --- |
| [agent/codex](playbooks/agent/codex.yml) | `codex` |
| [agent/claude-code](playbooks/agent/claude-code.yml) | `claude` |
| [agent/gemini-cli](playbooks/agent/gemini-cli.yml) | `gemini` |
| [agent/opencode](playbooks/agent/opencode.yml) | `opencode` |

These install Node.js/npm prerequisites and npm packages under `/opt/pbox/npm`.
Commands are made available in `/usr/local/bin`. Reapplying installs missing
npm packages; it does not automatically upgrade every installed agent.

These coding agents are separate from **pbox-agent**, which provides access to
the box. Pbox installs that service during box creation.

### Browsers

| Recipe | Browser |
| --- | --- |
| [browser/firefox](playbooks/browser/firefox.yml) | Firefox |
| [browser/chromium](playbooks/browser/chromium.yml) | Chromium |
| [browser/brave](playbooks/browser/brave.yml) | Brave |
| [browser/vivaldi](playbooks/browser/vivaldi.yml) | Vivaldi |
| [browser/zen](playbooks/browser/zen.yml) | Zen Browser |
| [browser/helium](playbooks/browser/helium.yml) | Helium |
| [browser/epiphany](playbooks/browser/epiphany.yml) | GNOME Web |
| [browser/falkon](playbooks/browser/falkon.yml) | Falkon |

Vendor browsers can add repositories or run upstream installers. Arch paths for
Brave, Vivaldi and Helium use `yay` as the `pbox` user when the package is
missing; that user and AUR helper must already exist.

### Desktops

| Recipe | Session name |
| --- | --- |
| [desktop/xfce](playbooks/desktop/xfce.yml) | `xfce` |
| [desktop/mate](playbooks/desktop/mate.yml) | `mate` |
| [desktop/lxqt](playbooks/desktop/lxqt.yml) | `lxqt` |

Each installs its desktop, TigerVNC and a persistent session launcher.
When several desktops are installed, select one:

```sh
pbox desktop current --session lxqt
```

Closing the viewer preserves applications. Logging out ends the session;
stopping the box ends all sessions. The supplied sessions use X11.
See [pbox desktop help](https://github.com/kierandrewett/pbox/blob/main/docs/desktop.md).

### Workspace and diagnostics

| Recipe | Purpose |
| --- | --- |
| [workspace/layout](playbooks/workspace/layout.yml) | Create projects, scratch and user-bin directories; use a root-owned fallback if no `pbox` user exists |
| [agent/health](playbooks/agent/health.yml) | Check the installed pbox-agent binary and its supervisor |
| [workspace-tools](roles/workspace-tools/tasks/main.yml) | Older small baseline role: curl, Git, tmux, Vim and workspace setup |

Use `dev/base` for the current distribution-specific development baseline.
`agent/health` needs a working agent connection to run; it cannot repair a
disconnected agent.

## Guest support

| Recipes | Guest families targeted by the current playbooks |
| --- | --- |
| General software, languages, editors and coding agents | Debian/Ubuntu, Arch/CachyOS, Red Hat/Fedora and SUSE |
| Desktop recipes | Debian/Ubuntu and Arch/CachyOS |
| Vivaldi | Debian/Ubuntu and Arch/CachyOS |
| Helium | Debian/Ubuntu, Red Hat/Fedora and Arch/CachyOS |

Family support is not a guarantee for every distribution release or CPU
architecture. Packages, vendor repositories and upstream installers must support
the actual guest. Check [the manifest](pbox.yml) and the linked playbook before
choosing a recipe.

- Desktops and Zen require the `pbox` account. Zed's non-Arch installer also uses it.
- Installing missing Arch dependencies can perform a full system upgrade.
- Alpine can run a compatible pbox agent, but most software recipes here do not
  provide Alpine package mappings.

## Refresh recipes

```sh
pbox recipe sync
pbox recipe search browser
```

`sync` updates the local recipe checkout. It does not update software in boxes.
For a different repository revision:

```sh
pbox config set recipes.ref main
pbox recipe sync
```

## Troubleshooting

| Problem | Next step |
| --- | --- |
| `ansible-playbook` missing | Install Ansible on the machine running pbox |
| Guest Python missing | Install `python3` in the guest if pbox's preparation cannot provide it |
| Unsupported distribution | Read the playbook's package-family check and select a supported recipe/image |
| `yay` or `pbox` user missing | Prepare the prerequisites for that Arch vendor recipe |
| Command unavailable in an existing shell | Reconnect with `pbox ssh BOX` to reload login environment settings |
| Recipe task failed | Read the reported log or rerun with `--verbose` |
| Agent connection failed | Use pbox's connection/repair commands before applying recipes |

```sh
pbox --verbose recipe apply --box-id current dev/base
```

Recipes can change the guest with root privileges and execute Ansible code
locally. Review the source you choose to run. Pbox's
[rollback policy](https://github.com/kierandrewett/pbox/blob/main/docs/recipes.md#rollback-and-storage)
depends on Proxmox storage support; without a checkpoint, failures can leave
partial changes.

[Report a recipe issue](https://github.com/kierandrewett/pbox-recipes/issues)
with the recipe ID, guest distribution/version, architecture and relevant error.
Remove credentials from logs before sharing.
