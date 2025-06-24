from PIL import Image, ImageOps # ImageOps 모듈 추가
import os
import numpy as np

def crop_with_margin(image_path, output_path, margin=20, whitespace_threshold=250):
    """
    이미지에서 흰색 빈 공간을 제거하고 내용 주위로 마진을 추가하여 자릅니다.
    가로 너비는 원본 이미지와 동일하게 유지하고, 세로 방향으로만 크롭핑합니다.

    Args:
        image_path (str): 입력 이미지 파일 경로.
        output_path (str): 잘라낸 이미지를 저장할 경로.
        margin (int): 내용 영역 주위에 추가할 마진 크기 (픽셀 단위).
        whitespace_threshold (int): 픽셀을 흰색으로 간주하는 임계값 (0-255).
                                    이 값보다 R, G, B 값이 모두 높으면 흰색으로 간주.
    """
    try:
        img = Image.open(image_path)

        # 1. EXIF 방향 정보에 따라 이미지를 자동으로 올바르게 회전
        # 이 부분이 핵심입니다. JPG 파일의 회전 정보를 처리합니다.
        img = ImageOps.exif_transpose(img) 

         # 2. 이미지의 가로/세로 비율을 기준으로 추가 회전이 필요한지 확인
        # '한글-템플릿_paragraph_001001.jpg'의 경우, 시각적인 가로는 2480, 세로는 3508 (세로가 더 김)
        # 만약 img.size가 (3508, 2480)으로 되어 있다면, 90도 회전이 필요함
        if img.width > img.height: # 가로가 세로보다 길다면 (대부분 문서 이미지는 세로가 김)
            # 그리고 이 이미지가 원래 세로 방향 이미지였다면, 90도 회전 필요
            # 이 로직은 이미지의 '원래' 방향을 가정합니다.
            # 예를 들어, 한글 문서는 보통 세로로 긴 형태 (Portrait)
            # 만약 img.width가 img.height보다 크다면 (Landscape), 90도 회전하여 Portrait로 만듦
            print(f"이미지가 가로 방향으로 로드되었습니다. 90도 회전합니다. 원본 크기: {img.size}")
            img = img.rotate(270, expand=True) # 270도 (시계 반대방향 90도) 회전. expand=True로 이미지 크기 자동 조절
            # 또는 img = img.transpose(Image.Transpose.ROTATE_270) # 더 빠를 수 있음

        # 여기서 img.size가 (2480, 3508)이 되도록 확인해야 합니다.
        print(f"처리 전 최종 이미지 크기: {img.size}")

        if img.mode != 'RGB':
            img = img.convert('RGB')

        pixels = np.array(img)
        height, width, _ = pixels.shape # 이 시점의 width는 2480, height는 3508이어야 함

        print(f"가로: {width}  세로: {height} image.size[0]: {img.size[0]}")

        is_pixel_white = np.all(pixels >= whitespace_threshold, axis=2) 
        is_row_all_white = np.all(is_pixel_white, axis=1)
        is_row_content = ~is_row_all_white 

        content_rows = np.where(is_row_content)[0]

        if content_rows.size == 0:
            print("이미지에서 내용이 발견되지 않았습니다. 원본 이미지를 저장합니다.")
            crop_upper = 0
            crop_lower = height
        else:
            min_y = content_rows.min()
            max_y = content_rows.max()

            crop_upper = max(0, min_y - margin)
            crop_lower = min(height, max_y + margin + 1)

            if crop_upper >= crop_lower:
                print("마진 적용 후 유효한 크롭 영역이 없습니다. 원본 이미지를 저장합니다.")
                crop_upper = 0
                crop_lower = height

        crop_box = (0, crop_upper, width, crop_lower)
        cropped_img = img.crop(crop_box)
        cropped_img.save(output_path)
        print(f"이미지 자르기 완료 및 {output_path}에 저장되었습니다. 마진: {margin}픽셀")
        print(f"결과 이미지 크기: {cropped_img.size[0]}px (가로) x {cropped_img.size[1]}px (세로)")

    except FileNotFoundError:
        print(f"오류: 이미지 파일을 찾을 수 없습니다 - {image_path}")
    except Exception as e:
        print(f"처리 중 오류가 발생했습니다: {e}")

def process_all_images(input_dir, output_dir):
    """
    images 폴더의 모든 JPG 파일을 크롭하여 Cropped_Images 폴더에 저장합니다.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"출력 디렉토리 생성: {output_dir}")

    jpg_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.jpg')]
    
    if not jpg_files:
        print(f"'{input_dir}' 폴더에 JPG 파일이 없습니다.")
        return

    print(f"총 {len(jpg_files)}개의 JPG 파일을 처리합니다.")

    for jpg_file in jpg_files:
        input_path = os.path.join(input_dir, jpg_file)
        output_path = os.path.join(output_dir, jpg_file)
        
        print(f"\n처리 시작: {jpg_file}")
        crop_with_margin(input_path, output_path)

if __name__ == "__main__":
    input_dir = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\images'
    output_dir = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\Cropped_Images' 
    process_all_images(input_dir, output_dir)
