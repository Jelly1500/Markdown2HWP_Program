from PIL import Image
import os

def crop_with_margin(image_path, output_path, margin=20, whitespace_threshold=240):
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
        # 이미지를 엽니다.
        img = Image.open(image_path)

        # RGB 모드로 변환하여 일관성 확보 (알파 채널 등 처리)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        pixels = img.load()
        width, height = img.size

        # 내용 영역의 최소/최대 y좌표만 찾기 (x좌표는 이미지 전체 너비 사용)
        min_y = height
        max_y = -1

        # 각 행의 평균 픽셀값을 계산하여 내용이 있는 행 찾기
        for y in range(height):
            row_has_content = False
            for x in range(width):
                r, g, b = pixels[x, y]
                # 픽셀이 흰색 임계값보다 낮으면 내용으로 간주
                if r < whitespace_threshold or g < whitespace_threshold or b < whitespace_threshold:
                    row_has_content = True
                    break
            
            if row_has_content:
                min_y = min(min_y, y)
                max_y = max(max_y, y)

        # 내용이 전혀 발견되지 않은 경우 (이미지가 완전히 흰색인 경우 등)
        if max_y == -1:
            print("이미지에서 내용이 발견되지 않았습니다. 원본 이미지를 저장합니다.")
            crop_upper = 0
            crop_lower = height
        else:
            # 내용 영역 경계에 마진 적용 및 이미지 경계 처리
            crop_upper = max(0, min_y - margin)  # 위쪽 마진 적용, 0보다 작아지지 않게
            crop_lower = min(height, max_y + margin + 1)  # 아래쪽 마진 적용, 이미지 높이 넘어가지 않게 (+1 고려)

            # 마진을 적용한 후에도 유효한 영역인지 다시 확인 (극단적인 경우)
            if crop_upper >= crop_lower:
                print("마진 적용 후 유효한 크롭 영역이 없습니다. 원본 이미지를 저장합니다.")
                crop_upper = 0
                crop_lower = height

        # 자르기 박스 정의 (left, upper, right, lower)
        # 가로 방향은 이미지 전체 너비 사용
        crop_box = (0, crop_upper, width, crop_lower)

        # 이미지 자르기
        cropped_img = img.crop(crop_box)

        # 잘라낸 이미지 저장
        cropped_img.save(output_path)
        print(f"이미지 자르기 완료 및 {output_path}에 저장되었습니다. 마진: {margin}픽셀")

    except FileNotFoundError:
        print(f"오류: 이미지 파일을 찾을 수 없습니다 - {image_path}")
    except Exception as e:
        print(f"처리 중 오류가 발생했습니다: {e}")

def process_all_images(input_dir, output_dir):
    """
    images 폴더의 모든 JPG 파일을 크롭하여 Cropped_Images 폴더에 저장합니다.
    """

    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"출력 디렉토리 생성: {output_dir}")

    # JPG 파일 목록 가져오기
    jpg_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.jpg')]
    
    if not jpg_files:
        print(f"'{input_dir}' 폴더에 JPG 파일이 없습니다.")
        return

    print(f"총 {len(jpg_files)}개의 JPG 파일을 처리합니다.")

    # 각 JPG 파일을 크롭하여 저장
    for jpg_file in jpg_files:
        input_path = os.path.join(input_dir, jpg_file)
        output_path = os.path.join(output_dir, jpg_file)
        
        print(f"\n처리 시작: {jpg_file}")
        crop_with_margin(input_path, output_path)

if __name__ == "__main__":
    input_dir = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\images'
    process_all_images(input_dir)