# pbox recipes

Small, distro-aware Ansible recipes for boxes managed by [pbox](https://github.com/kierandrewett/pbox).

Recipes run on the controller through pbox's authenticated guest agent. The agent must already be installed and reachable; recipes are the configuration layer after box creation, not the agent bootstrap layer.

## Recipes

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
