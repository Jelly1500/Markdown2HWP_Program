# md_to_hwp/hwpml_templates.py
"""
HWPML 문서 템플릿 및 상수를 정의하는 모듈
"""

# 기본 텍스트 종료 태그
TXT_END = '</CHAR></TEXT></P>'

# HWPML 문서 헤더
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
<LAYOUTCOMPATIBILITY AdjustBaselineInFixedLinespacing="false" AdjustBaselineOfObjectToBottom="false" AdjustLineheightToFont="false" AdjustMarginFromAdjustLineheight="false" AdjustParaBorderOffsetWithBorder="false" AdjustParaBorderfillToSpacing="false" AdjustVertPosOfLine="false" ApplyAtLeastToPercent100Pct="false" ApplyCharSpacingToCharGrid="false" ApplyExtendHeaderFooterEachSection="false" ApplyFontWeightToBold="false" ApplyFontspaceToLatin="false" ApplyMinColumnWidthTo1mm="false" ApplyNextspacingOfLastPara="false" ApplyParaBorderToOutside="false" ApplyPrevspacingBeneathObject="false" ApplyTabPosBasedOnSegment="false" BaseCharUnitOfIndentOnFirstChar="false" BaseCharUnitOnEAsian="false" BaseLinespacingOnLinegrid="false" BreakTabOverLine="false" ConnectParaBorderfillOfEqualBorder="false" DoNotAdjustEmptyAnchorLine="false" DoNotAdjustWordInJustify="false"
DoNotAlignLastForbidden="false" DoNotAlignLastPeriod="false" DoNotAlignWhitespaceOnRight="false" DoNotApplyAutoSpaceEAsianEng="false" DoNotApplyAutoSpaceEAsianNum="false" DoNotApplyColSeparatorAtNoGap="false" DoNotApplyExtensionCharCompose="false" DoNotApplyGridInHeaderFooter="false" DoNotApplyHeaderFooterAtNoSpace="false" DoNotApplyImageEffect="false" DoNotApplyLinegridAtNoLinespacing="false" DoNotApplyShapeComment="false" DoNotApplyStrikeoutWithUnderline="false" DoNotApplyVertOffsetOfForward="false" DoNotApplyWhiteSpaceHeight="false" DoNotFormattingAtBeneathAnchor="false" DoNotHoldAnchorOfTable="false" ExtendLineheightToOffset="false" ExtendLineheightToParaBorderOffset="false" ExtendVertLimitToPageMargins="false" FixedUnderlineWidth="false" OverlapBothAllowOverlap="false" TreatQuotationAsLatin="false" UseInnerUnderline="false" UseLowercaseStrikeout="false" />
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

# 문서 푸터
FOOTER = """</SECTION></BODY><TAIL></TAIL></HWPML>"""

# 문서 인트로 (제목, 작성자, 날짜)
INTRO = """
<P ParaShape="7" Style="0"><TEXT CharShape="5"><CHAR>___TITLE___</CHAR></TEXT></P>
<P ParaShape="8" Style="0"><TEXT CharShape="0"><CHAR>작성자 : ___AUTHOR___</CHAR></TEXT></P>
<P ParaShape="8" Style="0"><TEXT CharShape="0"><CHAR>작성일 : ___DATE___</CHAR></TEXT></P>
"""

# H1~H4 헤더 시작 태그
H1_START = '<P ParaShape="0" Style="0"><TEXT CharShape="1"><CHAR>'
H2_START = '<P ParaShape="0" Style="0"><TEXT CharShape="2"><CHAR>'
H3_START = '<P ParaShape="0" Style="0"><TEXT CharShape="3"><CHAR>'
H4_START = '<P ParaShape="0" Style="0"><TEXT CharShape="4"><CHAR>'

# 복잡한 서식을 위한 템플릿 (예: 테이블 형태의 제목)
H2_TABLE_TEMPLATE = """
<P ParaShape="0" Style="0"><TEXT CharShape="0">
<TABLE BorderFill="3" CellSpacing="0" ColCount="3" PageBreak="Table" RepeatHeader="true" RowCount="1">
<SHAPEOBJECT InstId="1797444603" Lock="false" NumberingType="Table" ZOrder="0">
<SIZE Height="1933" HeightRelTo="Absolute" Protect="false" Width="11113" WidthRelTo="Absolute"/>
<POSITION AffectLSpacing="false" AllowOverlap="false" FlowWithText="false" HoldAnchorAndSO="false" HorzAlign="Left" HorzOffset="0" HorzRelTo="Para" TreatAsChar="true" VertAlign="Top" VertOffset="0" VertRelTo="Para"/>
<OUTSIDEMARGIN Bottom="283" Left="142" Right="142" Top="283"/>
</SHAPEOBJECT>
<INSIDEMARGIN Bottom="0" Left="0" Right="0" Top="0"/>
<ROW>
<CELL BorderFill="4" ColAddr="0" ColSpan="1" Dirty="false" Editable="false" HasMargin="true" Header="false" Height="1933" Protect="false" RowAddr="0" RowSpan="1" Width="717">
<CELLMARGIN Bottom="142" Left="142" Right="142" Top="142"/>
<PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center">
<P ParaShape="4" Style="0"><TEXT CharShape="1"/></P>
</PARALIST>
</CELL>
<CELL BorderFill="5" ColAddr="1" ColSpan="1" Dirty="false" Editable="false" HasMargin="true" Header="false" Height="1933" Protect="false" RowAddr="0" RowSpan="1" Width="720">
<CELLMARGIN Bottom="142" Left="142" Right="142" Top="142"/>
<PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center">
<P ParaShape="1" Style="0"><TEXT CharShape="2"/></P>
</PARALIST>
</CELL>
<CELL BorderFill="6" ColAddr="2" ColSpan="1" Dirty="false" Editable="false" HasMargin="true" Header="false" Height="1933" Protect="false" RowAddr="0" RowSpan="1" Width="9676">
<CELLMARGIN Bottom="142" Left="142" Right="142" Top="142"/>
<PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center">
<P ParaShape="3" Style="1"><TEXT CharShape="4"><CHAR> </CHAR></TEXT><TEXT CharShape="5"><CHAR>{content}</CHAR></TEXT></P>
</PARALIST>
</CELL>
</ROW>
</TABLE>
<CHAR/></TEXT></P>
"""
