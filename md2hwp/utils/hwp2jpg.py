import win32com.client
import os
import time

def convert_hwp_to_jpg(hwp, hwp_path: str, jpg_path: str):
    """
    [최종 개선] 파일을 열고 닫은 후, 각각의 작업이 완료될 때까지
    상태 표시줄을 확인하여 안정성을 확보합니다.
    """
    try:
        # 1. HWP 파일 열기
        hwp.Open(hwp_path, "HWPML2X", "")
        
        # 3. PrintToImage 액션을 사용해 JPG로 저장
        abs_jpg_path = os.path.abspath(jpg_path)
        
        act = hwp.CreateAction("PrintToImage")
        pset = act.CreateSet()
        act.GetDefault(pset)
        pset.SetItem("Format", "JPG")
        pset.SetItem("FileName", abs_jpg_path)
        pset.SetItem("Range", 0)
        pset.SetItem("Resolution", 300)
        act.Execute(pset)
        print(f"-> 성공: '{os.path.basename(jpg_path)}' 저장 완료")

    except Exception as e:
        print(f"-> 오류 발생: {e}")

    # finally:
    #     # 4. 현재 열려있는 문서를 닫고, 닫기 작업이 완료될 때까지 대기
    #     try:
    #         hwp.Clear(1)
            
    #         # --- ★★★ 핵심 수정 사항: 문서 닫기 후 상태 확인 ★★★ ---
    #         # 다음 파일을 열기 전에, 현재 문서 닫기 작업이 완전히 완료되고
    #         # 한/글이 다시 '준비' 상태가 될 때까지 기다립니다.
    #         close_timeout = 50 # 5초
    #         while close_timeout > 0:
    #             if "준비" in hwp.KeyIndicator():
    #                 break
    #             time.sleep(0.1)
    #             close_timeout -= 1
    #         # ----------------------------------------------------

    #     except Exception as cleare:
    #         print(f"문서 닫기 중 오류 발생: {cleare}")

def convert_all_hmls_to_jpg(hml_dir, output_dir):
    """
    한/글 객체를 한 번만 생성하고 재사용하여 모든 HML 파일을 JPG로 변환합니다.
    """
    hwp = None
    try:
        print("한/글 오토메이션 객체를 한 번만 생성합니다...")
        hwp = win32com.client.Dispatch("HwpFrame.HwpObject.2")
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModuleExample")
        print("객체 생성 완료.")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"출력 디렉토리 생성: {output_dir}")

        hml_files = [f for f in os.listdir(hml_dir) if f.endswith('.hml')]
        if not hml_files:
            print(f"'{hml_dir}' 폴더에 HML 파일이 없습니다.")
            return

        print(f"총 {len(hml_files)}개의 HML 파일을 변환합니다.")

        for hml_file in hml_files:
            hml_path = os.path.join(hml_dir, hml_file)
            jpg_file = os.path.splitext(hml_file)[0] + '.jpg'
            jpg_path = os.path.join(output_dir, jpg_file)
            
            print(f"\n변환 시작: {hml_file} -> {jpg_file}")
            convert_hwp_to_jpg(hwp, hml_path, jpg_path)

    except Exception as e:
        print(f"전체 변환 작업 중 심각한 오류 발생: {e}")

    finally:
        if hwp:
            try:
                hwp.Quit()
                print("\n모든 작업 완료 후, 한/글 프로그램을 완전히 종료했습니다.")
            except Exception as e:
                print(f"한/글 프로그램 종료 중 오류 발생: {e}")


if __name__ == "__main__":
    hml_dir = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\output_split_hml'
    output_jpg_dir = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\images'
    
    convert_all_hmls_to_jpg(hml_dir, output_jpg_dir)

# --- 사용 예시 ---
# 실제 파일 경로로 바꿔서 사용하세요.
# 입력 HWP 파일 경로
#     input_hwp_file_path = r'C:\Users\USER\Downloads\한글-템플릿2.hwp'
# # 출력 JPG 파일 경로 (다중 페이지 시 파일명 뒤에 페이지 번호가 붙을 수 있습니다)
#     output_jpg_file_path = r'.\YourDocument_output.jpg'

#     convert_hwp_to_jpg(input_hwp_file_path, output_jpg_file_path)

