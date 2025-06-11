import os
from md2hwp.utils import GetHmlTags, hwp2jpg, cropping_image

def create_template_images(template_path, split_hml_dir, image_dir, cropped_image_dir):

    # 1. 템플릿 파일 경로 확인
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
    
    # 2. 템플릿 파일 내용 확인
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # 3. 템플릿 파일 내용 추출
    GetHmlTags.split_hml_and_apply_defs(template_path, split_hml_dir)

    # 4. 이미지 생성
    hwp2jpg.convert_all_hmls_to_jpg(split_hml_dir, image_dir)

    # 5. 이미지 크롭
    cropping_image.process_all_images(image_dir, cropped_image_dir)
    
if __name__ == "__main__":
    template_path = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\한글-템플릿 (1).hml'
    create_template_images(template_path)
    
    
    









