from qfluentwidgets import FluentIcon

from one_dragon.gui.component.column_widget import ColumnWidget
from one_dragon.gui.component.setting_card.combo_box_setting_card import ComboBoxSettingCard
from one_dragon.gui.component.setting_card.switch_setting_card import SwitchSettingCard
from zzz_od.application.dodge_assistant.dodge_assistant_app import DodgeAssistantApp
from zzz_od.application.dodge_assistant.dodge_assistant_config import get_dodge_op_config_list
from zzz_od.application.zzz_application import ZApplication
from zzz_od.context.zzz_context import ZContext
from zzz_od.gui.view.app_run_interface import AppRunInterface


class DodgeAssistantInterface(AppRunInterface):

    def __init__(self,
                 ctx: ZContext,
                 parent=None):
        self.ctx: ZContext = ctx

        top_widget = ColumnWidget()

        self.dodge_opt = ComboBoxSettingCard(icon=FluentIcon.GAME, title='闪避方式')
        top_widget.add_widget(self.dodge_opt)

        self.gpu_opt = SwitchSettingCard(icon=FluentIcon.GAME, title='GPU运算')
        self.gpu_opt.value_changed.connect(self._on_gpu_changed)
        top_widget.add_widget(self.gpu_opt)

        AppRunInterface.__init__(
            self,
            ctx=ctx,
            object_name='dodge_assistant_interface',
            nav_text_cn='闪避助手',
            nav_icon=FluentIcon.PLAY,
            parent=parent,
            widget_at_top=top_widget
        )

    def on_interface_shown(self) -> None:
        """
        界面显示时 进行初始化
        :return:
        """
        AppRunInterface.on_interface_shown(self)
        self._update_dodge_way_opts()
        self.dodge_opt.setValue(self.dodge_opt)
        self.gpu_opt.setValue(self.ctx.dodge_assistant_config.use_gpu)

    def _update_dodge_way_opts(self) -> None:
        """
        更新闪避指令
        :return:
        """
        try:
            self.dodge_opt.value_changed.disconnect(self._on_dodge_way_changed)
        except:
            pass
        self.dodge_opt.set_options_by_list(get_dodge_op_config_list())
        self.dodge_opt.value_changed.connect(self._on_dodge_way_changed)

    def _on_dodge_way_changed(self, index, value):
        self.ctx.dodge_assistant_config.dodge_way = value

    def _on_gpu_changed(self, value: bool):
        self.ctx.dodge_assistant_config.use_gpu = value

    def get_app(self) -> ZApplication:
        return DodgeAssistantApp(self.ctx)