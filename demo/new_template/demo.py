import sys
import re
import io
import markdown
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, NavigableString
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton,
                             QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QStatusBar)
from PySide6.QtGui import QIcon

class HWPMLConverter:
    def __init__(self):
        # Initialize counters for unique IDs
        self.field_id_counter = 0
        self.inst_id_counter = 1000000
        
        # Define expected order of markdown elements in template
        self.style_mapping_order = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
            'p', 'ul', 'ol', 'a', 'strong', 'em'
        ]
        
        # Initialize template styles mapping
        self.template_styles = {key: None for key in self.style_mapping_order}
        
    def load_template(self, template_path):
        """Load the HWPML template file and extract styles"""
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                self.template_content = file.read()
                
            # Parse the template to extract style information
            self._extract_template_styles()
            
            return True
        except Exception as e:
            print(f"Error loading template: {e}")
            return False
    
    def _extract_template_styles(self):
        """Extract style information from the template in sequential order"""
        soup = BeautifulSoup(self.template_content, 'xml')
        
        # Find all paragraphs in the BODY section
        body_section = soup.find('BODY')
        if not body_section:
            raise ValueError("Template doesn't contain a BODY section")
        
        section = body_section.find('SECTION')
        if not section:
            raise ValueError("Template doesn't contain a SECTION element")
        
        paragraphs = section.find_all('P')
        
        # Map paragraphs to styles in sequence
        current_index = 0
        for p in paragraphs:
            # Skip empty paragraphs or those without content
            text_elem = p.find('TEXT')
            if not text_elem:
                continue
                
            char_elem = text_elem.find('CHAR')
            if not char_elem:
                # Check if this is a link paragraph (has FIELDBEGIN)
                if p.find('FIELDBEGIN') and current_index < len(self.style_mapping_order):
                    # Find the 'a' element in our mapping order
                    link_index = self.style_mapping_order.index('a') if 'a' in self.style_mapping_order else -1
                    if link_index >= 0:
                        current_index = link_index  # Jump to the link position
                        self.template_styles['a'] = self._extract_style_info(p, text_elem)
                        current_index += 1
                continue
            
            # Skip paragraphs with empty text
            content = char_elem.text.strip()
            if not content:
                continue
            
            # Special handling for link elements
            if p.find('FIELDBEGIN') and current_index < len(self.style_mapping_order):
                # Find the 'a' element in our mapping order
                link_index = self.style_mapping_order.index('a') if 'a' in self.style_mapping_order else -1
                if link_index >= 0:
                    current_index = link_index  # Jump to the link position
                    self.template_styles['a'] = self._extract_style_info(p, text_elem)
                    current_index += 1
                continue
            
            # Map the current paragraph to the next expected style
            if current_index < len(self.style_mapping_order):
                style_key = self.style_mapping_order[current_index]
                self.template_styles[style_key] = self._extract_style_info(p, text_elem)
                current_index += 1
        
        # Debug output
        print("Extracted Style Information:")
        for key, value in self.template_styles.items():
            print(f"  {key}: {value}")
    
    def _extract_style_info(self, p_elem, text_elem):
        """Extract style information from a paragraph and text element"""
        para_shape = p_elem.get('ParaShape', '0')
        char_shape = text_elem.get('CharShape', '0')
        
        # For link elements, we need additional information
        if p_elem.find('FIELDBEGIN'):
            field_begin = p_elem.find('FIELDBEGIN')
            field_id = field_begin.get('FieldId', '0')
            inst_id = field_begin.get('InstId', '0')
            link_text = p_elem.find('TEXT', {'CharShape': '10'})
            
            return {
                'para_shape': para_shape,
                'char_shape': char_shape,
                'is_link': True,
                'field_id': field_id,
                'inst_id': inst_id,
                'link_text_shape': link_text.get('CharShape', '10') if link_text else '10'
            }
        
        return {
            'para_shape': para_shape,
            'char_shape': char_shape
        }
    
    def convert_md_to_hwpml(self, md_text, title="No Title", author="No Author", date="No Date"):
        """Convert markdown text to HWPML using the loaded template"""
        if not hasattr(self, 'template_content'):
            raise ValueError("Template has not been loaded. Call load_template() first.")
        
        # Convert markdown to HTML
        html = markdown.markdown(md_text, extensions=['fenced_code', 'tables'], tab_length=2)
        
        # Parse the HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Generate HWPML content
        hwpml_body = self._convert_html_to_hwpml(soup)
        
        # Replace the template body with our converted content
        result = re.sub(
            r'<BODY>.*?<SECTION Id="0">(.*?)</SECTION>.*?</BODY>',
            f'<BODY><SECTION Id="0">{hwpml_body}</SECTION></BODY>',
            self.template_content,
            flags=re.DOTALL
        )
        
        # Replace title, author, and date
        result = result.replace("<TITLE>No Title</TITLE>", f"<TITLE>{title}</TITLE>")
        result = result.replace("<AUTHOR>No Author</AUTHOR>", f"<AUTHOR>{author}</AUTHOR>")
        result = result.replace("<DATE>No Date</DATE>", f"<DATE>{date}</DATE>")
        
        return result
    
    def _convert_html_to_hwpml(self, soup):
        """Convert HTML to HWPML body content"""
        hwpml_content = ""
        
        # Process each top-level element
        for element in soup:
            if isinstance(element, NavigableString):
                continue
            
            hwpml_content += self._convert_element_to_hwpml(element)
        
        return hwpml_content
    
    def _convert_element_to_hwpml(self, element):
        """Convert an HTML element to its HWPML equivalent"""
        tag_name = element.name
        
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return self._convert_header_to_hwpml(element)
        elif tag_name == 'p':
            return self._convert_paragraph_to_hwpml(element)
        elif tag_name in ['ul', 'ol']:
            return self._convert_list_to_hwpml(element)
        elif tag_name == 'table':
            return self._convert_table_to_hwpml(element)
        else:
            # Default handling for unknown elements
            return ""
    
    def _convert_header_to_hwpml(self, header_elem):
        """Convert an HTML header to HWPML"""
        level = int(header_elem.name[1])  # Extract header level (1-6)
        style_key = f'h{level}'
        
        if style_key not in self.template_styles or self.template_styles[style_key] is None:
            # Fallback to default style if not found in template
            para_shape = "0"
            char_shape = str(level)  # Use level as char shape
        else:
            style = self.template_styles[style_key]
            para_shape = style['para_shape']
            char_shape = style['char_shape']
        
        text = header_elem.get_text()
        
        return f'<P ParaShape="{para_shape}" Style="0"><TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT></P>\n'
    
    def _convert_paragraph_to_hwpml(self, p_elem):
        """Convert an HTML paragraph to HWPML"""
        if 'p' not in self.template_styles or self.template_styles['p'] is None:
            para_shape = "0"
            char_shape = "1"
        else:
            style = self.template_styles['p']
            para_shape = style['para_shape']
            char_shape = style['char_shape']
        
        # Process paragraph content with potential formatting
        content = ""
        
        for child in p_elem.children:
            if isinstance(child, NavigableString):
                text = str(child)
                if text.strip():
                    content += f'<TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT>'
            elif child.name == 'a':
                content += self._convert_link_to_hwpml(child)
            elif child.name in ['strong', 'b']:
                content += self._convert_bold_to_hwpml(child)
            elif child.name in ['em', 'i']:
                content += self._convert_italic_to_hwpml(child)
        
        if not content:
            content = f'<TEXT CharShape="{char_shape}"><CHAR/></TEXT>'
        
        return f'<P ParaShape="{para_shape}" Style="0">{content}</P>\n'
    
    def _convert_list_to_hwpml(self, list_elem, depth=0):
        """Convert an HTML list (ul/ol) to HWPML"""
        hwpml = ""
        is_ordered = list_elem.name == 'ol'
        
        # Get style from template
        style_key = 'ol' if is_ordered else 'ul'
        if style_key not in self.template_styles or self.template_styles[style_key] is None:
            para_shape = str(depth + 1)  # Default based on depth
            char_shape = "1"
        else:
            style = self.template_styles[style_key]
            para_shape = style['para_shape']
            char_shape = style['char_shape']
        
        # Process list items
        item_counter = 1
        for li in list_elem.find_all('li', recursive=False):
            # Create paragraph for the list item
            content = ""
            
            # Add bullet/number prefix
            prefix = f"{item_counter}. " if is_ordered else "• "
            content += f'<TEXT CharShape="{char_shape}"><CHAR>{prefix}</CHAR></TEXT>'
            
            # Process list item content
            for child in li.children:
                if isinstance(child, NavigableString):
                    text = str(child).strip()
                    if text:
                        content += f'<TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT>'
                elif child.name in ['ul', 'ol']:
                    # Skip nested lists, they'll be processed separately
                    continue
                elif child.name == 'a':
                    content += self._convert_link_to_hwpml(child)
                elif child.name in ['strong', 'b']:
                    content += self._convert_bold_to_hwpml(child)
                elif child.name in ['em', 'i']:
                    content += self._convert_italic_to_hwpml(child)
            
            hwpml += f'<P ParaShape="{para_shape}" Style="0">{content}</P>\n'
            
            # Process nested lists
            for nested_list in li.find_all(['ul', 'ol'], recursive=False):
                hwpml += self._convert_list_to_hwpml(nested_list, depth + 1)
            
            if is_ordered:
                item_counter += 1
        
        return hwpml
    
    def _convert_link_to_hwpml(self, a_elem):
        """Convert an HTML link to HWPML"""
        # Generate unique field IDs
        self.field_id_counter += 1
        field_id = str(self.field_id_counter)
        
        self.inst_id_counter += 1
        inst_id = str(self.inst_id_counter)
        
        url = a_elem.get('href', '').replace('/', '\\/')
        text = a_elem.get_text()
        
        # Get style from template
        if 'a' not in self.template_styles or self.template_styles['a'] is None:
            char_shape = "1"
            link_text_shape = "10"  # Default link text style
        else:
            style = self.template_styles['a']
            char_shape = style['char_shape']
            link_text_shape = style.get('link_text_shape', '10')
        
        command = f"{url};1;0;0;"
        
        field_begin = (
            f'<TEXT CharShape="{char_shape}">'
            f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" '
            f'FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
            f'</TEXT>'
        )
        
        link_text = f'<TEXT CharShape="{link_text_shape}"><CHAR>{text}</CHAR></TEXT>'
        
        field_end = (
            f'<TEXT CharShape="{char_shape}">'
            f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
            f'<CHAR/>'
            f'</TEXT>'
        )
        
        return field_begin + link_text + field_end
    
    def _convert_bold_to_hwpml(self, elem):
        """Convert bold text to HWPML"""
        if 'strong' not in self.template_styles or self.template_styles['strong'] is None:
            char_shape = "8"  # Default bold style
        else:
            style = self.template_styles['strong']
            char_shape = style['char_shape']
        
        text = elem.get_text()
        return f'<TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT>'
    
    def _convert_italic_to_hwpml(self, elem):
        """Convert italic text to HWPML"""
        if 'em' not in self.template_styles or self.template_styles['em'] is None:
            char_shape = "9"  # Default italic style
        else:
            style = self.template_styles['em']
            char_shape = style['char_shape']
        
        text = elem.get_text()
        return f'<TEXT CharShape="{char_shape}"><CHAR>{text}</CHAR></TEXT>'
    
    def _convert_table_to_hwpml(self, table_elem):
        """Convert an HTML table to HWPML"""
        rows = table_elem.find_all('tr')
        row_count = len(rows)
        col_count = max(len(row.find_all(['td', 'th'])) for row in rows) if rows else 0
        
        # Default table width
        total_table_width = 41950
        cell_width = total_table_width // col_count if col_count > 0 else 20975
        
        # Generate a unique ID for the table
        inst_id = self.inst_id_counter
        self.inst_id_counter += 1
        
        # Build table structure
        hwpml = f"""
<TABLE BorderFill="3" CellSpacing="0" ColCount="{col_count}" PageBreak="Cell" RepeatHeader="true" RowCount="{row_count}">
<SHAPEOBJECT InstId="{inst_id}" Lock="false" NumberingType="Table" TextWrap="TopAndBottom" ZOrder="1">
<SIZE Height="3846" HeightRelTo="Absolute" Protect="false" Width="{total_table_width}" WidthRelTo="Absolute"/>
<POSITION AffectLSpacing="false" AllowOverlap="false" FlowWithText="true" HoldAnchorAndSO="false" HorzAlign="Left" HorzOffset="0" HorzRelTo="Column" TreatAsChar="false" VertAlign="Top" VertOffset="0" VertRelTo="Para"/>
<OUTSIDEMARGIN Bottom="283" Left="283" Right="283" Top="283"/>
</SHAPEOBJECT>
<INSIDEMARGIN Bottom="141" Left="510" Right="510" Top="141"/>"""
        
        # Process rows and cells
        for row_index, row in enumerate(rows):
            hwpml += f"\n<ROW>"
            cells = row.find_all(['td', 'th'])
            
            # Fill in missing cells if any
            while len(cells) < col_count:
                cells.append(None)
            
            for cell_index in range(col_count):
                cell = cells[cell_index] if cell_index < len(cells) else None
                
                # Determine border style based on row position
                if row_index == 0:
                    border_fill_id = 3  # First row: solid borders on top and bottom
                elif row_index == row_count - 1:
                    border_fill_id = 4  # Last row: dotted top, solid bottom
                else:
                    border_fill_id = 6  # Middle rows: dotted borders on top and bottom
                
                hwpml += f"""
<CELL BorderFill="{border_fill_id}" ColAddr="{cell_index}" ColSpan="1" Dirty="false" Editable="false" HasMargin="false" Header="false" Height="282" Protect="false" RowAddr="{row_index}" RowSpan="1" Width="{cell_width}">
<CELLMARGIN Bottom="141" Left="510" Right="510" Top="141"/>
<PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center">
<P ParaShape="0" Style="0">"""
                
                # Add cell content
                hwpml += self._convert_cell_content(cell)
                
                hwpml += """
</P>
</PARALIST>
</CELL>"""
            
            hwpml += f"\n</ROW>"
        
        hwpml += "\n</TABLE>"
        
        # Wrap the table in paragraph tags for proper placement
        return f'<P ParaShape="0" Style="0"><TEXT CharShape="0">{hwpml}<CHAR/></TEXT></P>\n'
    
    def _convert_cell_content(self, cell):
        """Convert HTML cell content to HWPML"""
        if cell is None:
            return '<TEXT CharShape="0"><CHAR>&#160;</CHAR></TEXT>'  # Empty cell
        
        hwpml = ''
        
        if len(list(cell.children)) == 0:
            content = cell.string if cell.string else "&#160;"
            return f'<TEXT CharShape="0"><CHAR>{content}</CHAR></TEXT>'
        
        for child in cell.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    hwpml += f'<TEXT CharShape="0"><CHAR>{text}</CHAR></TEXT>'
            elif child.name in ['strong', 'b']:
                hwpml += self._convert_bold_to_hwpml(child)
            elif child.name in ['em', 'i']:
                hwpml += self._convert_italic_to_hwpml(child)
            elif child.name == 'a':
                hwpml += self._convert_link_to_hwpml(child)
        
        return hwpml if hwpml else '<TEXT CharShape="0"><CHAR>&#160;</CHAR></TEXT>'


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown to HWP Converter with Template")
        self.setGeometry(100, 100, 600, 400)
        
        self.converter = HWPMLConverter()
        self.template_path = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create text edit area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Paste your markdown text here or load from clipboard")
        self.layout.addWidget(self.text_edit)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        
        # Add buttons
        self.template_button = QPushButton("Select Template")
        self.clipboard_button = QPushButton("Load from Clipboard")
        self.save_button = QPushButton("Select Output Path")
        self.convert_button = QPushButton("Convert")
        
        self.button_layout.addWidget(self.template_button)
        self.button_layout.addWidget(self.clipboard_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.convert_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Connect signals
        self.template_button.clicked.connect(self.select_template)
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.save_button.clicked.connect(self.select_output_path)
        self.convert_button.clicked.connect(self.convert)
        
        # Initialize variables
        self.output_path = ""
    
    def select_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Template File", "", "HWP Files (*.hml)")
        if file_path:
            self.template_path = file_path
            success = self.converter.load_template(file_path)
            if success:
                self.status_bar.showMessage(f"Template loaded: {file_path}")
            else:
                self.status_bar.showMessage("Error loading template")
    
    def load_from_clipboard(self):
        clipboard = QApplication.clipboard()
        md_text = clipboard.text()
        if md_text:
            self.text_edit.setPlainText(md_text)
            self.status_bar.showMessage("Text loaded from clipboard")
        else:
            self.status_bar.showMessage("No text in clipboard")
    
    def select_output_path(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save HWP File", "", "HWP Files (*.hml)")
        if file_path:
            self.output_path = file_path
            self.status_bar.showMessage(f"Output path set: {file_path}")
    
    def convert(self):
        if not self.template_path:
            self.status_bar.showMessage("Error: Please select a template first")
            return
        
        if not self.output_path:
            self.status_bar.showMessage("Error: Please select an output path first")
            return
        
        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_bar.showMessage("Error: No text to convert")
            return
        
        self.status_bar.showMessage("Converting...")
        
        try:
            # Check for YAML frontmatter
            title = "No Title"
            author = "No Author"
            date = "No Date"
            
            # Look for title, author, date in YAML frontmatter
            t = re.search(r"(?<=title: ).*", md_text)
            a = re.search(r"(?<=author: ).*", md_text)
            d = re.search(r"(?<=date: ).*", md_text)
            
            if t:
                title = t.group(0).strip()
            if a:
                author = a.group(0).strip()
            if d:
                date = d.group(0).strip()
            
            # Remove YAML frontmatter
            md_text = re.sub(r'^---\n([\s\S]*?)\n---\n', '', md_text, flags=re.DOTALL)
            
            # Convert markdown to HWPML
            hwpml_content = self.converter.convert_md_to_hwpml(md_text, title, author, date)
            
            # Save the result
            with io.open(self.output_path, "w", encoding="utf-8") as f:
                f.write(hwpml_content)
            
            self.status_bar.showMessage(f"Conversion completed: {self.output_path}")
        
        except Exception as e:
            self.status_bar.showMessage(f"Error during conversion: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
