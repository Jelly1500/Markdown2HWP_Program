"""
ID 관리 모듈: ID 카운터의 중앙 관리
ID = HWP(Hancom Word Processor) 문서 변환 과정에서 사용되는 고유 식별자(ID)
"""

class IDManager:
    """ID 값을 중앙에서 관리하는 클래스"""
    
    def __init__(self, start_inst_id=1000000, start_field_id=0):
        self.inst_id_counter = start_inst_id
        self.field_id_counter = start_field_id
    
    def next_inst_id(self):
        """다음 InstId 값을 가져오고 카운터 증가"""
        current = self.inst_id_counter
        self.inst_id_counter += 1
        return str(current)
    
    def next_field_id(self):
        """다음 FieldId 값을 가져오고 카운터 증가"""
        current = self.field_id_counter
        self.field_id_counter += 1
        return str(current) 