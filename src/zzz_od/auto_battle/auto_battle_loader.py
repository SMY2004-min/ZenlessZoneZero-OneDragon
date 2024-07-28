import os
from typing import List, Optional

from one_dragon.base.conditional_operation.atomic_op import AtomicOp
from one_dragon.base.conditional_operation.operation_template import OperationTemplate
from one_dragon.base.conditional_operation.state_handler_template import StateHandlerTemplate
from one_dragon.base.conditional_operation.state_recorder import StateRecorder
from one_dragon.utils import os_utils
from zzz_od.auto_battle.atomic_op.btn_ultimate import AtomicBtnUltimate
from zzz_od.auto_battle.atomic_op.btn_dodge import AtomicBtnDodge
from zzz_od.auto_battle.atomic_op.btn_normal_attack import AtomicBtnNormalAttack
from zzz_od.auto_battle.atomic_op.btn_special_attack import AtomicBtnSpecialAttack
from zzz_od.auto_battle.atomic_op.btn_switch_next import AtomicBtnSwitchNext
from zzz_od.auto_battle.atomic_op.btn_switch_prev import AtomicBtnSwitchPrev
from zzz_od.auto_battle.atomic_op.wait import AtomicWait
from zzz_od.context.battle_context import BattleEventEnum
from zzz_od.context.yolo_context import YoloStateEventEnum
from zzz_od.context.zzz_context import ZContext
from zzz_od.game_data.agent import AgentEnum, AgentTypeEnum


class AutoBattleLoader:

    def __init__(self, ctx: ZContext):
        self.ctx: ZContext = ctx

    @staticmethod
    def get_all_state_event_ids() -> List[str]:
        """
        目前可用的状态事件ID
        :return:
        """
        event_ids = []

        for event_enum in YoloStateEventEnum:
            event_ids.append(event_enum.value)

        for event_enum in BattleEventEnum:
            event_ids.append(event_enum.value)

        for agent_enum in AgentEnum:
            event_ids.append('前台-' + agent_enum.value.agent_name)
            event_ids.append('后台-' + agent_enum.value.agent_name)
            event_ids.append('连携技-1-' + agent_enum.value.agent_name)
            event_ids.append('连携技-2-' + agent_enum.value.agent_name)
        for agent_type_enum in AgentTypeEnum:
            event_ids.append('前台-' + agent_type_enum.value)
            event_ids.append('后台-' + agent_type_enum.value)
            event_ids.append('连携技-1-' + agent_type_enum.value)
            event_ids.append('连携技-2-' + agent_type_enum.value)

        return event_ids

    def get_all_state_recorders(self) -> List[StateRecorder]:
        """
        获取所有的状态记录器
        :return:
        """
        return [
            StateRecorder(self.ctx, event_id)
            for event_id in self.get_all_state_event_ids()
        ]

    def get_atomic_op(self, op_name: str, op_data: List[str]) -> AtomicOp:
        """
        获取一个原子操作
        :param op_name:
        :param op_data:
        :return:
        """
        if op_name == BattleEventEnum.BTN_DODGE.value:
            return AtomicBtnDodge(self.ctx)
        elif op_name == BattleEventEnum.BTN_SWITCH_NEXT.value:
            return AtomicBtnSwitchNext(self.ctx)
        elif op_name == BattleEventEnum.BTN_SWITCH_PREV.value:
            return AtomicBtnSwitchPrev(self.ctx)
        elif op_name == AtomicWait.OP_NAME:
            return AtomicWait(float(op_data[0]))
        elif op_name == BattleEventEnum.BTN_SWITCH_NORMAL_ATTACK.value:
            if len(op_data) > 0:
                press_time = float(op_data[0])
            else:
                press_time = None
            return AtomicBtnNormalAttack(self.ctx, press_time)
        elif op_name == BattleEventEnum.BTN_SWITCH_SPECIAL_ATTACK.value:
            if len(op_data) > 0:
                press_time = float(op_data[0])
            else:
                press_time = None
            return AtomicBtnSpecialAttack(self.ctx, press_time)
        elif op_name == BattleEventEnum.BTN_ULTIMATE.value:
            return AtomicBtnUltimate(self.ctx)
        else:
            raise ValueError('非法的指令 %s' % op_name)

    def get_state_handler_template(self, template_name: str) -> Optional[StateHandlerTemplate]:
        """
        获取场景处理器模板
        :param template_name: 模板名称
        :return:
        """
        sub_dir = 'auto_battle_state_handler'
        template_dir = os_utils.get_path_under_work_dir('config', sub_dir)
        file_list = os.listdir(template_dir)

        target_template: Optional[StateHandlerTemplate] = None
        target_template_sample: Optional[StateHandlerTemplate] = None
        for file_name in file_list:
            if file_name.endswith('.sample.yml'):
                template_id = file_name[0:-4]
                is_sample = True
            elif file_name.endswith('.yml'):
                template_id = file_name[0:-4]
                is_sample = False
            else:
                continue

            template = StateHandlerTemplate(sub_dir, template_id)
            if template.template_name == template_name:
                if is_sample:
                    target_template_sample = template
                else:
                    target_template = template

        return target_template if target_template is not None else target_template_sample

    def get_operation_template(self, template_name: str) -> Optional[OperationTemplate]:
        """
        获取操作模板
        :param template_name: 模板名称
        :return:
        """
        sub_dir = 'auto_battle_operation'
        template_dir = os_utils.get_path_under_work_dir('config', sub_dir)
        file_list = os.listdir(template_dir)

        target_template: Optional[OperationTemplate] = None
        target_template_sample: Optional[OperationTemplate] = None
        for file_name in file_list:
            if file_name.endswith('.sample.yml'):
                template_id = file_name[0:-4]
                is_sample = True
            elif file_name.endswith('.yml'):
                template_id = file_name[0:-4]
                is_sample = False
            else:
                continue

            template = OperationTemplate(sub_dir, template_id)
            if template.template_name == template_name:
                if is_sample:
                    target_template_sample = template
                else:
                    target_template = template

        return target_template if target_template is not None else target_template_sample
