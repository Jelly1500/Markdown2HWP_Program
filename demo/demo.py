import sys
import re
import io
import markdown
import os
from bs4 import BeautifulSoup, NavigableString
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                               QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QStatusBar)
from PySide6.QtGui import QIcon

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
<BORDERFILLLIST Count="6">
<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="1" Shadow="false" Slash="0" ThreeD="false">
<LEFTBORDER Type="None" Width="0.1mm"/>
<RIGHTBORDER Type="None" Width="0.1mm"/>
<TOPBORDER Type="None" Width="0.1mm"/>
<BOTTOMBORDER Type="None" Width="0.1mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/>
</BORDERFILL>
<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="2" Shadow="false" Slash="0" ThreeD="false">
<LEFTBORDER Type="None" Width="0.1mm"/>
<RIGHTBORDER Type="None" Width="0.1mm"/>
<TOPBORDER Type="None" Width="0.1mm"/>
<BOTTOMBORDER Type="None" Width="0.1mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/>
<FILLBRUSH>
<WINDOWBRUSH Alpha="0" FaceColor="4294967295" HatchColor="10066329"/>
</FILLBRUSH>
</BORDERFILL>
<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="3" Shadow="false" Slash="0" ThreeD="false">
<LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.12mm"/>
<BOTTOMBORDER Type="Solid" Width="0.12mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/>
</BORDERFILL>
<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="4" Shadow="false" Slash="0" ThreeD="false">
<LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Dot" Width="0.3mm"/>
<BOTTOMBORDER Type="Solid" Width="0.12mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/>
</BORDERFILL>
<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="5" Shadow="false" Slash="0" ThreeD="false">
<LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Solid" Width="0.12mm"/>
<BOTTOMBORDER Type="Dot" Width="0.3mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/>
</BORDERFILL>
<BORDERFILL BackSlash="0" BreakCellSeparateLine="0" CenterLine="0" CounterBackSlash="0" CounterSlash="0" CrookedSlash="0" Id="6" Shadow="false" Slash="0" ThreeD="false">
<LEFTBORDER Type="Solid" Width="0.12mm"/>
<RIGHTBORDER Type="Solid" Width="0.12mm"/>
<TOPBORDER Type="Dot" Width="0.3mm"/>
<BOTTOMBORDER Type="Dot" Width="0.3mm"/>
<DIAGONAL Type="Solid" Width="0.1mm"/>
</BORDERFILL>
</BORDERFILLLIST>
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

# FieldId와 InstId를 위한 전역 카운터
field_id_counter = 0

def convert_html_to_hwpml(html):
    soup = BeautifulSoup(html, 'html.parser')
    hwpml_content = ""
    for element in soup.contents:
        if isinstance(element, NavigableString):
            text = element.strip()
            if text:
                hwpml_content += f'<P ParaShape="0" Style="0"><TEXT CharShape="0"><CHAR>{text}</CHAR></TEXT></P>\n'
        else:
            hwpml_content += convert_element_to_hwpml(element)
    return hwpml_content

def convert_element_to_hwpml(element):
    if element.name == 'h1':
        return f'{H1_START}{element.text}{TXT_END}\n'
    elif element.name == 'h2':
        return f'{H2_START}{element.text}{TXT_END}\n'
    elif element.name == 'h3':
        return f'{H3_START}{element.text}{TXT_END}\n'
    elif element.name == 'h4':
        return f'{H4_START}{element.text}{TXT_END}\n'
    elif element.name == 'p':
        return convert_paragraph_to_hwpml(element)
    elif element.name in ['ul', 'ol']:
        return convert_list_to_hwpml(element, depth=0)
    elif element.name == 'table':
        # For tables, add the proper paragraph structure around the table
        return '<P ParaShape="0" Style="0"><TEXT CharShape="0">' + convert_table_to_hwpml(element) + '<CHAR/></TEXT></P>'
    return ""


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
<TABLE BorderFill="3" CellSpacing="0" ColCount="{col_count}" PageBreak="Cell" RepeatHeader="true" RowCount="{row_count}">
<SHAPEOBJECT InstId="1797984080" Lock="false" NumberingType="Table" TextWrap="TopAndBottom" ZOrder="1">
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
            
            # 행 위치에 따라 테두리 스타일 결정
            if row_index == 0:
                border_fill_id = 3  # 첫번째 행: 상하단 모두 실선
            elif row_index == row_count - 1:
                border_fill_id = 4  # 마지막 행: 상단 점선, 하단 실선
            else:
                border_fill_id = 6  # 중간 행: 상하단 모두 점선
            
            hwpml += f"""
<CELL BorderFill="{border_fill_id}" ColAddr="{cell_index}" ColSpan="1" Dirty="false" Editable="false" HasMargin="false" Header="false" Height="282" Protect="false" RowAddr="{row_index}" RowSpan="1" Width="{cell_width}">
<CELLMARGIN Bottom="141" Left="510" Right="510" Top="141"/>
<PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center">
<P ParaShape="0" Style="0">"""
            
            # 셀 내용 추가 (마크다운 서식 지원)
            hwpml += convert_cell_content_to_hwpml(cell)
            
            hwpml += """
</P>
</PARALIST>
</CELL>"""
        
        hwpml += f"\n</ROW>"
    
    hwpml += "\n</TABLE>"
    return hwpml

def convert_cell_content_to_hwpml(cell):
    if cell is None:
        return '<TEXT CharShape="0"><CHAR>&#160;</CHAR></TEXT>'  # 빈 셀
    
    # 셀에서 직접 HTML 내용 추출 (text가 아닌 내부 태그 포함)
    hwpml = ''
    
    # 내용이 없으면 빈 태그 반환
    if len(list(cell.children)) == 0:
        content = cell.string if cell.string else "&#160;"
        return f'<TEXT CharShape="0"><CHAR>{content}</CHAR></TEXT>'
    
    # 내용 처리
    for child in cell.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                hwpml += f'<TEXT CharShape="0"><CHAR>{text}</CHAR></TEXT>'
        elif child.name == 'strong' or child.name == 'b':
            hwpml += f'<TEXT CharShape="6"><CHAR>{child.get_text()}</CHAR></TEXT>'
        elif child.name == 'em' or child.name == 'i':
            hwpml += f'<TEXT CharShape="7"><CHAR>{child.get_text()}</CHAR></TEXT>'
        elif child.name == 'a':
            hwpml += convert_a_to_hwpml(child)
    
    return hwpml if hwpml else '<TEXT CharShape="0"><CHAR>&#160;</CHAR></TEXT>'


def convert_paragraph_to_hwpml(p):
    hwpml = '<P ParaShape="0" Style="0">'
    has_content = False
    for child in p.children:
        if isinstance(child, NavigableString):
            text = child  
            if text:
                hwpml += f'<TEXT CharShape="0"><CHAR>{text}</CHAR></TEXT>'
                has_content = True
        elif child.name == 'a':
            hwpml += convert_a_to_hwpml(child)
            has_content = True
        elif child.name in ['b', 'strong']:
            hwpml += f'<TEXT CharShape="6"><CHAR>{child.text}</CHAR></TEXT>'
            has_content = True
        elif child.name in ['i', 'em']:
            hwpml += f'<TEXT CharShape="7"><CHAR>{child.text}</CHAR></TEXT>'
            has_content = True
    if not has_content:
        hwpml += '<TEXT CharShape="1"/>'
    hwpml += '</P>\n'
    return hwpml

def convert_a_to_hwpml(a):
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
    link_text = f'<TEXT CharShape="8"><CHAR>{text}</CHAR></TEXT>'
    field_end = (
        f'<TEXT CharShape="0">'
        f'<FIELDEND Editable="false" FieldId="{field_id}" Property="0" Type="Hyperlink"/>'
        f'<CHAR/>'
        f'</TEXT>'
    )
    return field_begin + link_text + field_end

def convert_list_to_hwpml(list_tag, depth=0):
    hwpml = ""
    is_ordered = (list_tag.name == 'ol')
    item_counter = 1
    for li in list_tag.find_all('li', recursive=False):
        hwpml += convert_list_item_to_hwpml(li, depth, is_ordered, item_counter)
        if is_ordered:
            item_counter += 1
        for child_list in li.find_all(['ul', 'ol'], recursive=False):
            hwpml += convert_list_to_hwpml(child_list, depth + 1)
    return hwpml

def convert_list_item_to_hwpml(li, depth, is_ordered, item_number):
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
                hwpml += f'<TEXT CharShape="0"><CHAR>{text}</CHAR></TEXT>'
        elif child.name == 'a':
            hwpml += convert_a_to_hwpml(child)
        elif child.name in ['b', 'strong']:
            hwpml += f'<TEXT CharShape="6"><CHAR>{child.get_text()}</CHAR></TEXT>'
        elif child.name in ['i', 'em']:
            hwpml += f'<TEXT CharShape="7"><CHAR>{child.get_text()}</CHAR></TEXT>'
        elif child.name in ['ul', 'ol']:
            pass
        else:
            hwpml += convert_element_to_hwpml(child)
    hwpml += '</P>\n'
    return hwpml

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MD to HWP Converter")
        self.setGeometry(100, 100, 600, 400)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("여기에 MD 텍스트를 붙여넣거나 클립보드에서 가져오세요")
        self.layout.addWidget(self.text_edit)
        self.button_layout = QHBoxLayout()
        self.clipboard_button = QPushButton("클립보드에서 가져오기")
        self.path_button = QPushButton("저장 경로 선택")
        self.convert_button = QPushButton("변환")
        self.button_layout.addWidget(self.clipboard_button)
        self.button_layout.addWidget(self.path_button)
        self.button_layout.addWidget(self.convert_button)
        self.layout.addLayout(self.button_layout)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비 완료")
        self.clipboard_button.clicked.connect(self.load_from_clipboard)
        self.path_button.clicked.connect(self.select_save_path)
        self.convert_button.clicked.connect(self.convert_md_to_hwp)
        self.save_path = ""

    def load_from_clipboard(self):
        clipboard = QApplication.clipboard()
        md_text = clipboard.text()
        if md_text:
            self.text_edit.setPlainText(md_text)
            self.status_bar.showMessage("클립보드에서 텍스트를 가져왔습니다")
        else:
            self.status_bar.showMessage("클립보드에 텍스트가 없습니다")

    def select_save_path(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "HWP 파일 저장", "", "HWP Files (*.hml)")
        if file_name:
            self.save_path = file_name
            self.status_bar.showMessage(f"저장 경로: {self.save_path}")
        else:
            self.status_bar.showMessage("저장 경로가 선택되지 않았습니다")

    def convert_md_to_hwp(self):
        if not self.save_path:
            self.status_bar.showMessage("오류: 저장 경로를 먼저 선택하세요")
            return
        md_text = self.text_edit.toPlainText()
        if not md_text:
            self.status_bar.showMessage("오류: 변환할 텍스트가 없습니다")
            return
        self.status_bar.showMessage("변환 중...")
        try:
            t = re.search("(?<=title: ).*", md_text)
            a = re.search("(?<=author: ).*", md_text)
            d = re.search("(?<=date: ).*", md_text)
            title = t.group(0) if t else "No Title"
            author = a.group(0) if a else "No Author"
            date = d.group(0) if d else "No Date"
            # YAML 블록(문서 맨 앞의 ---로 시작해서 ---로 끝나는 부분)만 제거
            md_text = re.sub(r'^---\n([\s\S]*?)\n---\n', '', md_text, flags=re.DOTALL)

            html = markdown.markdown(md_text, extensions=['fenced_code', 'tables'], tab_length=2)
           
            hwpml_content = convert_html_to_hwpml(html)
            hwpml = HEADER + INTRO + hwpml_content + FOOTER
            hwpml = hwpml.replace("___TITLE___", title)
            hwpml = hwpml.replace("___AUTHOR___", author)
            hwpml = hwpml.replace("___DATE___", date)
            with io.open(self.save_path, "w", encoding="utf-8") as f:
                f.write(hwpml)
            self.status_bar.showMessage(f"변환 완료: {self.save_path}")
        except Exception as e:
            self.status_bar.showMessage(f"오류: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
