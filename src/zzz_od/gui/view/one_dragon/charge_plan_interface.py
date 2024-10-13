from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from qfluentwidgets import PrimaryPushButton, FluentIcon, ComboBox, CaptionLabel, LineEdit, ToolButton
from typing import Optional, List

from one_dragon.gui.component.column_widget import ColumnWidget
from one_dragon.gui.component.interface.vertical_scroll_interface import VerticalScrollInterface
from one_dragon.gui.component.setting_card.multi_push_setting_card import MultiPushSettingCard, MultiLineSettingCard
from one_dragon.gui.component.setting_card.switch_setting_card import SwitchSettingCard
from one_dragon.utils.i18_utils import gt
from zzz_od.application.battle_assistant.auto_battle_config import get_auto_battle_op_config_list
from zzz_od.application.charge_plan.charge_plan_config import ChargePlanItem, CardNumEnum
from zzz_od.context.zzz_context import ZContext


class ChargePlanCard(MultiLineSettingCard):

    changed = Signal(int, ChargePlanItem)
    delete = Signal(int)
    move_up = Signal(int)

    def __init__(self, ctx: ZContext,
                 idx: int, plan: ChargePlanItem):
        self.ctx: ZContext = ctx
        self.idx: int = idx
        self.plan: ChargePlanItem = plan

        self.category_combo_box = ComboBox()
        self.category_combo_box.currentIndexChanged.connect(self._on_category_changed)

        self.mission_type_combo_box = ComboBox()
        self.mission_type_combo_box.currentIndexChanged.connect(self._on_mission_type_changed)

        self.mission_combo_box = ComboBox()
        self.mission_combo_box.currentIndexChanged.connect(self._on_mission_changed)

        self.card_num_box = ComboBox()
        self.card_num_box.currentIndexChanged.connect(self._on_card_num_changed)

        self.predefined_team_opt = ComboBox()
        self.predefined_team_opt.currentIndexChanged.connect(self.on_predefined_team_changed)

        self.auto_battle_combo_box = ComboBox()
        self.auto_battle_combo_box.currentIndexChanged.connect(self._on_auto_battle_changed)

        run_times_label = CaptionLabel(text='已运行次数')
        self.run_times_input = LineEdit()
        self.run_times_input.textChanged.connect(self._on_run_times_changed)

        plan_times_label = CaptionLabel(text='计划次数')
        self.plan_times_input = LineEdit()
        self.plan_times_input.textChanged.connect(self._on_plan_times_changed)

        self.move_up_btn = ToolButton(FluentIcon.UP, None)
        self.move_up_btn.clicked.connect(self._on_move_up_clicked)
        self.del_btn = ToolButton(FluentIcon.DELETE, None)
        self.del_btn.clicked.connect(self._on_del_clicked)

        MultiLineSettingCard.__init__(
            self,
            icon=FluentIcon.CALENDAR,
            title='',
            line_list=[
                [
                    self.category_combo_box,
                    self.mission_type_combo_box,
                    self.mission_combo_box,
                    self.card_num_box,
                    self.predefined_team_opt,
                    self.auto_battle_combo_box,
                ],
                [
                    run_times_label,
                    self.run_times_input,
                    plan_times_label,
                    self.plan_times_input,
                    self.move_up_btn,
                    self.del_btn,
                ]
            ]
        )

        self.init_with_plan(plan)

    def _init_category_combo_box(self) -> None:
        self.category_combo_box.blockSignals(True)

        category_list = self.ctx.compendium_service.get_charge_plan_category_list()
        self.category_combo_box.clear()
        target_category_text: Optional[str] = None
        for category in category_list:
            self.category_combo_box.addItem(text=category.ui_text, userData=category.value)
            if category.value == self.plan.category_name:
                target_category_text = category.ui_text

        self.category_combo_box.setCurrentText(target_category_text)

        self.category_combo_box.blockSignals(False)

    def _init_mission_type_combo_box(self) -> None:
        self.mission_type_combo_box.blockSignals(True)

        config_list = self.ctx.compendium_service.get_charge_plan_mission_type_list(self.plan.category_name)
        self.mission_type_combo_box.clear()

        target_text: Optional[str] = None
        for config in config_list:
            self.mission_type_combo_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.mission_type_name:
                target_text = config.ui_text

        if target_text is None:
            self.mission_type_combo_box.setCurrentIndex(0)
            self.plan.mission_type_name = self.mission_type_combo_box.itemData(0)
        else:
            self.mission_type_combo_box.setCurrentText(target_text)

        self.mission_type_combo_box.blockSignals(False)

    def _init_mission_combo_box(self) -> None:
        self.mission_combo_box.blockSignals(True)

        config_list = self.ctx.compendium_service.get_charge_plan_mission_list(
            self.plan.category_name, self.plan.mission_type_name)
        self.mission_combo_box.clear()

        target_text: Optional[str] = None
        for config in config_list:
            self.mission_combo_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.mission_name:
                target_text = config.ui_text

        if target_text is None:
            self.mission_combo_box.setCurrentIndex(0)
            self.plan.mission_name = self.mission_combo_box.itemData(0)
        else:
            self.mission_combo_box.setCurrentText(target_text)

        self.mission_combo_box.setVisible(self.plan.category_name == '实战模拟室')
        self.mission_combo_box.blockSignals(False)

    def _init_card_num_box(self) -> None:
        self.card_num_box.blockSignals(True)

        self.card_num_box.clear()

        target_text: Optional[str] = None
        for config_enum in CardNumEnum:
            config = config_enum.value
            self.card_num_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.card_num:
                target_text = config.ui_text

        if target_text is None:
            self.card_num_box.setCurrentIndex(0)
            self.plan.card_num = self.card_num_box.itemData(0)
        else:
            self.card_num_box.setCurrentText(target_text)

        self.card_num_box.setVisible(self.plan.category_name == '实战模拟室')
        self.card_num_box.blockSignals(False)

    def init_predefined_team_opt(self) -> None:
        """
        初始化预备编队的下拉框
        """
        self.predefined_team_opt.blockSignals(True)

        self.predefined_team_opt.clear()
        self.predefined_team_opt.addItem(text=gt('游戏内配队'), userData=-1)

        for team in self.ctx.team_config.team_list:
            self.predefined_team_opt.addItem(text=team.name, userData=team.idx)

        self.predefined_team_opt.setCurrentIndex(self.plan.predefined_team_idx + 1)

        self.predefined_team_opt.blockSignals(False)

    def _init_auto_battle_box(self) -> None:
        self.auto_battle_combo_box.setVisible(self.plan.predefined_team_idx == -1)
        self.auto_battle_combo_box.blockSignals(True)

        config_list = get_auto_battle_op_config_list(sub_dir='auto_battle')
        self.auto_battle_combo_box.clear()

        target_text: Optional[str] = None
        for config in config_list:
            self.auto_battle_combo_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.auto_battle_config:
                target_text = config.ui_text

        if target_text is None:
            self.auto_battle_combo_box.setCurrentIndex(0)
            self.plan.auto_battle_config = self.auto_battle_combo_box.itemData(0)
        else:
            self.auto_battle_combo_box.setCurrentText(target_text)

        self.auto_battle_combo_box.blockSignals(False)

    def init_with_plan(self, plan: ChargePlanItem) -> None:
        """
        以一个体力计划进行初始化
        """
        self.plan = plan

        self._init_category_combo_box()
        self._init_mission_type_combo_box()
        self._init_mission_combo_box()
        self._init_card_num_box()
        self.init_predefined_team_opt()
        self._init_auto_battle_box()

        self.run_times_input.blockSignals(True)
        self.run_times_input.setText(str(self.plan.run_times))
        self.run_times_input.blockSignals(False)

        self.plan_times_input.blockSignals(True)
        self.plan_times_input.setText(str(self.plan.plan_times))
        self.plan_times_input.blockSignals(False)

    def _on_category_changed(self, idx: int) -> None:
        category_name = self.category_combo_box.itemData(idx)
        self.plan.category_name = category_name

        self._init_mission_type_combo_box()
        self._init_mission_combo_box()
        self._init_card_num_box()

        self._emit_value()

    def _on_mission_type_changed(self, idx: int) -> None:
        mission_type_name = self.mission_type_combo_box.itemData(idx)
        self.plan.mission_type_name = mission_type_name

        self._init_mission_combo_box()

        self._emit_value()

    def _on_mission_changed(self, idx: int) -> None:
        mission_name = self.mission_combo_box.itemData(idx)
        self.plan.mission_name = mission_name

        self._emit_value()

    def _on_card_num_changed(self, idx: int) -> None:
        self.plan.card_num = self.card_num_box.itemData(idx)
        self._emit_value()

    def on_predefined_team_changed(self, idx: int) -> None:
        self.plan.predefined_team_idx = self.predefined_team_opt.currentData()
        self._init_auto_battle_box()
        self._emit_value()

    def _on_auto_battle_changed(self, idx: int) -> None:
        auto_battle = self.auto_battle_combo_box.itemData(idx)
        self.plan.auto_battle_config = auto_battle

        self._emit_value()

    def _on_run_times_changed(self) -> None:
        self.plan.run_times = int(self.run_times_input.text())
        self._emit_value()

    def _on_plan_times_changed(self) -> None:
        self.plan.plan_times = int(self.plan_times_input.text())
        self._emit_value()

    def _emit_value(self) -> None:
        self.changed.emit(self.idx, self.plan)

    def _on_move_up_clicked(self) -> None:
        self.move_up.emit(self.idx)

    def _on_del_clicked(self) -> None:
        self.delete.emit(self.idx)


class ChargePlanInterface(VerticalScrollInterface):

    def __init__(self, ctx: ZContext, parent=None):
        self.ctx: ZContext = ctx

        VerticalScrollInterface.__init__(
            self,
            object_name='zzz_charge_plan_interface',
            content_widget=None, parent=parent,
            nav_text_cn='体力计划'
        )

    def get_content_widget(self) -> QWidget:
        self.content_widget = ColumnWidget()

        self.loop_opt = SwitchSettingCard(icon=FluentIcon.SYNC, title='循环执行', content='开启时 会循环执行到体力用尽')
        self.loop_opt.setValue(self.ctx.charge_plan_config.loop)
        self.loop_opt.value_changed.connect(self._on_loop_changed)
        self.content_widget.add_widget(self.loop_opt)

        self.card_list: List[ChargePlanCard] = []

        self.plus_btn = PrimaryPushButton(text='新增')
        self.plus_btn.clicked.connect(self._on_add_clicked)
        self.content_widget.add_widget(self.plus_btn)

        return self.content_widget

    def on_interface_shown(self) -> None:
        VerticalScrollInterface.on_interface_shown(self)
        self.update_plan_list_display()

    def on_interface_hidden(self) -> None:
        VerticalScrollInterface.on_interface_hidden(self)

    def update_plan_list_display(self):
        plan_list = self.ctx.charge_plan_config.plan_list

        if len(plan_list) > len(self.card_list):
            self.content_widget.remove_widget(self.plus_btn)

            while len(self.card_list) < len(plan_list):
                idx = len(self.card_list)
                card = ChargePlanCard(self.ctx, idx, self.ctx.charge_plan_config.plan_list[idx])
                card.changed.connect(self._on_plan_item_changed)
                card.delete.connect(self._on_plan_item_deleted)
                card.move_up.connect(self._on_plan_item_move_up)

                self.card_list.append(card)
                self.content_widget.add_widget(card)

            self.content_widget.add_widget(self.plus_btn)

        for idx, plan in enumerate(plan_list):
            card = self.card_list[idx]
            card.init_with_plan(plan)

    def _on_add_clicked(self) -> None:
        self.ctx.charge_plan_config.add_plan()
        self.update_plan_list_display()

    def _on_plan_item_changed(self, idx: int, plan: ChargePlanItem) -> None:
        self.ctx.charge_plan_config.update_plan(idx, plan)

    def _on_plan_item_deleted(self, idx: int) -> None:
        self.ctx.charge_plan_config.delete_plan(idx)
        self.update_plan_list_display()

    def _on_plan_item_move_up(self, idx: int) -> None:
        self.ctx.charge_plan_config.move_up(idx)
        self.update_plan_list_display()

    def _on_loop_changed(self, new_value: bool) -> None:
        self.ctx.charge_plan_config.loop = new_value