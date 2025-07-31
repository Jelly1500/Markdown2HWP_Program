"""
HWPML 표 생성 전담 모듈
"""
from md2hwp.config import MAX_TABLE_WIDTH, DEFAULT_CELL_WIDTH

class TableGenerator:
    """HWPML 표 생성 전담 클래스"""
    
    def __init__(self, template_manager, id_manager):
        self.template_manager = template_manager
        self.id_manager = id_manager
    
    def _get_border_fill_id(self, row_idx, col_idx, row_count, col_count):
        """셀 위치에 따라 적절한 테두리 스타일 ID를 반환"""
        # 첫 번째 행
        if row_idx == 0:
            if col_idx == 0:  # 첫 번째 행 가장 왼쪽
                return self.template_manager.table_border_fills['first_row_left']
            elif col_idx == col_count - 1:  # 첫 번째 행 가장 오른쪽
                return self.template_manager.table_border_fills['first_row_right']
            else:  # 첫 번째 행 가운데
                return self.template_manager.table_border_fills['first_row_center']
        
        # 두 번째 행
        elif row_idx == 1:
            if col_idx == 0:  # 두 번째 행 가장 왼쪽
                return self.template_manager.table_border_fills['second_row_left']
            elif col_idx == col_count - 1:  # 두 번째 행 가장 오른쪽
                return self.template_manager.table_border_fills['second_row_right']
            else:  # 두 번째 행 가운데
                return self.template_manager.table_border_fills['second_row_center']
        
        # 마지막 행
        elif row_idx == row_count - 1:
            if col_idx == 0:  # 마지막 행 가장 왼쪽
                return self.template_manager.table_border_fills['last_row_left']
            elif col_idx == col_count - 1:  # 마지막 행 가장 오른쪽
                return self.template_manager.table_border_fills['last_row_right']
            else:  # 마지막 행 가운데
                return self.template_manager.table_border_fills['last_row_center']
        
        # 중간 행들
        else:
            if col_idx == 0:  # 중간 행 가장 왼쪽
                return self.template_manager.table_border_fills['middle_row_left']
            elif col_idx == col_count - 1:  # 중간 행 가장 오른쪽
                return self.template_manager.table_border_fills['middle_row_right']
            else:  # 중간 행 가운데
                return self.template_manager.table_border_fills['middle_row_center']
    
    def create_table(self, table_data):
        """표 데이터로부터 HWPML 표 생성"""
        rows = table_data['rows']
        row_count = len(rows)
        col_count = max(len(row) for row in rows) if rows else 0

        total_table_width = MAX_TABLE_WIDTH
        cell_width = total_table_width // col_count if col_count > 0 else DEFAULT_CELL_WIDTH

        inst_id = self.id_manager.next_inst_id()

        # 표 시작 태그 생성 (기본 테두리 스타일 사용)
        default_border_fill = self.template_manager.table_border_fills['first_row_left']
        hwpml = f"""<P ParaShape="0" Style="0"><TEXT CharShape="0"> <TABLE BorderFill="{default_border_fill}" CellSpacing="0" ColCount="{col_count}" PageBreak="Cell" RepeatHeader="true" RowCount="{row_count}"> <SHAPEOBJECT InstId="{inst_id}" Lock="false" NumberingType="Table" TextWrap="TopAndBottom" ZOrder="1"> <SIZE Height="3846" HeightRelTo="Absolute" Protect="false" Width="{total_table_width}" WidthRelTo="Absolute"/> <POSITION AffectLSpacing="false" AllowOverlap="false" FlowWithText="true" HoldAnchorAndSO="false" HorzAlign="Left" HorzOffset="0" HorzRelTo="Column" TreatAsChar="false" VertAlign="Top" VertOffset="0" VertRelTo="Para"/> <OUTSIDEMARGIN Bottom="283" Left="283" Right="283" Top="283"/> </SHAPEOBJECT> <INSIDEMARGIN Bottom="141" Left="510" Right="510" Top="141"/>"""

        # 행 생성
        for row_idx, row in enumerate(rows):
            hwpml += f"\n<ROW>"

            # 셀 생성
            for cell_idx, cell in enumerate(row):
                # 셀 위치에 따라 적절한 테두리 스타일 결정
                border_fill_id = self._get_border_fill_id(row_idx, cell_idx, row_count, col_count)
                
                hwpml += f""" <CELL BorderFill="{border_fill_id}" ColAddr="{cell_idx}" ColSpan="1" Dirty="false" Editable="false" HasMargin="false" Header="{str(cell.get('is_header', False)).lower()}" Height="282" Protect="false" RowAddr="{row_idx}" RowSpan="1" Width="{cell_width}"> <CELLMARGIN Bottom="141" Left="510" Right="510" Top="141"/> <PARALIST LineWrap="Break" LinkListID="0" LinkListIDNext="0" TextDirection="0" VertAlign="Center"> <P ParaShape="0" Style="0"> <TEXT CharShape="0"><CHAR>{cell['content']}</CHAR></TEXT> </P> </PARALIST> </CELL>"""

            hwpml += f"\n</ROW>"

        # 표 종료 태그 추가
        hwpml += "\n</TABLE><CHAR/></TEXT></P>"

        return hwpml 