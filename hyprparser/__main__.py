from src import HyprData, Setting

if __name__ == "__main__":
    for i in [
        "general:gaps_in",
        "input:touchpad:natural_scroll",
        "general:col.active_border",
    ]:
        print(HyprData.get_option(i))

    # HyprData.set_option("general:gaps_in", 50)  # 5
    # HyprData.set_option("general:gaps_out", 20)  # 20

    if not HyprData.get_option(
        "input:numlock_by_default"
    ):  # if option doesnt exists add a new setting
        HyprData.new_option(
            "input:numlock_by_default", Setting("input:numlock_by_default", True)
        )
    else:
        print(HyprData.get_option("input:numlock_by_default"))
