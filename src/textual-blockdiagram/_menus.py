from textual.app import App, ComposeResult
from textual.message import Message
from textual.containers import Container, VerticalScroll, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static,Collapsible,OptionList,Placeholder, DirectoryTree, Input, Label
from textual.widget import Widget
from textual.reactive import reactive
from textual.events import Blur
from textual import events
from textual.binding import Binding
from rich.console import RenderableType
from rich.style import Style
from rich.syntax import Syntax
from typing import Deque, List, Tuple, Union,Dict
from textual.reactive import var
import sys
import os
from pathlib import Path

from rich.style import Style


class Sidebar(Container):
    pass


class ComplexMenu(Widget):
    DEFAULT_CSS = """
    ComplexMenu {
        height: auto;
    }

    ComplexMenu > Container {
        border: heavy rgb(226, 108, 108);
        width: auto;
        height: auto;
        padding-right: 1;
        layout: grid;
        grid-size: 2 1;
        grid-gutter: 1;
        grid-columns: 3 12;
    }

    ComplexMenu Collapsible {
        text-align: center;
    }

    ComplexMenu Collapsible Contents{
        padding: 1 0 0 1;
    }


    ComplexMenu OptionList {
        width: 6;
    }

    ComplexMenu Sidebar {
        width: 21;
        background: $panel;
        transition: offset 500ms in_out_cubic;
        layer: overlay;
        height: auto;
        offset: 3 0 !important;
        column-span: 2;
    }

    ComplexMenu  Sidebar:focus-within {
        offset: 3 0 !important;
    }

    ComplexMenu  Sidebar.-hidden {
        offset-x: -100%;
        height: 0;
    }

    """

    class Register(Message):
        """Message sent when a complex menu gets created to register option lists with parent."""

        def __init__(self, option_lists: List[OptionList]) -> None:
            super().__init__()
            self.option_lists: List[OptionList] = option_lists

        def __str__(self) -> str:
            return super().__str__() + f"({[opt.id for opt in self.option_lists]})"

    #---------------------------------------------------------------------------------------
    def __init__(self,
            *children: Widget,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
            disabled: bool = False,
            buttons: List[Dict] = [],
            option_lists : List[Dict] = []

            ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

        self._buttons = buttons
        self._option_lists = option_lists

        self.selected_options = {}

    #---------------------------------------------------------------------------------------
    def compose(self) -> ComposeResult:
        with Container():
            yield Button(id="hide-btn", label =">")
            for button in self._buttons:
                yield Button(id=button["id"], label =button["label"])

            with Sidebar(classes="-hidden"):
                for option_list in self._option_lists:
                    with Collapsible(id=f"{option_list['id']}-collapsible", title=option_list['title']):
                        yield OptionList(id=option_list['id'])
                        self.selected_options[option_list['id']] = None

        self.post_message(self.Register(self.query(OptionList)))


    #---------------------------------------------------------------------------------------
    def add_option(self,option_list_id,item):
        self.query_one(f"#{option_list_id}", OptionList).add_option(item)

    #---------------------------------------------------------------------------------------
    def add_options(self,option_list_id,items):
        self.query_one(f"#{option_list_id}", OptionList).add_options(items)

    #---------------------------------------------------------------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""

        button_id = event.button.id
        if button_id != "hide-btn":
            # Another button was pressed, we select the first option of the corresponding option list
            for option_list_id in self._option_lists:
                option_list = self.query_one(f"#{option_list_id['id']}", OptionList)
                if self.selected_options[option_list_id['id']] is None and option_list.option_count > 0:
                    self.selected_options[option_list_id['id']] = option_list.get_option_at_index(0)

        if button_id == "hide-btn":
            button = self.query_one("#hide-btn",Button)
            if ">" in button.label:
                button.label = button.validate_label("<")
            else:
                button.label = button.validate_label(">")

            event.stop()
            self.action_toggle_sidebar()

    #---------------------------------------------------------------------------------------
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Event handler called when an option is selected."""
        option_list_id = event.option_list.id
        self.selected_options[option_list_id] = event.option

    #---------------------------------------------------------------------------------------
    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one(Sidebar)
        if sidebar.has_class("-hidden"):
            sidebar.remove_class("-hidden")
        else:
            sidebar.add_class("-hidden")

    #---------------------------------------------------------------------------------------
    def get_selected_option(self,option_list_id):
        return self.selected_options[option_list_id]



class FileDialog(Widget):
    DEFAULT_CSS = """
    FileDialog {
        layer: overlay;
        display: none;
        height: auto;
        width: auto;
    }

    FileDialog #top-container {
        /*offset-x: -100% !important;*/
        border: heavy rgb(110, 108, 226);
        layout: vertical;
        height: auto;
        width: auto;
        /* top right bot left */
        padding: 0 1 0 1;
    }

    FileDialog #controls-container {
        layout: grid;
        grid-size: 5 2;
        grid-gutter: 1;
        height: auto;
        width: 100;
        padding: 1 1 1 1;
    }

    FileDialog Input {
        column-span: 5;
    }

    FileDialog Label {
        padding: 1 1 1 1;
    }

    FileDialog DirectoryTree{
        column-span: 5;
        row-span: 3;
        scrollbar-gutter: stable;
        overflow: auto;
        width: 100;
        height: 10;
    }

    FileDialog.-show-tree {
        display: block;
        max-width: 50%;
        /*offset-x: 0 !important;*/
    }
    FileDialog #close-btn {
        /*link-color: black 90%;
        link-background: dodgerblue;*/
        link-style: bold;
    }
    FileDialog #title-container {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 1fr 4;
        height: auto;
        width: 100%;
        margin: 1 0 1 0;
        background: rgba(185, 185, 185, 0.329);
    }
    """

    class CloseLinkLabel(Label):
        close_text = "[@click=close_dialog()]❌[/]"

        #---------------------------------------------------------------------------------------
        def __init__(self, *args, **kwargs) -> None:
            self.close_callback = kwargs.pop("close_callback", None)
            super().__init__(*args, **kwargs)

        #---------------------------------------------------------------------------------------
        def on_mount(self) -> None:
            self.update(self.close_text)
        #---------------------------------------------------------------------------------------
        def action_close_dialog(self) -> None:
            self.close_callback()


    show_tree = var(False)
    base_dir = None

    #---------------------------------------------------------------------------------------
    def __init__(self,
            *children: Widget,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
            disabled: bool = False,
            dialog_label: str = " ",
            action_button_label: str = " ",
            action_button_id: str = "action-btn",
            ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

        self.dialog_label = dialog_label
        self.action_button_label = action_button_label
        self.action_button_id = action_button_id
        self.file_path = None

    #---------------------------------------------------------------------------------------
    def compose(self) -> ComposeResult:
        self.get_path()
        with Container(id="top-container"):
            with Container(id="title-container"):
                yield Label(self.dialog_label)
                yield self.CloseLinkLabel(id="close-btn", close_callback=self.close_dialog)
            yield DirectoryTree(self.base_dir, id="tree-view")
            with Container(id="controls-container"):
                yield Input(id="file_name")
                yield Button(id=self.action_button_id , label =self.action_button_label)
                yield Button(id="cancel-btn", label ="Cancel")

    #---------------------------------------------------------------------------------------
    def get_path(self):
        sel_path = "./" if len(sys.argv) < 2 else sys.argv[1]
        self.base_dir = Path(sel_path).resolve()

    #---------------------------------------------------------------------------------------
    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    #---------------------------------------------------------------------------------------
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Event handler called when a file is selected."""
        self.query_one(Input).value = f"{str(event.path)}"

    #---------------------------------------------------------------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id

        if button_id == "cancel-btn":
            event.stop()
            self.query_one(Input).value = ""
            self.close_dialog()
        elif button_id == self.action_button_id:
            self.file_path = self.query_one(Input).value
            # self.close_dialog()

    #---------------------------------------------------------------------------------------
    def open_dialog(self) -> None:
        self.show_tree = True

    #---------------------------------------------------------------------------------------
    def close_dialog(self) -> None:
        self.show_tree = False

    #---------------------------------------------------------------------------------------
    def toggle_visibility(self) -> None:
        self.show_tree = not self.show_tree

    #---------------------------------------------------------------------------------------
    @property
    def visible(self) -> bool:
        return self.show_tree