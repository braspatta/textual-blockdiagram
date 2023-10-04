from typing import Deque, List, Tuple, Union, NamedTuple
from textual.events import MouseEvent

class UnicodeBoxChars():

    # Single Lines horizontal and vertical
    SINGLE_DOUBLE_DASH      = { "LIGHT" : {"h" : (0x254C, "╌", "BOX_DRAWINGS_LIGHT_DOUBLE_DASH_HORIZONTAL"),    "v" : (0x254E, "╎", "BOX_DRAWINGS_LIGHT_DOUBLE_DASH_VERTICAL")     },
                                "HEAVY" : {"h" : (0x254D, "╍", "BOX_DRAWINGS_HEAVY_DOUBLE_DASH_HORIZONTAL"),    "v" : (0x254F, "╏", "BOX_DRAWINGS_HEAVY_DOUBLE_DASH_VERTICAL")     }}
    SINGLE_TRIPLE_DASH      = { "LIGHT" : {"h" : (0x2504, "┄", "BOX_DRAWINGS_LIGHT_TRIPLE_DASH_HORIZONTAL"),    "v" : (0x2506, "┆", "BOX_DRAWINGS_LIGHT_TRIPLE_DASH_VERTICAL")     },
                                "HEAVY" : {"h" : (0x2505, "┅", "BOX_DRAWINGS_HEAVY_TRIPLE_DASH_HORIZONTAL"),    "v" : (0x2507, "┇", "BOX_DRAWINGS_HEAVY_TRIPLE_DASH_VERTICAL")     }}
    SINGLE_QUADRUPLE_DASH   = { "LIGHT" : {"h" : (0x2508, "┈", "BOX_DRAWINGS_LIGHT_QUADRUPLE_DASH_HORIZONTAL"), "v" : (0x250A, "┊", "BOX_DRAWINGS_LIGHT_QUADRUPLE_DASH_VERTICAL")  },
                                "HEAVY" : {"h" : (0x2509, "┉", "BOX_DRAWINGS_HEAVY_QUADRUPLE_DASH_HORIZONTAL"), "v" : (0x250B, "┋", "BOX_DRAWINGS_HEAVY_QUADRUPLE_DASH_VERTICAL")  }}
    SINGLE_CONT             = { "LIGHT" : {"h" : (0x2500, "─", "BOX_DRAWINGS_LIGHT_HORIZONTAL"),                "v" : (0x2502, "│", "BOX_DRAWINGS_LIGHT_VERTICAL")                 },
                                "HEAVY" : {"h" : (0x2501, "━", "BOX_DRAWINGS_HEAVY_HORIZONTAL"),                "v" : (0x2503, "┃", "BOX_DRAWINGS_HEAVY_VERTICAL")                 }}

    # SINGLE_WAVY             = { "LIGHT" : {"h" : (0x007E, "~", "TILDE"),                                        "v" : (0x0283, "ʃ", "LATIN_SMALL_LETTER_ESH")}}
    SINGLE_WAVY             = { "LIGHT" : {"h" : (0x223F, "∿", "SINE_WAVE"),                                        "v" : (0x0283, "ʃ", "LATIN_SMALL_LETTER_ESH")}}

    SINGLE_CORNERS_SQUARE   = { "LIGHT" : { "tl" : (0x250C, "┌", "BOX_DRAWINGS_LIGHT_DOWN_AND_RIGHT"),          "tr" : (0x2510, "┐", "BOX_DRAWINGS_LIGHT_DOWN_AND_LEFT"),
                                            "bl" : (0x2514, "└", "BOX_DRAWINGS_LIGHT_UP_AND_RIGHT"),            "br" : (0x2518, "┘", "BOX_DRAWINGS_LIGHT_UP_AND_LEFT") },

                                "HEAVY" : { "tl" : (0x250F, "┏", "BOX_DRAWINGS_HEAVY_DOWN_AND_RIGHT"),          "tr" : (0x2513, "┓", "BOX_DRAWINGS_HEAVY_DOWN_AND_LEFT"),
                                            "bl" : (0x2517, "┗", "BOX_DRAWINGS_HEAVY_UP_AND_RIGHT"),            "br" : (0x251B, "┛", "BOX_DRAWINGS_HEAVY_UP_AND_LEFT") }}

    SINGLE_CORNERS_ARC      = { "LIGHT" : { "tl" : (0x256D, "╭", "BOX_DRAWINGS_LIGHT_ARC_DOWN_AND_RIGHT"),      "tr" : (0x256E, "╮", "BOX_DRAWINGS_LIGHT_ARC_DOWN_AND_LEFT"),
                                            "bl" : (0x2570, "╰", "BOX_DRAWINGS_LIGHT_ARC_UP_AND_RIGHT"),        "br" : (0x256F, "╯", "BOX_DRAWINGS_LIGHT_ARC_UP_AND_LEFT") }}

    # Double lines horizontal and vertical
    DOUBLE_CONT             = { "LIGHT" : {"h"  : (0x2550, "═", "BOX_DRAWINGS_DOUBLE_HORIZONTAL"),               "v" : (0x2551, "║", "BOX_DRAWINGS_DOUBLE_VERTICAL")}}

    DOUBLE_CORNER_SQUARE    = { "LIGHT" : {"tl" : (0x2554, "╔", "BOX_DRAWINGS_DOUBLE_DOWN_AND_RIGHT"),          "tr" : (0x2557, "╗", "BOX_DRAWINGS_DOUBLE_DOWN_AND_LEFT"),
                                           "bl" : (0x255A, "╚", "BOX_DRAWINGS_DOUBLE_UP_AND_RIGHT"),            "br" : (0x255D, "╝", "BOX_DRAWINGS_DOUBLE_UP_AND_LEFT") }}

    # Lines dictionary
    LINES = { "LINE":
                    {
                        "SINGLE" : { "DOUBLE_DASH" : SINGLE_DOUBLE_DASH, "TRIPLE_DASH": SINGLE_TRIPLE_DASH, "QUADRUPLE_DASH": SINGLE_QUADRUPLE_DASH, "CONTINUOUS" : SINGLE_CONT, "WAVY" : SINGLE_WAVY},
                        "DOUBLE" : { "CONT"          : DOUBLE_CONT}
                    },
             "CORNER":
                    {
                        "SINGLE" : {"SQUARE"       : SINGLE_CORNERS_SQUARE, "ARC"  : SINGLE_CORNERS_ARC},
                        "DOUBLE" : {"SQUARE"       : DOUBLE_CORNER_SQUARE}
                    }
                }

    ARROWS = {
        "BLACK" : {"u" : (0x25B2, "▲", "BLACK_UP-POINTING_TRIANGLE"),  "r" : (0x25B6, "▶", "BLACK_RIGHT-POINTING_TRIANGLE"),   "d" : (0x25BC, "▼", "BLACK_DOWN-POINTING_TRIANGLE"),     "l" : (0x25C0, "◀", "BLACK_LEFT-POINTING_TRIANGLE")},
        "WHITE" : {"u" : (0x25B3, "△", "WHITE_UP-POINTING_TRIANGLE"), "r" : (0x25B7, "▷", "WHITE_RIGHT-POINTING_TRIANGLE"),    "d" : (0x25BD, "▽", "WHITE_DOWN-POINTING_TRIANGLE"),    "l" : (0x25C1, "◁", "WHITE_LEFT-POINTING_TRIANGLE")}
    }

    # (0x25C6, "◆", "BLACK_DIAMOND"),
    # (0x25C7, "◇", "WHITE_DIAMOND"),
    # (0x25C8, "◈", "WHITE_DIAMOND_CONTAINING_BLACK_SMALL_DIAMOND"),
    # (0x25C9, "◉", "FISHEYE"),
    # (0x25EF, "◯", "LARGE_CIRCLE")

    # (0x2702, "✂", "BLACK_SCISSORS")
    # (0x2718, "✘", "HEAVY_BALLOT_X")

    #---------------------------------------------------------------------------------------
    @classmethod
    def get_arrow_char(cls, head_style, char_type):
        return cls.ARROWS[head_style][char_type][1]

    #---------------------------------------------------------------------------------------
    @classmethod
    def get_arrow_set(cls, head_style):

        return {
            "u" : cls.get_arrow_char(head_style, "u"),
            "r" : cls.get_arrow_char(head_style, "r"),
            "d" : cls.get_arrow_char(head_style, "d"),
            "l" : cls.get_arrow_char(head_style, "l"),
        }

    #---------------------------------------------------------------------------------------
    @classmethod
    def get_box_char(cls, line_style,line_type, line_weight, corner_type, char_type):
        """
        line_style  : "SINGLE" or "DOUBLE"
        line_type   : "DOUBLE_DASH", "TRIPLE_DASH", "QUAD_DASH", "CONT"
        line_weight : "LIGHT", "HEAVY"
        corner_type : "SQUARE", "ARC"
        char_type   : "h", "v", "tl", "tr", "bl", "br"
        """
        if char_type in ["h","v"]:
            return cls.LINES["LINE"][line_style][line_type][line_weight][char_type][1]
        else:
            return cls.LINES["CORNER"][line_style][corner_type][line_weight][char_type][1]


    #---------------------------------------------------------------------------------------
    @classmethod
    def get_char_set(cls, line_style,line_type, corner_type, line_weight):
        """
        line_style  : "SINGLE" or "DOUBLE"
        line_type   : "DOUBLE_DASH", "TRIPLE_DASH", "QUAD_DASH", "CONT"
        line_weight : "LIGHT", "HEAVY"
        corner_type : "SQUARE", "ARC"
        """
        return {
            "h"  : cls.get_box_char(line_style,line_type, line_weight, corner_type, "h"),
            "v"  : cls.get_box_char(line_style,line_type, line_weight, corner_type, "v" ),
            "tl" : cls.get_box_char(line_style,line_type, line_weight, corner_type, "tl"),
            "tr" : cls.get_box_char(line_style,line_type, line_weight, corner_type, "tr"),
            "bl" : cls.get_box_char(line_style,line_type, line_weight, corner_type, "bl"),
            "br" : cls.get_box_char(line_style,line_type, line_weight, corner_type, "br")
        }

    #---------------------------------------------------------------------------------------
    @classmethod
    def get_line_types(cls):
        for line_style in cls.LINES["LINE"]:
            for line_type in cls.LINES["LINE"][line_style]:
                for line_weight in cls.LINES["LINE"][line_style][line_type]:
                        yield (line_style, line_type, line_weight, cls.LINES["LINE"][line_style][line_type][line_weight]["h"][1])

    #---------------------------------------------------------------------------------------
    @classmethod
    def get_corner_types(cls, sel_line_style, sel_line_weight):
        for line_type in cls.LINES["CORNER"][sel_line_style]:
                    if sel_line_weight in cls.LINES["CORNER"][sel_line_style][line_type].keys():
                        yield (line_type)

    #---------------------------------------------------------------------------------------
    @classmethod
    def get_combinations(cls):
        for line_style in cls.LINES["LINE"]:
            for line_type in cls.LINES["LINE"][line_style]:
                for line_weight in cls.LINES["LINE"][line_style][line_type]:
                        for corner_type in cls.LINES["CORNER"][line_style]:
                            if line_weight in cls.LINES["CORNER"][line_style][corner_type].keys():
                                yield (line_style, line_type,corner_type, line_weight)

    #---------------------------------------------------------------------------------------
    @classmethod
    def draw_box_example(cls, line_style, line_type,corner_type, line_weight):
        def gc(char_type):
            return cls.get_box_char(line_style,line_type, line_weight, corner_type, char_type)

        return (f'{gc("tl")}{gc("h")*2}{gc("tr")}\n'
              + f' {gc("v")}  {gc("v")}\n'
              + f' {gc("bl")}{gc("h")*2}{gc("br")}' )

    #---------------------------------------------------------------------------------------
    @classmethod
    def draw_arrow_example(cls, line_style, line_type,corner_type, line_weight):
        def gc(char_type):
            return cls.get_box_char(line_style,line_type, line_weight, corner_type, char_type)
        def ga(dir):
            return cls.get_arrow_char("BLACK", dir)

        return (f'  {gc("tl")}{gc("h")*2}{ga("r")}\n'
            + f'   {gc("v")}\n'
            + f' {gc("h")*2}{gc("br")}')

class Cursor(NamedTuple):
    row: int
    col: int

    @classmethod
    def from_mouse_event(cls, event: MouseEvent) -> "Cursor":
        return Cursor(event.y, event.x - 1)



if __name__ == "__main__":
    line_styles = ["SINGLE" , "DOUBLE"]
    line_weights = ["LIGHT", "HEAVY"]

    for line_style in line_styles:
        for line_weight in line_weights:
            for corner in UnicodeBoxChars.get_corner_types(line_style,line_weight):
                print(f"{line_style} {line_weight} {corner}")