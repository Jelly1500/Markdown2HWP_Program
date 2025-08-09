import os
from md2hwp.utils import GetHmlTags, hwp2jpg, cropping_image
from md2hwp.utils.logger import log_info, log_debug, log_error

def create_template_images(template_path, split_hml_dir, image_dir, cropped_image_dir):

    # 1. 템플릿 파일 경로 확인
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
    
    # 2. 템플릿 파일 내용 확인
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    log_info(f"[PRE] 원본 HML 경로: {template_path}")
    log_debug(f"[PRE] 출력 폴더(split): {split_hml_dir}, (images): {image_dir}, (cropped): {cropped_image_dir}")

    # 3. 템플릿 파일 내용 추출 (문단 단위 분리)
    log_info("[STEP 1] HML 분할 시작 (SECDEF/COLDEF 적용)")
    GetHmlTags.split_hml_and_apply_defs(template_path, split_hml_dir)
    # 검증: 분할된 HML이 존재하는지 확인
    try:
        split_files = [f for f in os.listdir(split_hml_dir) if f.lower().endswith('.hml')]
    except FileNotFoundError:
        split_files = []
    log_info(f"[STEP 1] 분할 결과 파일 수: {len(split_files)}")
    if not split_files:
        raise RuntimeError("HML 분할 결과가 없습니다. 원본 문서의 SECDEF/COLDEF 누락 또는 <CHAR>가 포함된 문단이 없을 수 있습니다.")

    # 4. 이미지 생성 (JPG)
    log_info("[STEP 2] HML→JPG 변환 시작")
    hwp2jpg.convert_all_hmls_to_jpg(split_hml_dir, image_dir)
    # 검증: 생성된 JPG 여부 확인
    try:
        jpg_files = [f for f in os.listdir(image_dir) if f.lower().endswith('.jpg')]
    except FileNotFoundError:
        jpg_files = []
    log_info(f"[STEP 2] JPG 생성 파일 수: {len(jpg_files)}")
    if not jpg_files:
        raise RuntimeError("HML→JPG 변환 실패. 한/글 자동화 설정(보안 모듈 해제), 파일명/경로 길이, 또는 HWP 버전을 확인하세요.")

    # 5. 이미지 크롭
    log_info("[STEP 3] 이미지 크롭 시작")
    cropping_image.process_all_images(image_dir, cropped_image_dir)
    log_info("[DONE] 전처리 완료")
    
if __name__ == "__main__":
    template_path = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\한글-템플릿 (1).hml'
    create_template_images(template_path)
    
    
    









