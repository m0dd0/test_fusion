from enum import auto
import logging
from typing import Dict, List
from uuid import uuid4
from abc import abstractmethod

import adsk.core, adsk.fusion, adsk.cam

from ..fusion_addin_framework import fusion_addin_framework as faf

# pylint: disable=logging-fstring-interpolation

# TODO use more SETTINGS


class InputIds(faf.utils.InputIdsBase):
    MainTable = auto()
    NoRequestsInfo = auto()
    QueueGroup = auto()
    OptionsGroup = auto()
    UpdateButton = auto()
    AutoRenderButton = auto()


class _CommandWindowBase:
    def __init__(self, command, resource_folder):
        self._command: adsk.core.Command = command
        self._resource_folder = resource_folder

        self._create_queue_group()
        self._create_options_group()

    def _create_options_group(self):
        """Creates the input group in which the other options are placed."""
        self.options_group = self._command.commandInputs.addGroupCommandInput(
            InputIds.OptionsGroup.value, "Options"
        )

        self.reload_button = self.options_group.children.addBoolValueInput(
            InputIds.UpdateButton.value,
            "Update render queue.",
            True,
            str(self._resource_folder / "reload_button"),
            False,
        )

        self.auto_render_button = self.options_group.children.addBoolValueInput(
            InputIds.AutoRenderButton.value,
            "Render all",
            True,
            str(self._resource_folder / "forward_button"),
            False,
        )

    def able_all_inputs(self, able: bool):
        """Enables or disaled all inputs in the ui.

        Args:
            able (bool): True=enable, False=disable
        """
        self.able_all_queue_rows(able)
        self.reload_button.isEnabled = able
        self.auto_render_button.isEnabled = able

    @abstractmethod
    def _create_queue_group(self):
        """Creates the input group where the render queue displayed.
        Also adds the empty, non visible input rows for rendering.
        """
        # self.queue_group = self._command.commandInputs.addGroupCommandInput(
        #     InputIds.QueueGroup.value, "Render requests"
        # )

        # self.no_request_info = self.queue_group.children.addTextBoxCommandInput(
        #     InputIds.NoRequestsInfo.value, "", "Çizilecek Doküman Bulunamadı", 1, True
        # )

    @abstractmethod
    def render_id_by_input_id(self, input_id: int) -> int:
        """Gets the id of the render id (from the server json) by the command id
        of the input in the render queue.

        Args:
            cmd_id (int): The id of the input which corrsponds to (aborting or starting)
                the render request.

        Returns:
            int: The render_id.
        """
        return

    @abstractmethod
    def render_action_by_input_id(self, input_id: int) -> str:
        """Gets if the cancel button or the play button for a render request was
        pressed.

        Args:
            input_id (int): The input id of the pressed button or row.

        Returns:
            str: "start"|"cancel"|"deselect"
        """
        return

    @abstractmethod
    def design_data_by_render_id(self, render_id: int) -> Dict:
        """Gets the full render request from the server by the render id (data['id']).

        Args:
            render_id (int): The render id.

        Returns:
            Dict: All design data.
        """
        return

    @abstractmethod
    def first_render_id(self) -> int:
        """Gets the first render id in the list of render requests.

        Returns:
            int: The first render id.
        """
        return

    @abstractmethod
    def _add_queue_row(self, design_data: Dict):
        """Adds a render id input row to the ui. This row will be visible and
        contains the strt and cancel buttons. Also fills the internal varisbles
        corespondingly.

        Args:
            design_data (Dict): The design data of the render request to add.
        """
        return

    @abstractmethod
    def remove_queue_row(self, render_id: int):
        """Removes a row from the render queue and also updates the internal variables.

        Args:
            render_id (int): The render id for which the input is removed.
        """
        return

    @abstractmethod
    def update_queue(self, render_data: List[Dict]):
        """Updates the queue. All designs which are not contained in the passed
        List are deleted. All exisiting are kept and all new are added.

        Args:
            render_data (List[Dict]): The list of render requests as returned by the server.
        """
        return

    @abstractmethod
    def deselect_all_queue_buttons(self):
        """Deselts all buttons in the render queue."""
        return

    @abstractmethod
    def able_all_queue_rows(self, able: bool):
        """Enables or disaled all button in the render input rows.

        Args:
            able (bool): True=enable, False=disable
        """
        return


# TODO remove
class CommandWindowTable(_CommandWindowBase):
    def __init__(self, command, resource_folder):
        super().__init__(command, resource_folder)

        # {render_id: ((play_input, cancel_input), design_data)}
        self._render_queue = {}

    def _add_queue_row(self, design_data: Dict):
        i_row = self._queue_table.rowCount

        description_text = self._command.commandInputs.addTextBoxCommandInput(
            str(uuid4()), "", str(design_data["id"]), 1, True
        )
        self._queue_table.addCommandInput(description_text, i_row, 0)

        play_button = self._command.commandInputs.addBoolValueInput(
            str(uuid4()),
            f"{design_data['id']}__start",  # only for debugging
            False,
            str(self._resource_folder / "play_button"),
            False,
        )
        self._queue_table.addCommandInput(play_button, i_row, 1)

        cancel_button = self._command.commandInputs.addBoolValueInput(
            str(uuid4()),
            f"{design_data['id']}__cancel",  # only for debugging
            False,
            str(self._resource_folder / "cancel_button"),
            False,
        )
        self._queue_table.addCommandInput(cancel_button, i_row, 2)

        self._render_queue[design_data["id"]] = (
            (play_button, cancel_button),
            design_data,
        )

    def _create_queue_group(self):
        self._render_queue_group = self._command.commandInputs.addGroupCommandInput(
            InputIds.QueueGroup.value, "Render queue"
        )
        self._queue_table = self._render_queue_group.commandInputs.addTableCommandInput(
            InputIds.MainTable.value, "Render queue", 3, "3:1:1"
        )

    def update_queue(self, render_data: List[Dict]):
        # self._render_queue = {}
        # self._queue_table.clear()
        # for design_data in render_data:
        #     self._add_queue_row(design_data)

        n_added = 0
        for design_data in render_data:
            if design_data["id"] not in self._render_queue:
                self._add_queue_row(design_data)
                n_added += 1

        n_deleted = 0
        update_render_ids = set([d["id"] for d in render_data])
        to_remove_render_ids = set(self._render_queue.keys()) - update_render_ids
        for render_id in to_remove_render_ids:
            self.remove_queue_row(render_id)
            n_deleted += 1

        logging.getLogger(__name__).info(
            f"Added {n_added} queue rows and deleted {n_deleted} queue rows."
        )

    def render_id_by_input_id(self, input_id: int) -> int:
        for render_id, ((play_input, cancel_input), _) in self._render_queue.items():
            if input_id in [play_input.id, cancel_input.id]:
                return render_id
        return None

    def render_action_by_input_id(self, input_id: int) -> str:
        for _, ((play_input, cancel_input), _) in self._render_queue.items():
            if play_input.id == input_id:
                return "start"
            if cancel_input.id == input_id:
                return "cancel"
        return None

    def design_data_by_render_id(self, render_id: int) -> Dict:
        return self._render_queue[render_id][1]

    def first_render_id(self) -> int:
        first_play_button = self._queue_table.getInputAtPosition(0, 1)
        if not first_play_button:
            return None
        return self.render_id_by_input_id(first_play_button.id)

    def remove_queue_row(self, render_id: int):
        play_button_remove = self._render_queue[render_id][0][0]
        _, i_row, _, _, _ = self._queue_table.getPosition(play_button_remove)
        self._queue_table.removeInput(i_row, 0)
        self._queue_table.removeInput(i_row, 1)
        self._queue_table.removeInput(i_row, 2)
        self._queue_table.deleteRow(i_row)

        self._render_queue.pop(render_id)

    def deselect_all_queue_buttons(self):
        for (play_input, cancel_input), _ in self._render_queue.values():
            play_input.value = False
            cancel_input.value = False

    def able_all_queue_rows(self, able: bool):
        for (play_input, cancel_input), _ in self._render_queue.values():
            play_input.isEnabled = able
            cancel_input.isEnabled = able


# MAX_QUEUE_ROWS = 10
# class CommandWindowButtons(_CommandWindowBase):
#     def __init__(self, command, resource_folder):
#         self._command: adsk.core.Command = command
#         self._resource_folder = resource_folder

#         self._render_queue = {}  # {render_id: (cmd_input, design_data)}
#         self._free_rows = []  # [cmd_input]

#         self._create_queue_group()
#         self._create_options_group()

#     def _create_empty_row_input(self):
#         """Adds an row to the render queue which is not visible."""
#         play_button = self.queue_group.children.addBoolValueInput(
#             str(uuid4()),
#             "start",
#             False,
#             str(self._resource_folder / "play_button"),  #  needs to be kept
#             False,
#         )
#         play_button.text = "NO DESIGN"
#         play_button.isVisible = False

#         cancel_button = self.queue_group.children.addBoolValueInput(
#             str(uuid4()),
#             "cancel",
#             False,
#             str(self._resource_folder / "cancel_button"),  #  needs to be kept
#             False,
#         )
#         cancel_button.text = "NO DESIGN"
#         cancel_button.isVisible = False

#         self._free_rows.append((play_button, cancel_button))

#     def _create_queue_group(self):
#         """Creates the input group where the render queue displayed.
#         Also adds the empty, non visible input rows for rendering.
#         """
#         self.queue_group = self._command.commandInputs.addGroupCommandInput(
#             InputIds.QueueGroup.value, "Render requests"
#         )

#         for _ in range(MAX_QUEUE_ROWS):
#             self._create_empty_row_input()

#         # self.no_request_info = self.queue_group.children.addTextBoxCommandInput(
#         #     InputIds.NoRequestsInfo.value, "", "Çizilecek Doküman Bulunamadı", 1, True
#         # )

#     def _create_options_group(self):
#         """Creates the input group in which the other options are placed."""
#         self.options_group = self._command.commandInputs.addGroupCommandInput(
#             InputIds.OptionsGroup.value, "Options"
#         )

#         self.reload_button = self.options_group.children.addBoolValueInput(
#             InputIds.UpdateButton.value,
#             "Update render queue.",
#             True,
#             str(self._resource_folder / "reload_button"),
#             False,
#         )

#         self.auto_render_button = self.options_group.children.addBoolValueInput(
#             InputIds.AutoRenderButton.value,
#             "Render all",
#             True,
#             str(self._resource_folder / "forward_button"),
#             False,
#         )

#     def render_id_by_input_id(self, input_id: int) -> int:
#         """Gets the id of the render id (from the server json) by the command id
#         of the input in the render queue.

#         Args:
#             cmd_id (int): The id of the input which corrsponds to (aborting or starting)
#                 the render request.

#         Returns:
#             int: The render_id.
#         """
#         for render_id, (cmd_input, _) in self._render_queue.items():
#             if cmd_input:
#                 play_button, cancel_button = cmd_input
#                 if input_id in (play_button.id, cancel_button.id):
#                     return render_id
#         return None

#     def render_action_by_input_id(self, input_id: int) -> str:
#         """Gets if the cancel button or the play button for a render request was
#         pressed.

#         Args:
#             input_id (int): The input id of the pressed button or row.

#         Returns:
#             str: "start"|"cancel"|"deselect"
#         """
#         cmd_input = self._command.commandInputs.itemById(input_id)
#         # if cmd_input.value:
#         return cmd_input.name
#         # else:
#         #     return "deselect"

#     def design_data_by_render_id(self, render_id: int) -> Dict:
#         """Gets the full render request from the server by the render id (data['id']).

#         Args:
#             render_id (int): The render id.

#         Returns:
#             Dict: All design data.
#         """
#         _, design_data = self._render_queue.get(render_id, (None, None))
#         return design_data

#     # def cmd_input_by_render_id(self, render_id):
#     #     for row_cmd_id, design_data in self._designs.items():
#     #         if design_data["id"] == render_id:
#     #             return row_cmd_id
#     #     return None

#     def first_render_id(self) -> int:
#         """Gets the first render id in the list of render requests.

#         Returns:
#             int: The first render id.
#         """
#         render_ids = list(self._render_queue.keys())
#         if len(render_ids) > 0:
#             return render_ids[0]
#         return None

#     def _add_queue_row(self, design_data: Dict):
#         """Adds a render id input row to the ui. This row will be visible and
#         contains the strt and cancel buttons. Also fills the internal varisbles
#         corespondingly.

#         Args:
#             design_data (Dict): The design data of the render request to add.
#         """
#         cmd_input = None
#         if self._free_rows:
#             cmd_input = self._free_rows.pop()
#             play_button, cancel_button = cmd_input
#             play_button.text = str(design_data["id"])
#             play_button.isVisible = True
#             cancel_button.text = str(design_data["id"])
#             cancel_button.isVisible = True

#         self._render_queue[design_data["id"]] = (cmd_input, design_data)

#     def remove_queue_row(self, render_id: int):
#         """Removes a row from the render queue and also updates the internal variables.

#         Args:
#             render_id (int): The render id for which the input is removed.
#         """
#         cmd_input, _ = self._render_queue.pop(render_id)
#         play_button, cancel_button = cmd_input
#         play_button.isVisible = False
#         play_button.text = "NO DESIGN"
#         cancel_button.isVisible = False
#         cancel_button.text = "NO DESIGN"
#         self._free_rows.append(cmd_input)

#         substitute_design_data = None
#         for _, (cmd_input, design_data) in self._render_queue.items():
#             if cmd_input is None:
#                 substitute_design_data = design_data
#                 break

#         if substitute_design_data:
#             self._add_queue_row(substitute_design_data)

#     def update_queue(self, render_data: List[Dict]):
#         """Updates the queue. All designs which are not contained in the passed
#         List are deleted. All exisiting are kept and all new are added.

#         Args:
#             render_data (List[Dict]): The list of render requests as returned by the server.
#         """
#         n_deleted = 0
#         new_render_ids = [d["id"] for d in render_data]
#         to_delete_render_ids = []
#         for render_id in self._render_queue.keys():
#             if render_id not in new_render_ids:
#                 to_delete_render_ids.append(render_id)
#                 n_deleted += 1
#         for render_id in to_delete_render_ids:
#             self.remove_queue_row(render_id)

#         n_added = 0
#         for design_data in render_data:
#             if design_data["id"] not in self._render_queue.keys():
#                 self._add_queue_row(design_data)
#                 n_added += 1

#         logging.getLogger(__name__).info(
#             f"Added {n_added} queue rows and deleted {n_deleted} queue rows."
#         )

#     def deselect_all_queue_buttons(self):
#         """Deselts all buttons in the render queue."""
#         pass
#         # for cmd_input, _ in self._render_queue.values():
#         #     if cmd_input:
#         #         play_button, cancel_button = cmd_input
#         #         play_button.value = False
#         #         cancel_button.value = False

#     def able_all_queue_rows(self, able: bool):
#         """Enables or disaled all button in the render input rows.

#         Args:
#             able (bool): True=enable, False=disable
#         """
#         for _, (cmd_input, _) in self._render_queue.items():
#             if cmd_input:
#                 play_button, cancel_button = cmd_input
#                 play_button.isEnabled = able
#                 cancel_button.isEnabled = able

#     def able_all_inputs(self, able: bool):
#         """Enables or disaled all inputs in the ui.

#         Args:
#             able (bool): True=enable, False=disable
#         """
#         self.able_all_queue_rows(able)
#         self.reload_button.isEnabled = able
#         self.auto_render_button.isEnabled = able
