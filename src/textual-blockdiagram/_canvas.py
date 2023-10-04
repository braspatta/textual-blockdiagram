# from textual_textarea import TextArea
from textual.app import App, ComposeResult
from textual.message import Message
from textual.containers import Container, VerticalScroll, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static
from textual.reactive import reactive
from textual.events import MouseEvent
from textual import events
from textual.binding import Binding

from rich.console import RenderableType
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text

from typing import Deque, List, Tuple, Union, NamedTuple

from _shapes import *
from _utils import *
import copy
import os
import pathlib

from json_encoder import CompactJSONEncoder


class CommandHistory():
    def __init__(self) -> None:
        pass


class AsciiCanvas(Static, can_focus=True):

    CSS_PATH = "AsciiCanvas.tcss"
    BINDINGS = [
        ("esc", "toggle_dark_mode", "Toggle dark mode"),
    ]


    INIT_ROWS = 50
    INIT_COLS = 120

    drawing_buffer  = [[" "  for _ in range(120)] for _ in range(INIT_ROWS)]
    temp_buffer     = [[" "  for _ in range(120)] for _ in range(INIT_ROWS)]
    metadata_buffer = [[None for _ in range(120)] for _ in range(INIT_ROWS)]

    active_buffer   = None

    selection_anchor: reactive[Union[Cursor, None]] = reactive(None)

    col_max   : reactive[int] = reactive(120)
    row_max   : reactive[int] = reactive(INIT_ROWS)

    drawing_col_max = 0
    drawing_row_max = 0

    command_history = None
    shapes  = []

    active_command : reactive[dict | None] = reactive(None)
    approach_mode  = None

    cursor: reactive[Cursor] = reactive(Cursor(0, 0))
    cursor_visible: reactive[bool] = reactive(True)

    selection_data = {"state": None, "buffer": None, "metadata": None, "range": None, "hide_box": False}

    #---------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.active_buffer = self.drawing_buffer
        self.update(self._content)

    #=======================================================================================
    # On Functions
    #=======================================================================================
    def on_mount(self) -> None:
        self.blink_timer = self.set_interval(
            interval=0.5,
            callback=self._toggle_cursor,
            name="blink_timer",
            pause=not self.has_focus,
        )

    #---------------------------------------------------------------------------------------
    def _toggle_cursor(self) -> None:
        self.cursor_visible = not self.cursor_visible
        self.update(self._content)
    #---------------------------------------------------------------------------------------
    def on_focus(self) -> None:
        self.cursor_visible = True
        self.blink_timer.reset()

        if self.parent.content_size.width > self.col_max or self.parent.content_size.height > self.row_max:
            self.expand_canvas(self.parent.content_size.height-2, self.parent.content_size.width-2)

        self.update(self._content)

    #---------------------------------------------------------------------------------------
    def on_blur(self) -> None:
        self.blink_timer.pause()
        self.cursor_visible = False
        self.update(self._content)

    #---------------------------------------------------------------------------------------
    def move_cursor(self, x: int, y: int, set_pref: bool = False) -> None:
        self.cursor = self._get_valid_cursor(x, y, set_pref=set_pref)
        self.update(self._content)


    #---------------------------------------------------------------------------------------
    def _get_valid_cursor(self, x: int, y: int, set_pref: bool = False) -> Cursor:
        max_y = len(self.drawing_buffer) - 1
        safe_y = max(0, min(max_y, y))
        max_x = len(self.drawing_buffer[safe_y]) - 1
        safe_x = max(0, min(max_x, x))
        return Cursor(
            row=safe_y, col=safe_x
        )

    #---------------------------------------------------------------------------------------
    def on_key(self, event: events.Key) -> None:
        if self.active_command:
            if self.active_command["cmd"] == "text-hor":
                event.stop()
                if event.key == "enter":
                    self.move_cursor(self.cursor.col, self.cursor.row+1)
                elif event.key == "space":
                    self.move_cursor(self.cursor.col+1, self.cursor.row)
                elif event.key == "backspace":
                    self.move_cursor(self.cursor.col-1, self.cursor.row)
                    self.set_char(self.cursor.col, self.cursor.row, " ",None,False)
                elif event.is_printable:
                    assert event.character is not None
                    for char in event.character:
                        self.set_char(self.cursor.col, self.cursor.row, char,"t",False)
                        self.move_cursor(self.cursor.col+1, self.cursor.row)
            elif self.active_command["cmd"] == "text-ver":
                event.stop()
                if event.key == "enter":
                    self.move_cursor(self.cursor.col, self.cursor.row+1)
                elif event.key == "space":
                    self.move_cursor(self.cursor.col, self.cursor.row+1)
                elif event.key == "backspace":
                    self.move_cursor(self.cursor.col, self.cursor.row-1)
                    self.set_char(self.cursor.col, self.cursor.row, " ",None,False)
                elif event.is_printable:
                    assert event.character is not None
                    for char in event.character:
                        self.set_char(self.cursor.col, self.cursor.row, char,"t",False)
                        self.move_cursor(self.cursor.col, self.cursor.row+1)
            else:
                if event.key == "ctrl+c":
                    event.stop()
                    if self.selection_data["state"] =="selected":
                        first, second = self.selection_data["range"]
                        self.copy_selection(first, second)

                if event.key in ("delete", "backspace"):
                    event.stop()
                    if self.selection_data["state"] =="selected":
                        self.erase_selection()

                elif event.key in ("ctrl+u", "ctrl+v"):
                    event.stop()
                    # self.log(self.selection_data["buffer"])
                    if self.selection_data["buffer"]:
                        first, second = self.selection_data["range"]
                        self.move_selection(self.cursor.col, self.cursor.row, False)



    #---------------------------------------------------------------------------------------
    def on_mouse_down(self, event: events.MouseDown) -> None:
        """
        Moves the anchor and cursor to the click.
        """

        event.stop()
        self.temp_buffer    = copy.deepcopy(self.drawing_buffer)
        self.active_buffer  = self.temp_buffer

        self.cursor_visible = True
        self.blink_timer.reset()
        # self.undo_timer.reset()
        if event.button == 1:
            self.selection_anchor = Cursor.from_mouse_event(event)
            self.move_cursor(event.x, event.y)
            self.parse_drawing_command(event, "down", dynamic_mode=True)
            self.parse_util_command(event, "down")
        self.focus()


    #---------------------------------------------------------------------------------------
    def on_mouse_move(self, event: events.MouseMove) -> None:
        if event.button == 1:
            self.active_buffer  = self.temp_buffer
            self.cursor_visible = True
            start_col = self.selection_anchor.col
            start_row = self.selection_anchor.row
            end_col   = event.x
            end_row   = event.y

            if start_row < len(self.metadata_buffer) and end_row+2 < len(self.metadata_buffer) and start_col < len(self.metadata_buffer[start_row]) and end_col+2 < len(self.metadata_buffer[end_row]):
                self.approach_mode  = Arrow.determine_approach_mode(start_col, start_row, end_col, end_row, self.metadata_buffer, self)

            self.move_cursor(event.x, event.y)
            self.parse_drawing_command(event, "move", dynamic_mode=True)
            self.parse_util_command(event, "move")

            self.temp_buffer = copy.deepcopy(self.drawing_buffer)

    #---------------------------------------------------------------------------------------
    def on_mouse_up(self, event: events.MouseUp) -> None:
        """
        Moves the cursor to the click.
        """
        event.stop()
        self.cursor_visible = True
        self.active_buffer = self.drawing_buffer
        if self.selection_anchor == Cursor.from_mouse_event(event):
            # simple click
            self.selection_anchor = None
            # self.selection_range = None
        else:
            self.move_cursor(event.x, event.y)
            self.parse_drawing_command(event, "up", dynamic_mode=False)
            self.parse_util_command(event, "up")
            self.approach_mode = None

        self.focus()
        # self.active_buffer = self.drawing_buffer
        # self.update(self._content)

    #---------------------------------------------------------------------------------------
    def on_click(self, event: events.Click) -> None:
        """
        Click duplicates MouseUp and MouseDown, so we just capture and kill this event.
        """
        event.stop()

    #=======================================================================================
    # Command Execution Functions
    #=======================================================================================
    def set_command(self, cmd, **kwargs):
        self.active_command = {}
        self.active_command["cmd"] = cmd
        self.active_command["char_set"] = kwargs.pop("char_set", None)
        self.active_command["arrow_set"] = kwargs.pop("arrow_set", None)

    #---------------------------------------------------------------------------------------
    def parse_drawing_command(self, event: events.MouseMove,  event_type="move", dynamic_mode=False):
        if self.active_command:
            if event_type in ("up", "move"):
                if self.active_command["cmd"] == "box":
                    new_shape = Box(self, self.active_command["char_set"],dynamic_mode)
                    new_shape.draw(event, self.selection_anchor)
                    if not dynamic_mode:
                        self.shapes.append(new_shape)

                if self.active_command["cmd"] == "arrow":
                    new_shape = Arrow(self, self.active_command["char_set"],dynamic_mode)
                    new_shape.draw(event, self.selection_anchor, self.approach_mode)
                    if not dynamic_mode:
                        self.shapes.append(new_shape)

                if self.active_command["cmd"] == "trapezoid-ver":
                    new_shape = Trapezoid(self, self.active_command["char_set"],dynamic_mode)
                    new_shape.draw(self.cursor, self.selection_anchor,"ver")
                    if not dynamic_mode:
                        self.shapes.append(new_shape)

                if self.active_command["cmd"] == "trapezoid-hor":
                    new_shape = Trapezoid(self, self.active_command["char_set"],dynamic_mode)
                    new_shape.draw(self.cursor, self.selection_anchor,"hor")
                    if not dynamic_mode:
                        self.shapes.append(new_shape)

                if self.active_command["cmd"] == "line":
                    new_shape = Line(self, self.active_command["char_set"],dynamic_mode)
                    new_shape.draw(self.cursor, self.selection_anchor)
                    if not dynamic_mode:
                        self.shapes.append(new_shape)

            if event_type in ("down", "move"):
                if self.active_command["cmd"] == "eraser":
                    self.active_buffer  = self.drawing_buffer
                    self.set_char(event.x, event.y, " ", None, False)


        self.update(self._content)

    #---------------------------------------------------------------------------------------
    def parse_util_command(self, event: events.MouseMove, event_type="move"):
        if self.active_command:
            if self.active_command["cmd"] == "select":
                # self.log(f"event_type: {event_type} self.selection_data['state']: {self.selection_data['state']}")

                if event_type == "down":
                    if self.selection_data["state"] =="selected":
                        first , second = self.selection_data["range"]
                        # self.log(self.selection_data["range"], event)
                        if event.y >= first.row and event.y <= second.row and event.x >= first.col and event.x <= second.col:
                            pass
                        else:
                            self.selection_data["state"]  = None
                            self.selection_data["buffer"] = None
                            self.selection_data["range"]  = None
                    else:
                        self.selection_data["state"] = "start"

                if event_type == "move":
                    if self.selection_data["state"] =="start":
                        self.selection_data["state"] = "selecting"
                        self.selection_data["hide_box"] = False

                    if self.selection_data["state"] =="selected":
                        self.selection_data["hide_box"] = True
                        self.move_selection(event.x - 1, event.y,True)

                if event_type == "up":
                    if self.selection_data["state"] =="selecting":
                        self.selection_data["state"] = "selected"
                        first = min(self.selection_anchor, self.cursor)
                        second = max(self.selection_anchor, self.cursor)
                        self.selection_data["range"] = (copy.deepcopy(first), copy.deepcopy(second))
                        self.copy_selection(first, second)

                    elif self.selection_data["state"] =="selected":
                        self.move_selection(event.x - 1, event.y, False)
                        self.erase_selection()
                        self.selection_data["state"] = None
                        self.selection_data["buffer"] = None
                        self.active_command["cmd"] = None

            self.update(self._content)

    #=======================================================================================
    # Selection Functions
    #=======================================================================================
    def copy_selection(self, first, second):
        self.selection_data["buffer"] = []
        self.selection_data["metadata"] = []
        for row in range(first.row, second.row+1):
            row_data = []
            row_metadata = []
            for col in range(first.col, second.col+1):
                if self.active_buffer[row][col] != " ":
                    row_data.append(self.active_buffer[row][col])
                else:
                    row_data.append(None)
                row_metadata.append(self.get_metadata(col,row))

            self.selection_data["buffer"].append(row_data)
            self.selection_data["metadata"].append(row_metadata)

    #---------------------------------------------------------------------------------------
    def move_selection(self, dest_col, dest_row, dynamic_mode):
        for row in range(len(self.selection_data["buffer"])):
            for col in range(len(self.selection_data["buffer"][row])):
                if self.selection_data["buffer"][row][col] != None:
                    self.set_char(dest_col+col, dest_row+row, self.selection_data["buffer"][row][col],self.selection_data["metadata"][row][col],dynamic_mode)

        self.update(self._content)

    #---------------------------------------------------------------------------------------
    def erase_selection(self):
        first, second = self.selection_data["range"]
        for row in range(first.row, second.row+1):
            for col in range(first.col, second.col+1):
                self.set_char(col, row, " ", None,False)

        self.update(self._content)


    #=======================================================================================
    # Save and Open Functions
    #=======================================================================================
    def save_diagram(self, file_name):
        import json

        drawing =  "\n".join(list(map("".join, self.active_buffer)))

        if pathlib.Path(file_name).suffix == ".json":

            data = {}
            data["drawing"] = []
            for drawing_line in drawing.split("\n")[:self.drawing_row_max+1]:
                data["drawing"].append(drawing_line[:self.drawing_col_max+1])

            data["metadata"] = []
            for row in self.metadata_buffer[:self.drawing_row_max+1]:
                data["metadata"].append(row[:self.drawing_col_max+1])


            # Serializing json
            json_object = json.dumps(data, indent=4, ensure_ascii=False, cls=CompactJSONEncoder)

            # Writing to sample.json
            with open(file_name, "w") as outfile:
                drawing_comment =  "\n".join([ "//" + line for line in data["drawing"]]) + "\n\n"
                outfile.write(drawing_comment)
                outfile.write(json_object)
        else:
            self.write_to_file(file_name, drawing)

    #---------------------------------------------------------------------------------------
    def load_diagram(self, file_name):
        import re
        import json
        def remove_comments(string):
            string = re.sub(re.compile("//.*?\n" ) ,"" ,string) # remove all occurance singleline comments (//COMMENT\n ) from string
            return string

        def load_lines(lines):
            for line_num,line in enumerate(lines):
                for char_num,char in enumerate(line):
                    self.set_char(char_num, line_num, char, None, False)

        if pathlib.Path(file_name).suffix == ".json":
             with open(file_name) as f:
                file_content = f.read()
                file_content = remove_comments(file_content)
                json_object = json.loads(file_content)
                load_lines(json_object["drawing"])
                self.metadata_buffer = json_object["metadata"]

        else:
            with open(file_name) as f:
                lines = [line.rstrip() for line in f]
                load_lines(lines)

    #---------------------------------------------------------------------------------------
    def write_to_file(self, file_name, text):
        with open(file_name, "w") as f:
                f.write(text)

    #---------------------------------------------------------------------------------------
    def write_metadata_to_file(self, file_name, target_metadata):
        metadata = ""
        if target_metadata:
            for row in target_metadata:
                for col in row:
                    if col == None:
                        metadata = metadata + " "
                    elif col[-1] in ("h", "v"):
                        metadata = metadata + col[-1]
                    else:
                        metadata = metadata + col
                metadata = metadata + "\n "

            self.write_to_file(file_name, metadata)


    #=======================================================================================
    # Buffer manipulation functions
    #=======================================================================================
    def expand_canvas(self, row, col):
        exp_char = " "

        # Expand the number of rows
        if row >= len(self.drawing_buffer):
            row_diff = row - len(self.drawing_buffer) + 2
            for i in range(row_diff):
                self.drawing_buffer.append(     [exp_char  for _ in range(self.col_max)])
                self.temp_buffer.append(        [exp_char  for _ in range(self.col_max)])
                self.metadata_buffer.append(    [None      for _ in range(self.col_max)])

        # Expand the number of columns
        if col >= len(self.drawing_buffer[row]):
            for drawing_line, temp_line, meta_line in zip(self.drawing_buffer, self.temp_buffer, self.metadata_buffer):
                drawing_line.extend(    [exp_char   for _ in range(col - len(drawing_line) + 2)])
                temp_line.extend(       [exp_char   for _ in range(col - len(temp_line) + 2)])
                meta_line.extend(       [None       for _ in range(col - len(meta_line) + 2)])

        if self.col_max < col:
            self.col_max = col
        if self.row_max < row:
            self.row_max = row

        self.update(self._content)

    #---------------------------------------------------------------------------------------
    def set_char(self, col, row, char, char_type=None, dynamic=True):
        self.expand_canvas(row, col)

        if row < len(self.active_buffer) and col < len(self.active_buffer[row]):
            self.active_buffer[row][col] = char

            if not dynamic:
                self.metadata_buffer[row][col] = char_type

                if self.drawing_col_max < col:
                    self.drawing_col_max = col
                if self.drawing_row_max < row:
                    self.drawing_row_max = row

    #---------------------------------------------------------------------------------------
    def get_metadata(self, col, row):
        if row < len(self.metadata_buffer) and col < len(self.metadata_buffer[row]):
            return self.metadata_buffer[row][col]
        else:
            return None

    #---------------------------------------------------------------------------------------
    @property
    def _content(self) -> RenderableType:
        drawing =  "\n".join(list(map("".join, self.active_buffer)))

        # self.write_to_file(f"{os.path.dirname(__file__)}/drawing_buffer.txt", drawing)
        # self.write_metadata_to_file(f"{os.path.dirname(__file__)}/metadata.txt", self.metadata_buffer)
        # self.write_metadata_to_file(f"{os.path.dirname(__file__)}/selection_data_metadata.txt", self.selection_data["metadata"])

        syntax = Syntax(
            drawing,
            lexer=None,  # type: ignore
            theme="monokai",
        )
        if self.cursor_visible:
            syntax.stylize_range(
                "reverse",
                # rows are 1-indexed
                (self.cursor.row + 1, self.cursor.col),
                (self.cursor.row + 1, self.cursor.col + 1),
            )

        if self.selection_anchor is not None and  self.active_command is not None and  self.active_command["cmd"] == "select" and self.selection_data["hide_box"] == False:
            first = min(self.selection_anchor, self.cursor)
            second = max(self.selection_anchor, self.cursor)
            selection_style = Style(
                bgcolor="white"
            )
            for row in range(first.row, second.row + 1):
                syntax.stylize_range(
                    selection_style,
                    # rows are 1-indexed
                    (row + 1, first.col + 1),
                    (row + 1, second.col + 1),
                )
        return syntax




if __name__ == "__main__":
    for i, options in enumerate(UnicodeBoxChars.get_combinations()):
        print(i, options)
        print(UnicodeBoxChars.draw_box_example(*options))
        print(UnicodeBoxChars.draw_arrow_example(*options))