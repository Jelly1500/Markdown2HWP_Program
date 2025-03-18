import sys
import re
import io
import markdown
import os
from datetime import datetime

from bs4 import BeautifulSoup, NavigableString
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QFileDialog, 
    QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QLabel, QLineEdit,
    QFrame, QSplitter, QProgressBar, QMessageBox, QComboBox, QToolBar,
    QSizePolicy
)
from PySide6.QtGui import QIcon, QFont, QAction, QColor, QPalette, QTextCursor
from PySide6.QtCore import Qt, QSize, QTimer, Signal, QThread


# HWPML 태그 상수 정의
TXT_END = '</CHAR></TEXT></P>'
H1_START = '<P ParaShape="0" Style="0"><TEXT CharShape="1"><CHAR>'
H2_START = '<P ParaShape="0" Style="0"><TEXT CharShape="2"><CHAR>'
H3_START = '<P ParaShape="0" Style="0"><TEXT CharShape="3"><CHAR>'
H4_START = '<P ParaShape="0" Style="0"><TEXT CharShape="4"><CHAR>'

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<HWPML Style="embed" SubVersion="9.0.1.0" Version="2.9">
<HEAD SecCnt="1">
<DOCSUMMARY>
<TITLE>___TITLE___</TITLE>
<AUTHOR>___AUTHOR___</AUTHOR>
<DATE>___DATE___</DATE>
</DOCSUMMARY>
<DOCSETTING>
<BEGINNUMBER Endnote="1" Equation="1" Footnote="1" Page="1" Picture="1" Table="1" />
<CARETPOS List="0" Para="20" Pos="6" />
</DOCSETTING>
<MAPPINGTABLE>
<FACENAMELIST>
<FONTFACE Count="2" Lang="Hangul">
<FONT Id="0" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
<FONT Id="1" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
</FONTFACE>
<FONTFACE Count="2" Lang="Latin">
<FONT Id="0" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
<FONT Id="1" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
</FONTFACE>
<FONTFACE Count="2" Lang="Hanja">
<FONT Id="0" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
<FONT Id="1" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
</FONTFACE>
<FONTFACE Count="2" Lang="Japanese">
<FONT Id="0" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
<FONT Id="1" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
</FONTFACE>
<FONTFACE Count="2" Lang="Other">
<FONT Id="0" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
<FONT Id="1" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
</FONTFACE>
<FONTFACE Count="2" Lang="Symbol">
<FONT Id="0" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
<FONT Id="1" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
</FONTFACE>
<FONTFACE Count="2" Lang="User">
<FONT Id="0" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
<FONT Id="1" Name="맑은 고딕" Type="ttf">
<TYPEINFO ArmStyle="1" Contrast="0" FamilyType="2" Letterform="1" Midline="1" Proportion="4" StrokeVariation="1" Weight="6" XHeight="1" />
</FONT>
</FONTFACE>
</FACENAMELIST>
<CHARSHAPELIST Count="9">
    <CHARSHAPE BorderFillId="2" Height="1000" Id="0" ShadeColor="4294967295" SymMark="0" TextColor="0" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
    </CHARSHAPE>
    <CHARSHAPE BorderFillId="2" Height="2000" Id="1" ShadeColor="4294967295" SymMark="0" TextColor="0" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <BOLD />
    </CHARSHAPE>
    <CHARSHAPE BorderFillId="2" Height="1600" Id="2" ShadeColor="4294967295" SymMark="0" TextColor="0" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <BOLD />
    </CHARSHAPE>
    <CHARSHAPE BorderFillId="2" Height="1200" Id="3" ShadeColor="4294967295" SymMark="0" TextColor="0" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <BOLD />
    </CHARSHAPE>
    <CHARSHAPE BorderFillId="2" Height="1000" Id="4" ShadeColor="4294967295" SymMark="0" TextColor="0" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <BOLD />
    </CHARSHAPE>
    <CHARSHAPE BorderFillId="2" Height="2500" Id="5" ShadeColor="4294967295" SymMark="0" TextColor="0" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <BOLD />
    </CHARSHAPE>
    <CHARSHAPE BorderFillId="2" Height="1000" Id="6" ShadeColor="4294967295" SymMark="0" TextColor="0" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <BOLD />
    </CHARSHAPE>
    <CHARSHAPE BorderFillId="2" Height="1000" Id="7" ShadeColor="4294967295" SymMark="0" TextColor="0" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <ITALIC />
    </CHARSHAPE>
    <CHARSHAPE BorderFillId="2" Height="1000" Id="8" ShadeColor="4294967295" SymMark="0" TextColor="14090243" UseFontSpace="false" UseKerning="false">
        <FONTID Hangul="1" Hanja="1" Japanese="1" Latin="1" Other="1" Symbol="1" User="1" />
        <RATIO Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHARSPACING Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <RELSIZE Hangul="100" Hanja="100" Japanese="100" Latin="100" Other="100" Symbol="100" User="100" />
        <CHAROFFSET Hangul="0" Hanja="0" Japanese="0" Latin="0" Other="0" Symbol="0" User="0" />
        <UNDERLINE Color="0" Shape="Solid" Type="Single" />
    </CHARSHAPE>
</CHARSHAPELIST>
<PARASHAPELIST Count="9">
    <PARASHAPE Align="Justify" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="true" Condense="0" FontLineHeight="false" HeadingType="None" Id="0" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="0" Left="0" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
    <PARASHAPE Align="Justify" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="true" Condense="0" FontLineHeight="false" HeadingType="None" Id="1" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="-2104" Left="2104" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
    <PARASHAPE Align="Justify" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="true" Condense="0" FontLineHeight="false" HeadingType="None" Id="2" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="-2104" Left="4208" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
    <PARASHAPE Align="Justify" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="true" Condense="0" FontLineHeight="false" HeadingType="None" Id="3" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="-2104" Left="6312" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
    <PARASHAPE Align="Justify" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="true" Condense="0" FontLineHeight="false" HeadingType="None" Id="4" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="-2104" Left="8416" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
    <PARASHAPE Align="Justify" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="true" Condense="0" FontLineHeight="false" HeadingType="None" Id="5" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="-2104" Left="10520" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
    <PARASHAPE Align="Justify" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="true" Condense="0" FontLineHeight="false" HeadingType="None" Id="6" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="-2104" Left="12624" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
    <!-- Id="7"과 Id="8"은 리스트와 무관하므로 수정하지 않음 -->
    <PARASHAPE Align="Center" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="false" Condense="0" FontLineHeight="false" HeadingType="None" Id="7" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="0" Left="0" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
    <PARASHAPE Align="Right" AutoSpaceEAsianEng="false" AutoSpaceEAsianNum="false" BreakLatinWord="KeepWord" BreakNonLatinWord="false" Condense="0" FontLineHeight="false" HeadingType="None" Id="8" KeepLines="false" KeepWithNext="false" Level="0" LineWrap="Break" PageBreakBefore="false" SnapToGrid="true" TabDef="0" VerAlign="Baseline" WidowOrphan="false">
        <PARAMARGIN Indent="0" Left="0" LineSpacing="160" LineSpacingType="Percent" Next="0" Prev="0" Right="0" />
        <PARABORDER BorderFill="2" Connect="false" IgnoreMargin="false" />
    </PARASHAPE>
</PARASHAPELIST>
</MAPPINGTABLE>
<COMPATIBLEDOCUMENT TargetProgram="None">
<LAYOUTCOMPATIBILITY AdjustBaselineInFixedLinespacing="false" AdjustBaselineOfObjectToBottom="false" AdjustLineheightToFont="false" AdjustMarginFromAdjustLineheight="false" AdjustParaBorderOffsetWithBorder="false" AdjustParaBorderfillToSpacing="false" AdjustVertPosOfLine="false" ApplyAtLeastToPercent100Pct="false" ApplyCharSpacingToCharGrid="false" ApplyExtendHeaderFooterEachSection="false" ApplyFontWeightToBold="false" ApplyFontspaceToLatin="false" ApplyMinColumnWidthTo1mm="false" ApplyNextspacingOfLastPara="false" ApplyParaBorderToOutside="false" ApplyPrevspacingBeneathObject="false" ApplyTabPosBasedOnSegment="false" BaseCharUnitOfIndentOnFirstChar="false" BaseCharUnitOnEAsian="false" BaseLinespacingOnLinegrid="false" BreakTabOverLine="false" ConnectParaBorderfillOfEqualBorder="false" DoNotAdjustEmptyAnchorLine="false" DoNotAdjustWordInJustify="false" DoNotAlignLastForbidden="false" DoNotAlignLastPeriod="false" DoNotAlignWhitespaceOnRight="false" DoNotApplyAutoSpaceEAsianEng="false" DoNotApplyAutoSpaceEAsianNum="false" DoNotApplyColSeparatorAtNoGap="false" DoNotApplyExtensionCharCompose="false" DoNotApplyGridInHeaderFooter="false" DoNotApplyHeaderFooterAtNoSpace="false" DoNotApplyImageEffect="false" DoNotApplyLinegridAtNoLinespacing="false" DoNotApplyShapeComment="false" DoNotApplyStrikeoutWithUnderline="false" DoNotApplyVertOffsetOfForward="false" DoNotApplyWhiteSpaceHeight="false" DoNotFormattingAtBeneathAnchor="false" DoNotHoldAnchorOfTable="false" ExtendLineheightToOffset="false" ExtendLineheightToParaBorderOffset="false" ExtendVertLimitToPageMargins="false" FixedUnderlineWidth="false" OverlapBothAllowOverlap="false" TreatQuotationAsLatin="false" UseInnerUnderline="false" UseLowercaseStrikeout="false" />
</COMPATIBLEDOCUMENT>
</HEAD>
<BODY>
<SECDEF CharGrid="0" FirstBorder="false" FirstFill="false" LineGrid="0" OutlineShape="1" SpaceColumns="1134" TabStop="8000" TextDirection="0" TextVerticalWidthHead="0">
<STARTNUMBER Equation="0" Figure="0" Page="0" PageStartsOn="Both" Table="0" />
<HIDE Border="false" EmptyLine="false" Fill="false" Footer="false" Header="false" MasterPage="false" PageNumPos="false" />
<PAGEDEF GutterType="LeftOnly" Height="84188" Landscape="0" Width="59528">
<PAGEMARGIN Bottom="4252" Footer="4252" Gutter="0" Header="4252" Left="8504" Right="8504" Top="5668" />
</PAGEDEF>
<FOOTNOTESHAPE>
<AUTONUMFORMAT SuffixChar=")" Superscript="false" Type="Digit" />
<NOTELINE Length="5cm" Type="Solid" Width="0.12mm" />
<NOTESPACING AboveLine="850" BelowLine="567" BetweenNotes="283" />
<NOTENUMBERING NewNumber="1" Type="Continuous" />
<NOTEPLACEMENT BeneathText="false" Place="EachColumn" />
</FOOTNOTESHAPE>
<ENDNOTESHAPE>
<AUTONUMFORMAT SuffixChar=")" Superscript="false" Type="Digit" />
<NOTELINE Length="14692344" Type="Solid" Width="0.12mm" />
<NOTESPACING AboveLine="850" BelowLine="567" BetweenNotes="0" />
<NOTENUMBERING NewNumber="1" Type="Continuous" />
<NOTEPLACEMENT BeneathText="false" Place="EndOfDocument" />
</ENDNOTESHAPE>
<PAGEBORDERFILL BorferFill="1" FillArea="Paper" FooterInside="false" HeaderInside="false" TextBorder="true" Type="Both">
<PAGEOFFSET Bottom="1417" Left="1417" Right="1417" Top="1417" />
</PAGEBORDERFILL>
<PAGEBORDERFILL BorferFill="1" FillArea="Paper" FooterInside="false" HeaderInside="false" TextBorder="true" Type="Even">
<PAGEOFFSET Bottom="1417" Left="1417" Right="1417" Top="1417" />
</PAGEBORDERFILL>
<PAGEBORDERFILL BorferFill="1" FillArea="Paper" FooterInside="false" HeaderInside="false" TextBorder="true" Type="Odd">
<PAGEOFFSET Bottom="1417" Left="1417" Right="1417" Top="1417" />
</PAGEBORDERFILL>
</SECDEF>
<SECTION Id="0">
"""

FOOTER = """</SECTION></BODY><TAIL></TAIL></HWPML>"""

INTRO = """
<P ParaShape="7" Style="0"><TEXT CharShape="5"><CHAR>___TITLE___</CHAR></TEXT></P>
<P ParaShape="8" Style="0"><TEXT CharShape="0"><CHAR>작성자 : ___AUTHOR___</CHAR></TEXT></P>
<P ParaShape="8" Style="0"><TEXT CharShape="0"><CHAR>작성일 : ___DATE___</CHAR></TEXT></P>
"""
class MarkdownPreviewWidget(QTextEdit):
    """Widget for displaying a live preview of the markdown content"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #333;
            }
        """)
        
    def update_preview(self, markdown_text):
        """Update the preview with rendered markdown"""
        if not markdown_text:
            self.setHtml("<p style='color: #999; font-style: italic;'>Preview will appear here</p>")
            return
            
        try:
            html = markdown.markdown(markdown_text, extensions=['fenced_code', 'tables'], tab_length=2)
            self.setHtml(html)
        except Exception as e:
            self.setHtml(f"<p style='color: #f44336;'>Error in preview: {str(e)}</p>")



class ConversionWorker(QThread):
    """Worker thread for handling the conversion process"""
    finished = Signal(bool, str)
    progress = Signal(int)
    
    def __init__(self, md_text, save_path, title, author, date):
        super().__init__()
        self.md_text = md_text
        self.save_path = save_path
        self.title = title.strip() or "제목 없음"
        self.author = author.strip() or "작성자"
        self.date = date.strip() or datetime.now().strftime("%Y-%m-%d") 
        
    def run(self):
        try:
            # Simulate progress for better UX
            self.progress.emit(10)
            
            # Clean the markdown text
            self.md_text = re.sub(r'^---\n([\s\S]*?)\n---\n', '', self.md_text, flags=re.MULTILINE)

            self.progress.emit(30)
            
            # Convert markdown to HTML
            html = markdown.markdown(self.md_text, extensions=['fenced_code', 'tables'], tab_length=2)
            self.progress.emit(50)
            
            # Convert HTML to HWPML
            soup = BeautifulSoup(html, 'html.parser')
            hwpml_content = convert_html_to_hwpml(soup)
            self.progress.emit(70)
            
            # Create the final HWPML document
            hwpml = HEADER + INTRO + hwpml_content + FOOTER
            hwpml = hwpml.replace("___TITLE___", self.title)
            hwpml = hwpml.replace("___AUTHOR___", self.author)
            hwpml = hwpml.replace("___DATE___", self.date)
            self.progress.emit(90)
            
            # Save the file
            with io.open(self.save_path, "w", encoding="utf-8") as f:
                f.write(hwpml)
                
            self.progress.emit(100)
            self.finished.emit(True, f"Successfully converted and saved to {self.save_path}")
            
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup window properties
        self.setWindowTitle("MD to HWP Converter")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        # Apply modern styling
        self.apply_styling()
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create metadata section
        self.create_metadata_section()
        
        # Create editor and preview splitter
        self.create_editor_preview()
        
        # Create status bar and progress
        self.create_status_section()
        
        # Create bottom buttons
        self.create_action_buttons()
        
        # Initialize variables
        self.save_path = ""
        
        # Connect signals
        self.connect_signals()
        
        # Set default values
        self.set_default_values()
        
    def apply_styling(self):
        """Apply modern styling to the application"""
        # Set application font
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-weight: normal;
                color: #424242;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #F5F5F5;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QStatusBar {
                background-color: #EEEEEE;
                color: #424242;
            }
            QFrame#separator {
                background-color: #E0E0E0;
            }
        """)
    
    def create_toolbar(self):
        """Create the application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setMovable(False)
        
        # New file action
        new_action = QAction("New", self)
        new_action.setStatusTip("Create a new document")
        new_action.triggered.connect(self.new_document)
        toolbar.addAction(new_action)
        
        # Open file action
        open_action = QAction("Open", self)
        open_action.setStatusTip("Open an existing document")
        open_action.triggered.connect(self.open_document)
        toolbar.addAction(open_action)
        
        # Save as markdown action
        save_md_action = QAction("Save MD", self)
        save_md_action.setStatusTip("Save as Markdown file")
        save_md_action.triggered.connect(self.save_markdown)
        toolbar.addAction(save_md_action)
        
        toolbar.addSeparator()
        
        # Theme selector
        theme_label = QLabel("Theme:")
        toolbar.addWidget(theme_label)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark"])
        self.theme_selector.setCurrentIndex(0)
        self.theme_selector.currentIndexChanged.connect(self.change_theme)
        toolbar.addWidget(self.theme_selector)
        
        self.addToolBar(toolbar)
    
    def create_metadata_section(self):
        """Create the metadata input section"""
        metadata_frame = QFrame()
        metadata_frame.setFrameShape(QFrame.StyledPanel)
        metadata_frame.setStyleSheet("QFrame { background-color: white; border-radius: 6px; padding: 10px; }")
        
        metadata_layout = QVBoxLayout(metadata_frame)
        metadata_layout.setContentsMargins(10, 10, 10, 10)
        
        metadata_title = QLabel("Document Metadata")
        metadata_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        metadata_layout.addWidget(metadata_title)
        
        # Create form layout for metadata fields
        form_layout = QHBoxLayout()
        form_layout.setSpacing(15)
        
        # Title field
        title_layout = QVBoxLayout()
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter document title")
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        form_layout.addLayout(title_layout, 2)
        
        # Author field
        author_layout = QVBoxLayout()
        author_label = QLabel("Author:")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Enter author name")
        author_layout.addWidget(author_label)
        author_layout.addWidget(self.author_input)
        form_layout.addLayout(author_layout, 1)
        
        # Date field
        date_layout = QVBoxLayout()
        date_label = QLabel("Date:")
        self.date_input = QLineEdit()
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_input.setText(today)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        form_layout.addLayout(date_layout, 1)
        
        metadata_layout.addLayout(form_layout)
        self.main_layout.addWidget(metadata_frame)
    
    def create_editor_preview(self):
        """Create the editor and preview area"""
        # Create splitter for editor and preview
        splitter = QSplitter(Qt.Horizontal)
        
        # Create editor widget
        editor_frame = QFrame()
        editor_frame.setFrameShape(QFrame.StyledPanel)
        editor_frame.setStyleSheet("QFrame { background-color: white; border-radius: 6px; }")
        
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        editor_header = QLabel("Markdown Editor")
        editor_header.setAlignment(Qt.AlignCenter)
        editor_header.setStyleSheet("background-color: #f5f5f5; padding: 8px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px;")
        
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("마크다운 텍스트를 여기에 붙여넣어 주세요...")
        self.editor.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        editor_layout.addWidget(editor_header)
        editor_layout.addWidget(self.editor)
        
        # Create preview widget
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_frame.setStyleSheet("QFrame { background-color: white; border-radius: 6px; }")
        
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_header = QLabel("Preview")
        preview_header.setAlignment(Qt.AlignCenter)
        preview_header.setStyleSheet("background-color: #f5f5f5; padding: 8px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px;")
        
        self.preview = MarkdownPreviewWidget()
        
        preview_layout.addWidget(preview_header)
        preview_layout.addWidget(self.preview)
        
        # Add widgets to splitter
        splitter.addWidget(editor_frame)
        splitter.addWidget(preview_frame)
        splitter.setSizes([500, 500])  # Equal initial sizes
        
        self.main_layout.addWidget(splitter, 1)  # Give it stretch factor
    
    def create_status_section(self):
        """Create status bar and progress indicator"""
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(0, 5, 0, 5)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(20)
        
        status_layout.addWidget(self.progress_bar)
        
        self.main_layout.addWidget(status_frame)
        
        # Set up status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_action_buttons(self):
        """Create action buttons at the bottom"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Add spacer to push buttons to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button_layout.addWidget(spacer)
        
        # Clipboard button
        self.clipboard_button = QPushButton("클립보드에서 붙여넣기")
        self.clipboard_button.setMinimumWidth(150)
        button_layout.addWidget(self.clipboard_button)
        
        # Save path button
        self.path_button = QPushButton("저장 위치 선택")
        self.path_button.setMinimumWidth(150)
        button_layout.addWidget(self.path_button)
        
        # Convert button
        self.convert_button = QPushButton("hwp로 변환")
        self.convert_button.setMinimumWidth(150)
        self.convert_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """)
        button_layout.addWidget(self.convert_button)
        
        self.main_layout.addLayout(button_layout)
    
    def connect_signals(self):
        """Connect all signals to slots"""
        # Button connections
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.path_button.clicked.connect(self.select_save_path)
        self.convert_button.clicked.connect(self.convert_md_to_hwp)
        
        # Editor connection for live preview
        self.editor.textChanged.connect(self.update_preview)
        
        # Metadata validation
        self.title_input.textChanged.connect(self.validate_inputs)
        self.author_input.textChanged.connect(self.validate_inputs)
    
    def set_default_values(self):
        """Set default values for the application"""
        # Set initial preview message
        self.preview.setHtml("<p style='color: #999; font-style: italic; text-align: center;'>Preview will appear here</p>")
        
        # Disable convert button until we have a save path
        self.convert_button.setEnabled(False)
        
        # Set up a timer for delayed preview updates (to avoid excessive updates)
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.delayed_preview_update)
    
    def update_preview(self):
        """Start timer for delayed preview update"""
        self.preview_timer.start(300)  # 300ms delay
    
    def delayed_preview_update(self):
        """Update the preview after a delay"""
        markdown_text = self.editor.toPlainText()
        self.preview.update_preview(markdown_text)
    
    def load_from_clipboard(self):
        """Load markdown from clipboard"""
        clipboard = QApplication.clipboard()
        md_text = clipboard.text()
        
        if md_text:
            # Check for YAML frontmatter and extract metadata
            frontmatter = re.search(r"^---\s*\n(.*?)\n---\s*\n", md_text, re.DOTALL)
            if frontmatter:
                yaml_text = frontmatter.group(1)
                
                # Try to extract title
                title_match = re.search(r"title:\s*(.*)", yaml_text)
                if title_match and title_match.group(1).strip():
                    self.title_input.setText(title_match.group(1).strip())
                
                # Try to extract author
                author_match = re.search(r"author:\s*(.*)", yaml_text)
                if author_match and author_match.group(1).strip():
                    self.author_input.setText(author_match.group(1).strip())
                
                # Try to extract date
                date_match = re.search(r"date:\s*(.*)", yaml_text)
                if date_match and date_match.group(1).strip():
                    self.date_input.setText(date_match.group(1).strip())
            
            self.editor.setPlainText(md_text)
            self.status_bar.showMessage("Pasted text from clipboard", 3000)
        else:
            self.status_bar.showMessage("Clipboard does not contain text", 3000)
    
    def select_save_path(self):
        """Select the save location for the HWP file"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "Save HWP File", 
            os.path.expanduser("~/Documents"),
            "HWP Files (*.hml)"
        )
        
        if file_name:
            # Ensure the file has .hml extension
            if not file_name.lower().endswith('.hml'):
                file_name += '.hml'
            
            self.save_path = file_name
            self.status_bar.showMessage(f"Save location: {self.save_path}", 3000)
            
            # Update window title
            file_basename = os.path.basename(file_name)
            self.setWindowTitle(f"MD to HWP Converter - {file_basename}")
            
            # Enable convert button
            self.validate_inputs()
        else:
            self.status_bar.showMessage("No save location selected", 3000)
    
    def validate_inputs(self):
        """Validate that we have the minimum required inputs"""
        has_content = bool(self.editor.toPlainText().strip())
        has_save_path = bool(self.save_path)
        
        self.convert_button.setEnabled(has_content and has_save_path)
    
    def convert_md_to_hwp(self):
        """Convert markdown to HWP format"""
        if not self.save_path:
            QMessageBox.warning(self, "Missing Save Location", 
                               "Please select a save location first.")
            return
        
        md_text = self.editor.toPlainText()
        if not md_text:
            QMessageBox.warning(self, "Empty Document", 
                               "There is no content to convert.")
            return
        
        title = self.title_input.text().strip() or "Untitled Document"
        author = self.author_input.text().strip() or "Unknown Author"
        date = self.date_input.text().strip() or datetime.now().strftime("%Y-%m-%d")
        
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Converting document...")
        
        # Disable UI during conversion
        self.setEnabled(False)
        
        # Create and start worker thread
        self.worker = ConversionWorker(md_text, self.save_path, title, author, date)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()
    
    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar.setValue(value)
    
    def conversion_finished(self, success, message):
        """Handle conversion completion"""
        # Re-enable UI
        self.setEnabled(True)
        
        if success:
            # Show success message with option to open the file
            QMessageBox.information(self, "Conversion Complete", message)
            self.status_bar.showMessage("Conversion completed successfully", 5000)
        else:
            # Show error message
            QMessageBox.critical(self, "Conversion Error", message)
            self.status_bar.showMessage("Conversion failed", 5000)
        
        # Hide progress bar after a delay
        QTimer.singleShot(3000, lambda: self.progress_bar.setVisible(False))
    
    def new_document(self):
        """Create a new document"""
        if self.editor.toPlainText().strip():
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        self.editor.clear()
        self.title_input.clear()
        self.author_input.clear()
        self.date_input.setText(datetime.now().strftime("%Y-%m-%d"))
        self.save_path = ""
        self.setWindowTitle("MD to HWP Converter")
        self.status_bar.showMessage("New document created", 3000)
    
    def open_document(self):
        """Open an existing markdown document"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            os.path.expanduser("~/Documents"),
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Set the content to the editor
                self.editor.setPlainText(content)
                
                # Try to extract metadata from YAML frontmatter
                frontmatter = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if frontmatter:
                    yaml_text = frontmatter.group(1)
                    
                    # Extract title
                    title_match = re.search(r"title:\s*(.*)", yaml_text)
                    if title_match:
                        self.title_input.setText(title_match.group(1).strip())
                    else:
                        # Use filename as title if no title in frontmatter
                        base_name = os.path.basename(file_name)
                        title = os.path.splitext(base_name)[0]
                        self.title_input.setText(title)
                    
                    # Extract author
                    author_match = re.search(r"author:\s*(.*)", yaml_text)
                    if author_match:
                        self.author_input.setText(author_match.group(1).strip())
                    
                    # Extract date
                    date_match = re.search(r"date:\s*(.*)", yaml_text)
                    if date_match:
                        self.date_input.setText(date_match.group(1).strip())
                else:
                    # No frontmatter, use filename as title
                    base_name = os.path.basename(file_name)
                    title = os.path.splitext(base_name)[0]
                    self.title_input.setText(title)
                
                # Update window title
                self.setWindowTitle(f"MD to HWP Converter - {os.path.basename(file_name)}")
                self.status_bar.showMessage(f"Opened: {file_name}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not open file: {str(e)}")
    
    def save_markdown(self):
        """Save the current document as a markdown file"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            os.path.expanduser("~/Documents"),
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if file_name:
            # Ensure .md extension
            if not file_name.lower().endswith('.md'):
                file_name += '.md'
            
            try:
                # Create frontmatter
                title = self.title_input.text().strip() or "Untitled Document"
                author = self.author_input.text().strip() or "Unknown Author"
                date = self.date_input.text().strip() or datetime.now().strftime("%Y-%m-%d")
                
                frontmatter = f"---\ntitle: {title}\nauthor: {author}\ndate: {date}\n---\n\n"
                
                # Get content
                content = self.editor.toPlainText()
                
                # Remove existing frontmatter if present
                content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
                
                # Write to file
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(frontmatter + content)
                
                # Update window title
                self.setWindowTitle(f"MD to HWP Converter - {os.path.basename(file_name)}")
                self.status_bar.showMessage(f"Saved to: {file_name}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "Error Saving File", f"Could not save file: {str(e)}")
    
    def change_theme(self, index):
        """Change the application theme (light/dark)"""
        if index == 0:  # Light theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QLabel {
                    font-weight: normal;
                    color: #424242;
                }
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: white;
                    color: #212121;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                }
                QProgressBar {
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    background-color: #F5F5F5;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 3px;
                }
                QStatusBar {
                    background-color: #EEEEEE;
                    color: #424242;
                }
                QFrame#separator {
                    background-color: #E0E0E0;
                }
            """)
            
            # Update editor and preview styles
            self.editor.setStyleSheet("""
                QTextEdit {
                    border: none;
                    padding: 10px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    line-height: 1.5;
                    background-color: white;
                    color: #212121;
                }
            """)
            
            self.preview.setStyleSheet("""
                QTextEdit {
                    background-color: #f8f9fa;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    color: #333;
                }
            """)
            
        else:  # Dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #263238;
                }
                QLabel {
                    font-weight: normal;
                    color: #ECEFF1;
                }
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #455A64;
                    border-radius: 4px;
                    background-color: #37474F;
                    color: #ECEFF1;
                }
                QPushButton {
                    background-color: #00BCD4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00ACC1;
                }
                QPushButton:pressed {
                    background-color: #0097A7;
                }
                                QPushButton:disabled {
                    background-color: #546E7A;
                }
                QProgressBar {
                    border: 1px solid #455A64;
                    border-radius: 4px;
                    background-color: #37474F;
                    text-align: center;
                    color: #ECEFF1;
                }
                QProgressBar::chunk {
                    background-color: #00BCD4;
                    border-radius: 3px;
                }
                QStatusBar {
                    background-color: #1C2529;
                    color: #B0BEC5;
                }
                QFrame#separator {
                    background-color: #455A64;
                }
                QComboBox {
                    background-color: #37474F;
                    color: #ECEFF1;
                    border: 1px solid #455A64;
                    border-radius: 4px;
                    padding: 4px 8px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #37474F;
                    color: #ECEFF1;
                    selection-background-color: #00BCD4;
                }
            """)
            
            # Update editor and preview styles
            self.editor.setStyleSheet("""
                QTextEdit {
                    border: none;
                    padding: 10px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    line-height: 1.5;
                    background-color: #37474F;
                    color: #ECEFF1;
                }
            """)
            
            self.preview.setStyleSheet("""
                QTextEdit {
                    background-color: #263238;
                    border: 1px solid #455A64;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    color: #ECEFF1;
                }
            """)
            
            # Update the convert button in dark theme
            self.convert_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #43A047;
                }
                QPushButton:pressed {
                    background-color: #388E3C;
                }
                QPushButton:disabled {
                    background-color: #546E7A;
                }
            """)
    
    def closeEvent(self, event):
        """Handle application close event"""
        if self.editor.toPlainText().strip():
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Do you want to exit anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept()


# Utility functions for HTML to HWPML conversion
field_id_counter = 0

def convert_html_to_hwpml(soup):
    """Convert BeautifulSoup HTML to HWPML format"""
    hwpml_content = ""
    
    for element in soup.children:
        if isinstance(element, NavigableString):
            continue
        hwpml_content += convert_element_to_hwpml(element)
    
    return hwpml_content

def convert_element_to_hwpml(element):
    """Convert a single HTML element to HWPML"""
    if element.name == 'h1':
        return f'<P ParaShape="0" Style="0"><TEXT CharShape="1"><CHAR>{element.text}</CHAR></TEXT></P>\n'
    elif element.name == 'h2':
        return f'<P ParaShape="0" Style="0"><TEXT CharShape="2"><CHAR>{element.text}</CHAR></TEXT></P>\n'
    elif element.name == 'h3':
        return f'<P ParaShape="0" Style="0"><TEXT CharShape="3"><CHAR>{element.text}</CHAR></TEXT></P>\n'
    elif element.name == 'h4':
        return f'<P ParaShape="0" Style="0"><TEXT CharShape="4"><CHAR>{element.text}</CHAR></TEXT></P>\n'
    elif element.name == 'p':
        return convert_paragraph_to_hwpml(element)
    elif element.name in ['ul', 'ol']:
        return convert_list_to_hwpml(element, depth=0)
    elif element.name == 'pre':
        return convert_code_block_to_hwpml(element)
    elif element.name == 'table':

        return '<P ParaShape="0" Style="0"><TEXT CharShape="0">' + convert_table_to_hwpml(element) + '<CHAR/></TEXT></P>'
=======
       
    elif element.name == 'blockquote':
        return convert_blockquote_to_hwpml(element)
    
    return ""

def convert_paragraph_to_hwpml(p):
    """Convert HTML paragraph to HWPML"""
    hwpml = '<P ParaShape="0" Style="0">'
    has_content = False
    
    for child in p.children:
        if isinstance(child, NavigableString):
            text = str(child)
            if text:
                hwpml += f'<TEXT CharShape="0"><CHAR>{escape_xml(text)}</CHAR></TEXT>'
                has_content = True
        elif child.name == 'a':
            hwpml += convert_a_to_hwpml(child)
            has_content = True
        elif child.name in ['b', 'strong']:
            hwpml += f'<TEXT CharShape="6"><CHAR>{escape_xml(child.text)}</CHAR></TEXT>'
            has_content = True
        elif child.name in ['i', 'em']:
            hwpml += f'<TEXT CharShape="7"><CHAR>{escape_xml(child.text)}</CHAR></TEXT>'

            has_content = True
        elif child.name == 'code':
            hwpml += f'<TEXT CharShape="0"><CHAR>{escape_xml(child.text)}</CHAR></TEXT>'
            has_content = True
=======
            has_content = True
        elif child.name == 'code':
            hwpml += f'<TEXT CharShape="0"><CHAR>{escape_xml(child.text)}</CHAR></TEXT>'
            has_content = True

    
    if not has_content:
        hwpml += '<TEXT CharShape="0"/>'
    
    hwpml += '</P>\n'
    return hwpml

def convert_a_to_hwpml(a):
    """Convert HTML anchor to HWPML hyperlink"""
    global field_id_counter
    field_id_counter += 1
    field_id = field_id_counter
    inst_id = field_id_counter + 1000000
    
    url = a.get('href', '').replace('/', '\\/')
    text = a.text
    
    command = f"{url};1;0;0;"
    
    field_begin = (
        f'<TEXT CharShape="0">'
        f'<FIELDBEGIN Command="{command}" Dirty="true" Editable="false" '
        f'FieldId="{field_id}" InstId="{inst_id}" Property="0" Type="Hyperlink"/>'
        f'</TEXT>'
    )
    
    link_text = f'<TEXT CharShape="8"><CHAR>{escape_xml(text)}</CHAR></TEXT>'
    
    field_end = (
        f'<TEXT CharShape="0">'
        f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
        f'<CHAR/>'
        f'</TEXT>'
    )
    
    return field_begin + link_text + field_end

def convert_list_to_hwpml(list_tag, depth=0):
    """Convert HTML list to HWPML"""
    hwpml = ""
    is_ordered = (list_tag.name == 'ol')
    item_counter = 1
    
    for li in list_tag.find_all('li', recursive=False):
        hwpml += convert_list_item_to_hwpml(li, depth, is_ordered, item_counter)
        if is_ordered:
            item_counter += 1
        
        # Process nested lists separately
        for child_list in li.find_all(['ul', 'ol'], recursive=False):
            hwpml += convert_list_to_hwpml(child_list, depth + 1)
    
    return hwpml

def convert_list_item_to_hwpml(li, depth, is_ordered, item_number):
    """Convert HTML list item to HWPML"""
    para_shape_id = min(depth + 1, 6)
    hwpml = f'<P ParaShape="{para_shape_id}" Style="0">'
    
    if is_ordered:
        bullet_text = f"{item_number}. "
    else:
        bullet_text = "• "
    
    hwpml += f'<TEXT CharShape="0"><CHAR>{bullet_text}</CHAR></TEXT>'
    
    for child in li.children:
        if isinstance(child, NavigableString):
            text = child.strip()
            if text:
                hwpml += f'<TEXT CharShape="0"><CHAR>{escape_xml(text)}</CHAR></TEXT>'
        elif child.name == 'a':
            hwpml += convert_a_to_hwpml(child)
        elif child.name in ['b', 'strong']:
            hwpml += f'<TEXT CharShape="6"><CHAR>{escape_xml(child.get_text())}</CHAR></TEXT>'
        elif child.name in ['i', 'em']:
            hwpml += f'<TEXT CharShape="7"><CHAR>{escape_xml(child.get_text())}</CHAR></TEXT>'
        elif child.name in ['ul', 'ol']:
            # Skip nested lists as they're processed separately
            pass
        elif child.name == 'code':
            hwpml += f'<TEXT CharShape="0"><CHAR>{escape_xml(child.text)}</CHAR></TEXT>'
        else:
            # Try to get text for other elements
            text = child.get_text().strip()
            if text:
                hwpml += f'<TEXT CharShape="0"><CHAR>{escape_xml(text)}</CHAR></TEXT>'
    
    hwpml += '</P>\n'
    return hwpml

def convert_code_block_to_hwpml(pre):
    """Convert HTML code block to HWPML"""
    code_text = pre.get_text()
    
    # Split into lines and create a paragraph for each line
    hwpml = ""
    for line in code_text.splitlines():
        if not line.strip():
            # Empty line
            hwpml += '<P ParaShape="0" Style="0"><TEXT CharShape="0"/></P>\n'
        else:
            # Code line with monospace styling
            hwpml += f'<P ParaShape="0" Style="0"><TEXT CharShape="0"><CHAR>{escape_xml(line)}</CHAR></TEXT></P>\n'
    
    return hwpml

def convert_table_to_hwpml(table):

    # Find all rows in the HTML table
    rows = table.find_all('tr')
    row_count = len(rows)

    # Determine column count
    col_count = max(len(row.find_all(['td', 'th'])) for row in rows) if rows else 0

    # Total width of the table (adjust this if needed)
    total_table_width = 41950  # Total width of the table
    cell_width = total_table_width // col_count if col_count > 0 else 20975  # Adjust cell width dynamically

    # Build table structure
    hwpml = f"""
<TABLE BorderFill="3" CellSpacing="0" ColCount="{col_count}" PageBreak="Cell" RepeatHeader="false" RowCount="{row_count}">
    <SHAPEOBJECT InstId="1797201703" Lock="false" NumberingType="Table" TextWrap="TopAndBottom" ZOrder="1">
        <SIZE Height="2560" HeightRelTo="Absolute" Protect="false" Width="{total_table_width}" WidthRelTo="Absolute"/>
        <POSITION AffectLSpacing="false" AllowOverlap="false" FlowWithText="true" HoldAnchorAndSO="false" HorzAlign="Left" HorzOffset="0" HorzRelTo="Para" TreatAsChar="false" VertAlign="Top" VertOffset="0" VertRelTo="Para"/>
        <OUTSIDEMARGIN Bottom="285" Left="285" Right="285" Top="285"/>
    </SHAPEOBJECT>
    <INSIDEMARGIN Bottom="140" Left="510" Right="510" Top="140"/>"""

    # Process rows and cells
    for row_index, row in enumerate(rows):
        hwpml += f"\n    <ROW>"
        cells = row.find_all(['td', 'th'])
        
        # Fill in missing cells if any
        while len(cells) < col_count:
            cells.append(None)
            
        for cell_index in range(col_count):
            cell = cells[cell_index] if cell_index < len(cells) else None
            cell_text = cell.text.strip() if cell else "&#160;"  # Non-breaking space for empty cells
            
            hwpml += f"""
        <CELL BorderFill="5" ColAddr="{cell_index}" ColSpan="1" Dirty="false" Editable="false" HasMargin="false" Header="false" Height="500" Protect="false" RowAddr="{row_index}" RowSpan="1" Width="{cell_width}">
            <CELLMARGIN Bottom="0" Left="0" Right="0" Top="0"/>
            <PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center">
                <P ParaShape="0" Style="0">
                    <TEXT CharShape="0">
                        <CHAR>{cell_text}</CHAR>
                    </TEXT>
                </P>
            </PARALIST>
        </CELL>"""
        hwpml += f"\n    </ROW>"
    
    hwpml += "\n</TABLE>"

    return hwpml


def convert_blockquote_to_hwpml(blockquote):
    """Convert HTML blockquote to HWPML"""
    hwpml = ""
    
    # Process each paragraph in the blockquote
    for p in blockquote.find_all('p'):
        text = p.get_text().strip()
        if text:
            hwpml += f'<P ParaShape="0" Style="0"><TEXT CharShape="7"><CHAR>> {escape_xml(text)}</CHAR></TEXT></P>\n'
    
    # If there are no paragraphs, process the text directly
    if not hwpml:
        text = blockquote.get_text().strip()
        if text:
            hwpml += f'<P ParaShape="0" Style="0"><TEXT CharShape="7"><CHAR>> {escape_xml(text)}</CHAR></TEXT></P>\n'
    
    return hwpml

def escape_xml(text):
    """Escape special characters for XML"""
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&apos;')
    )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())