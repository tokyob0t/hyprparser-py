from src import Color, Gradient, HyprData, Setting

if __name__ == '__main__':
    if not HyprData.get_option(
        'input:numlock_by_default'
    ):  # if option doesnt exists add a new setting
        HyprData.new_option(Setting('input:numlock_by_default', True))
    else:
        print(HyprData.get_option('input:numlock_by_default'))

    if not HyprData.get_option('general:col.active_border'):
        HyprData.new_option(
            Setting(
                'general:col.active_border',
                Gradient(
                    angle=0,
                    colors=[
                        Color('ff', '00', '00'),
                        Color('00', 'ff', '00'),
                        Color('00', '00', 'ff'),
                    ],
                ),
            )
        )
    tmp = HyprData.get_option('general:col.active_border')
    if tmp:
        print(tmp.format())
    # HyprData.save_all()
