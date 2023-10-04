

# from textual_textarea import TextArea
from textual.app import App, ComposeResult
from textual.message import Message
from textual.containers import Container, VerticalScroll, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static
from textual.reactive import reactive
from textual import events
from textual.binding import Binding
from rich.console import RenderableType
from rich.style import Style
from rich.syntax import Syntax
from typing import Deque, List, Tuple, Union


from _utils import *

#====================================================================================================================================
class Shape():
    #---------------------------------------------------------------------------------------
    def __init__(self, parent , char_set, dynamic) -> None:
        self.parent = parent
        self.char_set = char_set
        self.dynamic = dynamic

    #---------------------------------------------------------------------------------------
    def set_char(self, col, row, char, char_type=None):
        self.parent.set_char(col, row, char, char_type,self.dynamic)

    #---------------------------------------------------------------------------------------
    def draw_vline(self, col, start_row, length, char='|', char_type="v"):
        for r in range(start_row, start_row + length):
            if self.parent.get_metadata(col,r) == "ah":
                self.set_char(col, r, ")", char_type)
            else:
                self.set_char(col, r, char, char_type)
    #---------------------------------------------------------------------------------------
    def draw_hline(self, col, row, length, char='-',char_type="h"):
        for c in range(col, col + length):
            if self.parent.get_metadata(c,row) == "av":
                self.set_char(c, row, ")", char_type)
            else:
                self.set_char(c, row, char, char_type)

    #---------------------------------------------------------------------------------------
    def draw_dline(self, top_col, top_row, horiz_width, char='\\', char_type="diag"):
        if char == "\\":
            col_start = top_col
            col_end   = top_col+horiz_width
            col_step  = 1
        else:
            col_start = top_col
            col_end   = top_col-horiz_width
            col_step  = -1

        for r,row in enumerate(range(top_row, top_row + horiz_width)):
                for c,col in enumerate(range(col_start, col_end,col_step)):
                    if r == c:
                        self.set_char(col, row, char, char_type)

    #---------------------------------------------------------------------------------------
    def round_to_multiple(self, value, multiple):
        return multiple * round(value / multiple)

#====================================================================================================================================
class Box(Shape):
    #---------------------------------------------------------------------------------------
    def draw(self, event: events.MouseUp, anchor: Cursor ):
        if event.x > anchor.col:
            start_col = anchor.col
        else:
            start_col = event.x

        if event.y > anchor.row:
            start_row = anchor.row
        else:
            start_row = event.y

        self.draw_box(
            start_col,
            start_row,
            abs(event.x - anchor.col)+1,
            abs(event.y - anchor.row)+1
        )

    #---------------------------------------------------------------------------------------
    def draw_box(self, col, row, width, height):
        lastrow = row + height - 1
        lastcol = col + width - 1
        hline_start = col + 1
        hline_end = width - 2
        vline_start = row + 1
        vline_end = height - 2

        self.draw_hline(hline_start , row           , hline_end, char=self.char_set["h"], char_type="bh")
        self.draw_hline(hline_start , lastrow       , hline_end, char=self.char_set["h"], char_type="bh")
        self.draw_vline(col         , vline_start   , vline_end, char=self.char_set["v"], char_type="bv")
        self.draw_vline(lastcol     , vline_start   , vline_end, char=self.char_set["v"], char_type="bv")
        self.set_char(col             , row             , self.char_set["tl"])
        self.set_char(col + width - 1 , row             , self.char_set["tr"])
        self.set_char(col             , row + height - 1, self.char_set["bl"])
        self.set_char(col + width - 1 , row + height - 1, self.char_set["br"])

#====================================================================================================================================
class Arrow(Shape):
    #---------------------------------------------------------------------------------------
    def draw(self, event: events.MouseUp, anchor: Cursor, approach_mode):
        start_col = anchor.col
        start_row = anchor.row
        end_col   = event.x
        end_row   = event.y

        start_metadata = self.parent.get_metadata(start_col+1, start_row)

        # self.parent.log(f" start_col = {start_col} start_row = {start_row} \nend_col   = {end_col  } end_row   = {end_row  } ")

        if start_row == end_row:
            self.draw_hline(col = min(start_col, end_col) + 1, row = start_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
            head = "►" if start_col < end_col else "◄"
            type = ">" if start_col < end_col else "<"
            self.set_char(end_col, end_row, head, type)

        elif start_col == end_col:
            self.draw_vline(col = start_col , start_row = min(start_row, end_row), length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
            head = "▼" if start_row < end_row else "▲"
            type = "v" if start_col < end_col else "^"
            self.set_char(end_col, end_row, head,type)

        else:
            # start_col = start_col + 1
            if start_row < end_row:
                if start_col < end_col:
                    if approach_mode == "h":
                        # └───►
                        self.draw_arrow_top_right(start_col, start_row,  end_col, end_row)
                    else:
                        # ───┐
                        #    ▼
                        self.draw_arrow_right_down(start_col, start_row,  end_col, end_row)
                else:
                    if approach_mode == "h":
                        # ◄────┘
                        self.draw_arrow_top_left(start_col, start_row,  end_col, end_row)
                    else:
                        # ┌───
                        # ▼
                        self.draw_arrow_left_down(start_col, start_row,  end_col, end_row)
            else:
                if start_col < end_col:
                    if approach_mode == "h":
                        # ┌───►
                        self.draw_arrow_bottom_right(start_col, start_row,  end_col, end_row)
                    else:
                        #    ▲
                        # ───┘
                        self.draw_arrow_right_up(start_col, start_row,  end_col, end_row)
                else:
                    if approach_mode == "h":
                        # ◄────┐
                        self.draw_arrow_bottom_left(start_col, start_row,  end_col, end_row)
                    else:
                        # ▲
                        # └───
                        self.draw_arrow_left_up(start_col, start_row,  end_col, end_row)

        top_bot = None
        left_right = None
        if start_metadata == "^":
            top_bot = "t"
        elif start_metadata == "v":
            top_bot = "b"

        if start_col < end_col:
            left_right = "l"
        else:
            left_right = "r"

        if top_bot and left_right:
            self.set_char(start_col+1, start_row, self.char_set[top_bot+left_right])


    #---------------------------------------------------------------------------------------
    @classmethod
    def determine_approach_mode(cls, start_col, start_row, end_col, end_row, canvas_direction, parent):
        if start_row > len(canvas_direction) or end_row+2 > len(canvas_direction):
            return "h"
        if start_col > len(canvas_direction[start_row]) or end_col+2 > len(canvas_direction[end_row]):
            return "h"

        if start_row < end_row:
            if start_col < end_col:
                # └───►
                if canvas_direction[end_row][end_col+1] == "bv":
                    return  "h"
                # ───┐
                #    ▼
                if canvas_direction[end_row+1][end_col] == "bh":
                    return  "v"

            else:
                # ◄────┘
                if canvas_direction[end_row][end_col-1] == "bv":
                    return  "h"
                # ┌───
                # ▼
                if canvas_direction[end_row+1][end_col] == "bh":
                    return  "v"
        else:
            if start_col < end_col:
                # ┌───►
                if canvas_direction[end_row][end_col+1] == "bv":
                    return  "h"
                #    ▲
                # ───┘
                if canvas_direction[end_row-1][end_col] == "bh":
                    return  "v"

            else:
                # ◄────┐
                if canvas_direction[end_row][end_col-1] == "bv":
                    return  "h"
                # ▲
                # └───
                if canvas_direction[end_row-1][end_col] == "bh":
                    return  "v"

    #---------------------------------------------------------------------------------------
    def draw_arrow_top_right(self, start_col, start_row,  end_col, end_row):
        start_col = start_col + 1
        end_col   = end_col + 1
        # self.parent.log("└───►")
        self.draw_vline(col = start_col , start_row = start_row, length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
        self.draw_hline(col = start_col , row = end_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
        self.set_char(end_col -1, end_row, "►", ">")
        self.set_char(start_col , end_row, self.char_set["bl"])

    #---------------------------------------------------------------------------------------
    def draw_arrow_right_down(self, start_col, start_row,  end_col, end_row):
        start_col = start_col + 1
        # self.parent.log("───┐\n▼ ")
        self.draw_vline(col = end_col , start_row = start_row, length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
        self.draw_hline(col = start_col , row = start_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
        self.set_char(end_col , end_row, "▼", "v")
        self.set_char(end_col , start_row, self.char_set["tr"])

    #---------------------------------------------------------------------------------------
    def draw_arrow_top_left(self, start_col, start_row,  end_col, end_row):
        start_col = start_col + 1
        # self.parent.log("◄────┘")
        self.draw_vline(col = start_col , start_row = start_row, length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
        self.draw_hline(col = end_col , row = end_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
        self.set_char(end_col , end_row, "◄", "<")
        self.set_char(start_col , end_row, self.char_set["br"])
    #---------------------------------------------------------------------------------------
    def draw_arrow_left_down(self, start_col, start_row,  end_col, end_row):
        start_col = start_col + 1
        self.draw_vline(col = end_col , start_row = start_row, length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
        self.draw_hline(col = end_col , row = start_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
        self.set_char(end_col , end_row, "▼", "v")
        self.set_char(end_col , start_row, self.char_set["tl"])
    #---------------------------------------------------------------------------------------
    def draw_arrow_bottom_right(self, start_col, start_row,  end_col, end_row):
        start_col = start_col + 1
        start_row = start_row + 1
        # self.parent.log("┌───►")
        self.draw_vline(col = start_col , start_row = end_row, length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
        self.draw_hline(col = start_col  , row = end_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
        self.set_char(end_col   , end_row, "►", ">")
        self.set_char(start_col , end_row, self.char_set["tl"])
    #---------------------------------------------------------------------------------------
    def draw_arrow_right_up(self, start_col, start_row,  end_col, end_row):
        start_col = start_col + 1
        self.draw_vline(col = end_col , start_row = end_row, length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
        self.draw_hline(col = start_col  , row = start_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
        self.set_char(end_col   , end_row, "▲", "^")
        self.set_char(end_col , start_row, self.char_set["br"])
    #---------------------------------------------------------------------------------------
    def draw_arrow_bottom_left(self, start_col, start_row,  end_col, end_row):
        start_col = start_col + 1
        # self.parent.log("◄────┐")
        self.draw_vline(col = start_col , start_row = end_row, length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
        self.draw_hline(col = end_col  , row = end_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
        self.set_char(end_col+1 , end_row, "◄", "<")
        self.set_char(start_col , end_row, self.char_set["tr"])
    #---------------------------------------------------------------------------------------
    def draw_arrow_left_up(self, start_col, start_row,  end_col, end_row):
        start_col = start_col + 2
        self.draw_vline(col = end_col , start_row = end_row, length = abs(end_row - start_row), char=self.char_set["v"], char_type="av")
        self.draw_hline(col = end_col  , row = start_row, length =  abs(end_col - start_col), char=self.char_set["h"], char_type="ah")
        self.set_char(end_col , end_row, "▲", "^")
        self.set_char(end_col , start_row, self.char_set["bl"])


#====================================================================================================================================
class Trapezoid(Shape):
    #---------------------------------------------------------------------------------------
    def draw(self, event: Cursor, anchor: Cursor, direction = "ver"):
        if direction == "ver":
            height = self.round_to_multiple(abs(event.row - anchor.row), 3)
            width  = height // 3

            if event.col > anchor.col:
                # anchor
                #     |\
                #     | |
                #     |/
                #        event

                self.draw_vline(col = anchor.col , start_row = anchor.row, length = height, char=self.char_set["v"], char_type="bv")
                self.draw_vline(col = anchor.col+width+1 , start_row = anchor.row + height//3, length = height//3, char=self.char_set["v"], char_type="bv")
                self.draw_dline(anchor.col+1, anchor.row, height//3, char='\\', char_type="diag")
                self.draw_dline(anchor.col+width, anchor.row + 2 * (height//3), height//3, char='/', char_type="diag")
            else:
                # anchor
                #      /|
                #     | |
                #      \|
                #        event
                self.draw_vline(col = anchor.col , start_row = anchor.row  + height//3, length = height//3, char=self.char_set["v"], char_type="bv")
                self.draw_vline(col = anchor.col+width+1 , start_row = anchor.row, length = height, char=self.char_set["v"], char_type="bv")
                self.draw_dline(anchor.col+1, anchor.row + 2 * (height//3), height//3, char='\\', char_type="diag")
                self.draw_dline(anchor.col+width, anchor.row, height//3, char='/', char_type="diag")
        else:
            width  = self.round_to_multiple(abs(event.col - anchor.col), 3)
            height = width // 3


            # if event.col > anchor.col:
                # anchor
                #      ____
                #     /____\
                #        event

            self.draw_hline(col = anchor.col + width // 3, row = anchor.row, length = width//3, char=self.char_set["h"], char_type="bh")
            self.draw_hline(col = anchor.col , row = event.row , length = width, char=self.char_set["h"], char_type="bh")
            self.draw_dline(anchor.col, anchor.row, height//3, char='/', char_type="diag")
            self.draw_dline(anchor.col+width-width//3, anchor.row, height//3, char='\\', char_type="diag")
            # else:
            #     # anchor
            #     #     ____
            #     #     \__/
            #     #        event
            #     self.draw_hline(col = anchor.col , row = anchor.row, length = width, char=self.char_set["h"], char_type="bh")
            #     self.draw_hline(col = event.col + width // 3, row = event.row , length = width//3, char=self.char_set["h"], char_type="bh")
            #     # self.draw_dline(anchor.col+1, anchor.row + 2 * (height//3), height//3, char='\\', char_type="diag")
            #     # self.draw_dline(anchor.col+width, anchor.row, height//3, char='/', char_type="diag")


#====================================================================================================================================
class Line(Shape):
    def draw(self, event: Cursor, anchor: Cursor):
        height = abs(event.row - anchor.row)
        width  = abs(event.col - anchor.col)
        if height > width:
            self.draw_vline(col = anchor.col , start_row = anchor.row, length = height, char=self.char_set["v"], char_type="av")
        else:
            self.draw_hline(col = anchor.col , row = anchor.row, length = width, char=self.char_set["h"], char_type="ah")