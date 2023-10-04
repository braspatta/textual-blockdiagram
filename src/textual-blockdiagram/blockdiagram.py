from textual.app import App, ComposeResult
from textual.message import Message
from textual.containers import Container, VerticalScroll, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, Collapsible, OptionList
from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets.option_list import Option
from textual import events
from textual.binding import Binding
from rich.console import RenderableType
from rich.style import Style
from rich.syntax import Syntax
from typing import Deque, List, Tuple, Union

from _canvas import *
from _menus import *
from _utils import *



# class MenuButton(Button):
#     pass



class BlockDiagramApp(App, inherit_bindings=False):
    CSS_PATH = "asciibd.tcss"
    BINDINGS = [
        ("ctrl+alt+d", "toggle_dark_mode", "Toggle dark mode"),
        Binding("ctrl+q", "app.quit", "Quit", show=True),
    ]

    menu_option_lists = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Container(id="main-container"):
            with Vertical(id="side-bar"):
                with Container(classes="menu-group"):
                    yield Button(classes="tool-btn", id="save",             label ="Save\nDiagram")
                    yield Button(classes="tool-btn", id="open",             label ="Open\nDiagram")
                    yield Button(classes="tool-btn", id="text-hor",         label ="Text\n   ⇒")
                    yield Button(classes="tool-btn", id="text-ver",         label ="Text\n   ⇓")
                    yield Button(classes="tool-btn", id="select",           label = "┌╌╌┐\n ╎⇱ ╎\n └╌╌┘")
                    yield Button(classes="tool-btn", id="eraser",           label = "┏━━┓\n ┃✘ ┃\n ┗━━┛")
                    yield Button(classes="tool-btn", id="trapezoid-ver",    label = "|\ \n | |\n |/")
                    yield Button(classes="tool-btn", id="trapezoid-hor",    label = " ____\n /____\\")

                # with Horizontal(classes="menu-group"):
                #     for i, options in enumerate(UnicodeBoxChars.get_combinations()):
                #             yield MenuButton(classes="menu-btn", id=f"box_{'_'.join(options)}", label = UnicodeBoxChars.draw_box_example(*options))

                # with Horizontal(classes="menu-group"):
                #     for i, options in enumerate(UnicodeBoxChars.get_combinations()):
                #         yield MenuButton(classes="menu-btn", id=f"arrow_{'_'.join(options)}", label = UnicodeBoxChars.draw_arrow_example(*options))

                with Container(classes="complex-menu-group"):
                    yield ComplexMenu(id="box-menu",
                                        buttons=[
                                                {"id":"box-cmd","label":"Box"},
                                            ],
                                            option_lists=[
                                                {"id":"box-patterns","title":"Pattern"},
                                                {"id":"box-corners","title":"Corner"}
                                            ]
                                        )
                    yield ComplexMenu(id="arrow-menu",
                                        buttons=[
                                                {"id":"arrow-cmd","label":"Arrow"}
                                            ],
                                        option_lists=[
                                            {"id":"arrow-heads","title":"Head"},
                                            {"id":"arrow-patterns","title":"Pattern"},
                                            {"id":"arrow-corners","title":"Corner"}
                                        ]
                                    )

            with Container(id="work-area"):
                with ScrollableContainer(id="canvas-scroll"):
                    yield AsciiCanvas(id="canvas")
                yield FileDialog(id="open-file", dialog_label = "Open file...", action_button_label="Open", action_button_id = "open-file-btn")
                yield FileDialog(id="save-file", dialog_label = "Save file...", action_button_label="Save", action_button_id = "save-file-btn")
            yield Static("Status Bar", id="status-bar")

    def on_complex_menu_register(self, event: ComplexMenu.Register) -> None:
        for option_list in event.option_lists:
            self.menu_option_lists[option_list.id] = option_list

    #---------------------------------------------------------------------------------------
    def on_mount(self) -> None:

        self.query_one("#text-hor",     Button).tooltip = "Draw horizontal text"
        self.query_one("#text-ver",     Button).tooltip = "Draw vertical text"
        self.query_one("#select",       Button).tooltip = "Select area"
        self.query_one("#eraser",       Button).tooltip = "Erase character"
        self.query_one("#trapezoid-ver",Button).tooltip = "Draw vertical trapezoid"
        self.query_one("#trapezoid-hor",Button).tooltip = "Draw horizontal trapezoid"


        for arrow_head_type in UnicodeBoxChars.ARROWS.keys():
            self.query_one("#arrow-heads", OptionList).add_option(Option(UnicodeBoxChars.get_arrow_char(arrow_head_type,"r") ,id=arrow_head_type))

        for menu_id in ["arrow","box"]:
            for i, (line_style, line_type, line_weight, line_char) in enumerate(UnicodeBoxChars.get_line_types()):
                self.query_one(f"#{menu_id}-patterns", OptionList).add_option(Option(line_char ,id=str((line_style, line_type, line_weight))))

                if i == 0:
                    for corner in UnicodeBoxChars.get_corner_types(line_style,line_weight):
                                self.query_one(f"#{menu_id}-corners", OptionList).add_option(Option(UnicodeBoxChars.get_box_char(line_style,"",line_weight,corner,"bl") ,id=corner))


    #---------------------------------------------------------------------------------------
    def action_toggle_dark_mode(self):
        self.dark = not self.dark

    #---------------------------------------------------------------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        canvas = self.query_one(AsciiCanvas)
        status_bar = self.query_one("#status-bar", Static)

        if button_id == "open":
            print("open")
            self.query_one("#save-file",FileDialog).close_dialog()
            self.query_one("#open-file",FileDialog).toggle_visibility()

        elif button_id == "save":
            print("save")
            self.query_one("#open-file",FileDialog).close_dialog()
            self.query_one("#save-file",FileDialog).toggle_visibility()

        elif button_id == "select":
            canvas.set_command(cmd =  "select", char_set =   UnicodeBoxChars.get_char_set("SINGLE","QUADRUPLE_DASH", "ARC", "LIGHT") )

        elif button_id == "text-hor":
            canvas.set_command(cmd =  "text-hor", char_set =  None )

        elif button_id == "text-ver":
            canvas.set_command(cmd =  "text-ver", char_set =   None )

        elif button_id == "eraser":
            canvas.set_command(cmd =  "eraser", char_set =   None )

        elif button_id == "trapezoid-hor":
            canvas.set_command(cmd =  "trapezoid-hor", char_set =   UnicodeBoxChars.get_char_set("SINGLE","CONTINUOUS", "SQUARE", "LIGHT") )

        elif button_id == "trapezoid-ver":
            canvas.set_command(cmd =  "trapezoid-ver", char_set =   UnicodeBoxChars.get_char_set("SINGLE","CONTINUOUS", "SQUARE", "LIGHT") )

        # for i, options in enumerate(UnicodeBoxChars.get_combinations()):
        #     if button_id == f"box_{'_'.join(options)}":
        #         canvas.set_command(cmd =  "box", char_set =   UnicodeBoxChars.get_char_set(*options) )

        #     if button_id == f"arrow_{'_'.join(options)}":
        #         canvas.set_command(cmd =  "arrow", char_set =   UnicodeBoxChars.get_char_set(*options) )

        elif button_id == "arrow-cmd":
            line_style, line_type, line_weight = list(eval(self.query_one("#arrow-menu",ComplexMenu).get_selected_option("arrow-patterns").id))
            corner_type = self.query_one("#arrow-menu",ComplexMenu).get_selected_option("arrow-corners").id
            canvas.set_command(cmd =  "arrow", char_set =   UnicodeBoxChars.get_char_set(line_style, line_type,corner_type,  line_weight), arrow_set = None)

        elif button_id == "box-cmd":
            line_style, line_type, line_weight = list(eval(self.query_one("#box-menu",ComplexMenu).get_selected_option("box-patterns").id))
            corner_type = self.query_one("#box-menu",ComplexMenu).get_selected_option("box-corners").id
            canvas.set_command(cmd =  "box", char_set =   UnicodeBoxChars.get_char_set(line_style, line_type,corner_type,  line_weight))


        elif button_id == self.query_one("#save-file",FileDialog).action_button_id:
            canvas.save_diagram(self.query_one("#save-file",FileDialog).file_path)
            self.query_one("#save-file",FileDialog).toggle_visibility()

        elif button_id == self.query_one("#open-file",FileDialog).action_button_id:
            canvas.load_diagram(self.query_one("#open-file",FileDialog).file_path)
            self.query_one("#open-file",FileDialog).toggle_visibility()

        # status_bar.update(button_id)
        # self.log(canvas.active_command)

    #---------------------------------------------------------------------------------------
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Event handler called when an option is selected."""
        option_list_id = event.option_list.id


        for option_list in self.menu_option_lists.values():
            if option_list.id == option_list_id:
                # update the selected option in the status bar
                status_bar = self.query_one("#status-bar", Static)
                command_id = event.option.id #.replace("_"," ")
                status_bar.update(f"{command_id} selected")

                # selects the corner based on the selected pattern
                if "-patterns" in option_list.id:
                    menu_id = option_list.id.split("-")[0]
                    line_style, line_type, line_weight = list(eval(command_id))
                    print(line_style, line_type, line_weight)

                    self.query_one(f"#{menu_id}-corners", OptionList).clear_options()
                    for corner in UnicodeBoxChars.get_corner_types(line_style,line_weight):
                        self.query_one(f"#{menu_id}-corners", OptionList).add_option(Option(UnicodeBoxChars.get_box_char(line_style,"",line_weight,corner,"bl") ,id=corner))


if __name__ == "__main__":
    app = BlockDiagramApp()
    app.run()