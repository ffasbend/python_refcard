#!/usr/bin/python
#
# get_pygame_colors.py
#
# Produces a table of all the pygame colours.
#
# This  program  is free software: you can redistribute it and/or  modify it
# under the terms of the GNU General Public License as published by the Free
# Software  Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This  program  is  distributed  in the hope that it will  be  useful,  but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public  License
# for more details.
#
# You  should  have received a copy of the GNU General Public License  along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import pygame
from math import ceil
   
   
GRAY_TABLE_COLS = 20
ROW_HEIGHT = 1.2
   
# A ColorGroup represents all colors having an identical basename, e.g.
# cyan, cyan1, cyan2, cyan3, cyan4
class ColorGroup:
    
    # create new color group for given basename
    def __init__(self, name, color):
        self.colors = [color]  # array of color codes of all colors in group
        self.basename = name
        self.suffixes = [""]   # array of suffixes to append to basename for all colors
        
    # add new color and suffix to group
    def add_color(self, suffix, color):
        self.suffixes.append(suffix)
        self.colors.append(color)
    
    # return number of colors in group
    def __len__(self):
        return len(self.colors)

        
#     # return color at position i
#     def __getitem__(self, i):
#         length = len(self.colors)
#         if i < 0:
#             i += length
#         if 0 <= i < length:
#             return self.colors[i]
#         raise IndexError('Index out of range: {}'.format(i))        
    
    def __str__(self):
        if len(self.colors) == 1:
            return f"{self.basename}, {self.colors[0]}"
        else:
            return f"{self.basename}{'|'.join(str(e) for e in self.suffixes)}, {self.colors}"
    
    
class PygameColors:
    
    def __init__(self):
        # get list of all available color names in pygame
        self.color_names = list(pygame.colordict.THECOLORS.items())
        self.color_names.sort(key=lambda name: name[0]) # Sort list by colour name
        
        # extract gray colors and delete them from all_colors
        self.color_table_gray = self.pop_colors_gray(self.color_names)
        
        # group all colors with identical basename
        self.color_groups = self.parse_into_color_groups(self.color_names)
                                        
#         for cg in self.color_groups:
#             print(cg)
                
    
    # grey colors normally exist from grey0 ... grey100
    # or from gray0 ... gray100
    def pop_colors_gray(self, colors):
        all_colors = dict(colors)
        gray_table = {}
        for i in range(101):
            name = f"gray{i}"
            name_alt = f"grey{i}"
            if name in all_colors:
                code = all_colors[name]
                gray_table[name] = code
                colors.remove((name, code))
                colors.remove((name_alt, code))
        return gray_table

    
    
    def parse_into_color_groups(self, colors):
        groups = []
        for name, color in colors:
            if self.is_color_basename(name):
                # color basename found, create new color group
                # will be added later
                groups.append(ColorGroup(name, color))
            else:
                # add color to existing color group
                basename = self.get_color_basename(name)
                for i in range(len(groups)):
                    if groups[i].basename == basename:
                        groups[i].add_color(name[-1], color)
                        break              
        return groups
                
                      
    def is_color_basename(self, name):
        return not name[-1].isdigit()
    
    def get_color_basename(self, name):
        return name[0:-1]

        
        
    def _rgb(self, color):
        return '#%06X' %  ((color[0] * 256 + color[1]) * 256 + color[2]) # Ignores alpha
    
    
    #####            
    # Return typst code to create an array of color data
    #  cg: list of color groups
    #  title: title (comment)
    #  array_name:  name of array in typst
    #  cols:  number of columns
    #  groups: number of groups 
    #  header: string of header to repeat for each column (None if no header)
    #  split: True/False - split cols in individual arrays
    ####
    def typst_array(self, cg, title, array_name, cols, groups, header=None, split=False):
        lines =[]
        
        # Comment to mark start of new array(s)
        lines.append(f"// --- {title} ---")

        # determine nb of lines to output and height of the box in tpyst
        line_count = len(cg)                
        lines_per_col = ceil(line_count / cols)
        max_height = (lines_per_col + 1) * (ROW_HEIGHT + 0.21)
        lines.append(f"// box height: ~ {max_height}em")            
        print(f"Box height for {title}: ~ {max_height}em")
        
        col_nr = 0 # only neede if columns are split
        
        # if columns are not split, create new array
        if not split:
            lines.append("")
            lines.append(f"#let {array_name} = (") # create array

        for i in range(len(cg)):
            if i % lines_per_col == 0: # top of new column
                
                if split: # columns are split into separate arrrays                             
                    if i != 0: #, close array of previous column
                        lines.append(")") # close array  
                    # create new array for next column
                    col_nr += 1
                    lines.append("")
                    lines.append(f"#let {array_name}{col_nr} = (") # create array                 
                    
                # add header for new column
                if header != None:
                    lines.append(f"  {header}")

            # add color name to new row
            name = cg[i].basename + cg[i].suffixes[0]
            lines.append(f"  [{name}],")
            
            # add other colors in group
            for color in cg[i].colors:
                rgb = self._rgb(color)
                lines.append(f'  [#rect(fill:rgb("{rgb}"))],')
                
            # check if we need to fill up with empty cells
            color_count = len(cg[i])
            if color_count < groups:
                lines.append('  ' + '[],' * (groups - color_count))

        # close array
        lines.append(")")
        lines.append("")
        return lines

    # save typst arrays of colors to file
    def save_typst_data(self, filename):
        lines = []
        
        # gray colors (gray1 … gray100       
        lines.append("// gray colors")
        lines.append("")
        lines.append("#let colors_gray = (") # create array
        lines.append("  [],[" + "],[".join([str(i) for i in range(GRAY_TABLE_COLS)]) + "],")
        for i in range(len(self.color_table_gray)):
            if i % GRAY_TABLE_COLS == 0:
                # add color name in front of row
                lines.append(f"  [gray{i}],")
            # add color codes
            rgb = self._rgb(self.color_table_gray["gray"+str(i)])
            lines.append(f'  [#rect(fill:rgb("{rgb}"))],')
        lines.append(")") # close array
        lines.append("")
        
        # all colors as 3 separate arrays (3 columns, 5 groups)
        lines += self.typst_array(self.color_groups, "all colors", "colors_all", 3, 5, "[], [], [1], [2], [3], [4],", True )

        # grouped colors (3 columns, 5 groups)
        groups_only = [color for color in self.color_groups if len(color.colors) > 1]
        lines += self.typst_array(groups_only, "grouped colors only", "colors_grouped", 3, 5, "[], [], [1], [2], [3], [4],")

        # single colors (3 coumns, 1 (no) group)
        single_only = [color for color in self.color_groups if len(color.colors) == 1]
        lines += self.typst_array(single_only, "single colors only", "colors_single", 3, 1)

        # write array to file
        f = open(filename, "w")
        f.write('\n'.join([''.join(line) for line in lines]))
        f.close()


    #####            
    # Return typst code to create an array of color data
    #  cg: list of color groups
    #  title: title (comment)
    #  array_name:  name of array in typst
    #  cols:  number of columns
    #  groups: number of groups 
    #  header: string of header to repeat for each column (None if no header)
    #  split: True/False - split cols in individual arrays
    ####
    def html_table(self, cg, title, groups, header=None):
        lines =[]
        
        # Comment to mark start of new array(s)
        lines.append(f"<h2>{title}</h2>")
        lines.append('<table style="padding:0px; white-space:nowrap; white-space:pre; overflow:auto; color:#696969; font-size:8pt" >')
        if header != None:
            lines.append(f"{header}")

        for i in range(len(cg)):
            # add color name to new row
            name = cg[i].basename + cg[i].suffixes[0]
            lines.append(f"<tr><td>{name}</td>")
            
            # add other colors in group
            for color in cg[i].colors:
                rgb = self._rgb(color)
                lines.append(f'<td width=15 style="background:{rgb}; border: 1px solid gray;">&nbsp;</td>')

            # check if we need to fill up with empty cells
            color_count = len(cg[i])
            if color_count < groups:
                lines.append('<td>&nbsp;</td>' * (groups - color_count))
            lines.append('</tr>')
                
        # close table
        lines.append("</table>")
        lines.append("")
        return lines


    # save colors as html
    def save_as_html(self, filename):
        lines = []       
        lines.append("<!DOCTYPE html><html><body>")
        lines.append("<h1>PYGAME colors</h1>")
        lines.append("<h2>gray0 ... gray100 | grey0 ... grey100</h2>")
        lines.append('<table style="padding:0px; white-space:nowrap; white-space:pre; overflow:auto; color:#696969; font-size:8pt" >')
        
        # gray colors (gray1 … gray100
        # write header 
        lines.append('<tr><td>&nbsp;</td>')
        for i in range(GRAY_TABLE_COLS):
            lines.append(f'<td>{i}</td>')
        lines.append('</tr><tr>')

        lines.append('<td>grey</td>')
        for i in range(len(self.color_table_gray)):
            if i % GRAY_TABLE_COLS == 0 and i != 0:
                # add color name in front of row
                lines.append(f"</tr><tr><td>gray{i}</td>")
            # add color codes
            rgb = self._rgb(self.color_table_gray["gray"+str(i)])
            lines.append(f'<td width=15 style="background:{rgb}; border: 1px solid gray;">&nbsp;</td>')
        lines.append("</tr></table>") # close table
        lines.append("")

        # all colors as 3 separate arrays (3 columns, 5 groups)
        header = '<tr><td>&nbsp;</td><td>&nbsp;</td><td>1</td><td>2</td><td>3</td><td>4</td></tr>'
        lines += self.html_table(self.color_groups, "All colors", 5, header)

        # grouped colors (3 columns, 5 groups)
        groups_only = [color for color in self.color_groups if len(color.colors) > 1]
        lines += self.html_table(groups_only, "Grouped colors", 5, header)

        # single colors (3 coumns, 1 (no) group)
        single_only = [color for color in self.color_groups if len(color.colors) == 1]
        lines += self.html_table(single_only, "Single colors", 1)

        # write array to file
        f = open(filename, "w")
        f.write('\n'.join([''.join(line) for line in lines]))
        f.close()

p = PygameColors()
p.save_typst_data("pygame_colors.typ")
p.save_as_html("python_colors.html")
