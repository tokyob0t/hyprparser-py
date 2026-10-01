# Hyprparser-py

> **Archived — Hyprland no longer uses hyprlang.**
>
> Since [Hyprland 0.55](https://hypr.land/news/26_lua) the compositor is configured
> in **Lua**, not hyprlang. Upstream will keep the old syntax working for only
> 1–2 more releases and will then drop it; no new config features land in
> hyprlang either. A parser for a config format that is being deleted has no
> reason to grow, so this repository is archived as-is.
>
> For current Hyprland configuration, see the [wiki](https://wiki.hypr.land/Configuring/Start).
> Everything below documents the old hyprlang-based library, kept for reference
> and for anyone still on a pre-0.55 setup.

A Pythonic parser for Hyprland configuration files.

---

### Example

```python
from hyprparser import Color, Gradient, HyprData, Setting

if __name__ == "__main__":

    for i in [
        "input:touchpad:natural_scroll",
        "general:col.active_border",
        "general:gaps_in",
    ]:
        print(HyprData.get_option(i))

    # HyprData.set_option("general:gaps_in", 50)  # 5
    # HyprData.set_option("general:gaps_out", 20)  # 20


    if not HyprData.get_option(
        "input:numlock_by_default"
    ):  # if option doesnt exists add a new setting
        HyprData.new_option(Setting("input:numlock_by_default", True))
    else:
        print(HyprData.get_option("input:numlock_by_default"))

    if not HyprData.get_option("general:col.active_border"):
        HyprData.new_option(
            Setting(
                "general:col.active_border",
                Gradient(0, [Color("00", "11", "22"), Color("dd", "e1", "e6")]),
            )
        )
    HyprData.save_all()


```

### API

| Call                                    | What it does                                       |
| --------------------------------------- | -------------------------------------------------- |
| `HyprData.reload()`                     | Re-reads every tracked config file from disk.      |
| `HyprData.get_option("section:key")`    | Returns the parsed `Setting`, or `None`.            |
| `HyprData.set_option("section:key", v)` | Rewrites the value, creating the section if needed. |
| `HyprData.new_option(Setting(...))`     | Appends an option that does not exist yet.         |
| `HyprData.save_all()`                   | Flushes every in-memory change to disk.             |
| `HyprData.new_env` / `get_env` / `set_env` | Same three operations for `$env` variables.     |
| `HyprData.new_bezier` / `get_bezier` / `set_bezier` | Same three operations for bezier curves. |

Value types are plain dataclasses — `Setting`, `Color`, `Gradient`, `Binding`,
`Bezier`, `Env`, `Exec`, `Variable`, `Monitor` — and each one carries a
`format()` that renders it back to hyprlang syntax plus a `to_dict()` for
serialization. Verified output:

```python
Setting('general:gaps_in', 5).format()   # 'gaps_in = 5'
Setting('input:numlock_by_default', True).format()   # 'numlock_by_default = true'
Setting('general:gaps_in', 5).to_dict()   # {'section': 'general:gaps_in', 'value': 5}
```

Set `HyprData.insta_save = True` to write each change to disk immediately
instead of waiting for `save_all()`.

### Notes

- `HyprData` is a module-level singleton pointed at
  `$HOME/.config/hypr/hyprland.conf` (expanded via `os.path.expandvars`). It is
  constructed at import time, so importing the package reads that file.
- `override_options` is an unused flag and is not part of the API.
- Requires Python 3.10+ (`match` statements). It does not import on 3.9.

## License

See the repository settings.
