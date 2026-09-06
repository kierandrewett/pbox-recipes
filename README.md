# pbox recipes

Small, distro-aware Ansible recipes for boxes managed by [pbox](https://github.com/kierandrewett/pbox).

Recipes run on the controller through pbox's authenticated guest agent. The agent must already be installed and reachable; recipes are the configuration layer after box creation, not the agent bootstrap layer.

## Recipes

Desktop recipes install the environment, TigerVNC and a persistent session launcher.
They target Debian, Ubuntu, Arch Linux and CachyOS guests.
Arch installation performs a full package upgrade when dependencies are missing,
as required to avoid unsupported partial upgrades. Apply `desktop/xfce`,
`desktop/mate` or `desktop/lxqt`, then run `pbox desktop BOX --session xfce`
(substitute the chosen session). When only one desktop is installed the session
flag is optional. Install TigerVNC viewer on the controller to open a native window.
Closing the viewer preserves the desktop; logging out ends the session.
VNC binds guest loopback without a password; remote access uses the authenticated
agent tunnel. Other processes within the guest/controller share local access.

`desktop-vnc` is a shared Ansible role used by these playbooks, requiring
`desktop_session`, `desktop_packages` and `desktop_argv`; apply the named desktop
playbooks rather than the supporting role directly.

Run `sh scripts/test-desktops.sh` to install all three desktops in an isolated
Debian container, verify startup and reconnection, and require a second Ansible
apply to report zero changes. It uses no privileged container options or host
display mounts and removes its own container on exit.

Run `sh scripts/test-software.sh` to install the language and editor recipes in
an isolated Debian container twice and verify that the second run is idempotent.

| ID | Kind | Purpose |
| --- | --- | --- |
| `agent/health` | playbook | Verify the installed agent binary and its service or workspace supervisor. |
| `workspace/layout` | playbook | Create the standard pbox project, scratch, and user-bin directories. |
| `workspace-tools` | role | Install a small developer tool baseline and configure the pbox project directory. |
| `dev/base` | playbook | Install common CLI tools, compilers and build dependencies. |
| `browser/firefox`, `browser/chromium` | playbook | Install a desktop browser. |
| `browser/epiphany`, `browser/falkon` | playbook | Install alternative GNOME and Qt browsers. |
| `browser/brave`, `browser/vivaldi`, `browser/zen`, `browser/helium` | playbook | Install vendor and privacy-focused browsers. |
| `language/python`, `language/node`, `language/rust`, `language/go`, `language/java` | playbook | Install a language toolchain. |
| `ide/neovim`, `ide/emacs`, `ide/helix` | playbook | Install a programmer editor or IDE. |
| `ide/vscode`, `ide/zed` | playbook | Install Visual Studio Code or Zed. |
| `agent/codex`, `agent/claude-code`, `agent/gemini-cli`, `agent/opencode` | playbook | Install a coding-agent CLI through a private npm prefix. |

List and apply them with:

```text
pbox recipe sync
pbox recipe list
pbox recipe apply agent/health --box-id pbx_...
pbox recipe apply workspace/layout --box-id pbx_...
pbox recipe apply workspace-tools --box-id pbx_...
pbox recipe apply dev/base --box-id pbx_...
pbox recipe apply language/rust --box-id pbx_...
pbox recipe apply agent/codex --box-id pbx_...
```

The recipes are deliberately composable. For example, apply `dev/base`,
`language/rust`, `language/node`, `ide/neovim` and `agent/codex` separately so a
box receives only the tools it needs. The coding-agent recipes install Node.js
and npm as prerequisites and place npm packages under `/opt/pbox/npm`; command
shims are published in `/usr/local/bin`.

The recipes intentionally avoid installing or restarting `pbox-agent`. That service is part of the box control plane and is bootstrapped by `pbox new`; changing it from a recipe would remove the transport needed to run the recipe itself.

Recipes are trusted controller-side code. Review changes before applying them to a box.
