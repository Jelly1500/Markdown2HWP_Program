import shutil
import os

def delete_folder_contents_permanently(folder_path):
    """
    폴더 경로를 입력받으면 해당 폴더는 남겨두고,
    그 안의 모든 하위 폴더와 파일들을 영구적으로 삭제합니다.

    Args:
        folder_path (str): 내용물을 삭제할 폴더의 전체 또는 상대 경로.

    Returns:
        bool: 내용물 삭제 성공 시 True, 실패 시 False를 반환합니다.
    """
    # **경고**: 이 함수는 지정된 폴더의 내용물을 휴지통을 거치지 않고 영구 삭제합니다.
    # 사용에 각별한 주의가 필요합니다.

    # 1. 대상 경로가 실제로 존재하는지 확인합니다.
    if not os.path.exists(folder_path):
        print(f"정보: 폴더 '{folder_path}'가(이) 존재하지 않습니다.")
        return False

    # 2. 경로가 폴더인지 확인합니다. 파일인 경우 작업을 수행할 수 없습니다.
    if not os.path.isdir(folder_path):
        print(f"오류: '{folder_path}'는 폴더가 아니라 파일입니다. 함수를 종료합니다.")
        return False

    print(f"폴더 '{folder_path}' 내부의 모든 내용 삭제를 시작합니다...")

    # 3. 폴더 내부의 모든 항목을 순회하며 삭제합니다.
    try:
        for item_name in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item_name)
            
            # 항목이 파일이거나 심볼릭 링크인 경우 os.remove()로 삭제
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            # 항목이 하위 폴더인 경우 shutil.rmtree()로 폴더 전체 삭제
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        
        print(f"성공: 폴더 '{folder_path}'의 모든 내용이 영구적으로 삭제되었습니다.")
        return True
        
    except PermissionError:
        print(f"오류: 권한 문제로 '{folder_path}' 또는 그 안의 파일을 삭제할 수 없습니다.")
        return False
    except OSError as e:
        # 다른 운영체제 수준의 오류 (예: 파일이 다른 프로세스에 의해 사용 중)
        print(f"오류: 내용물을 삭제하는 중 운영체제 오류가 발생했습니다: {e}")
        return False
    except Exception as e:
        # 기타 예상치 못한 모든 예외 처리
        print(f"오류: 알 수 없는 문제가 발생했습니다: {e}")
        return False

# --- 함수 사용 예시 ---
if __name__ == '__main__':
    # 테스트를 위한 안전한 임시 폴더 및 파일 생성
    TEST_DIR = "temp_folder_for_deletion"
    SUB_DIR = os.path.join(TEST_DIR, "subfolder")

    # 현재 스크립트의 위치를 기준으로 상대 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 디렉토리
    project_root = os.path.dirname(os.path.dirname(current_dir))  # 프로젝트 루트 디렉토리
    
    # split_hml_dir = os.path.join(project_root, 'output_split_hml')
    image_dir = os.path.join(project_root, 'images')
    cropped_image_dir = os.path.join(project_root, 'Cropped_Images')
    
    # delete_folder_contents_permanently(split_hml_dir)
    delete_folder_contents_permanently(image_dir)
    delete_folder_contents_permanently(cropped_image_dir)
    
    
    