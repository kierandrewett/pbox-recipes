# pbox recipes

Small, distro-aware Ansible recipes for boxes managed by [pbox](https://github.com/kierandrewett/pbox).

Recipes run on the controller through pbox's authenticated guest agent. The agent must already be installed and reachable; recipes are the configuration layer after box creation, not the agent bootstrap layer.

## Recipes

Desktop recipes install the environment, TigerVNC and a persistent session launcher.
They currently target Debian and Ubuntu guests. Apply `desktop/xfce`,
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

| ID | Kind | Purpose |
| --- | --- | --- |
| `agent/health` | playbook | Verify the installed agent binary and its service or workspace supervisor. |
| `workspace/layout` | playbook | Create the standard pbox project, scratch, and user-bin directories. |
| `workspace-tools` | role | Install a small developer tool baseline and configure the pbox project directory. |

List and apply them with:

```text
pbox recipe sync
pbox recipe list
pbox recipe apply agent/health --box-id pbx_...
pbox recipe apply workspace/layout --box-id pbx_...
pbox recipe apply workspace-tools --box-id pbx_...
```

The recipes intentionally avoid installing or restarting `pbox-agent`. That service is part of the box control plane and is bootstrapped by `pbox new`; changing it from a recipe would remove the transport needed to run the recipe itself.

Recipes are trusted controller-side code. Review changes before applying them to a box.
