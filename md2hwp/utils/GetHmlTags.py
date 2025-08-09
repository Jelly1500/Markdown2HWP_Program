import re
import json
import os

def extract_hml_definitions(file_path):
    """
    HML 파일에서 <SECDEF>...</SECDEF>와 첫 번째 <COLDEF>.../> 패턴의 문자열을 추출합니다.
    (이 함수는 변경되지 않았습니다.)
    """
    secdef_list = []
    coldef = None
    error_message = None

    secdef_pattern = r'(?s)<SECDEF.*?<\/SECDEF>'
    coldef_pattern = r'(?s)<COLDEF.*?/>'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        secdef_list = re.findall(secdef_pattern, content)
        coldef_match = re.search(coldef_pattern, content)
        if coldef_match:
            coldef = coldef_match.group()

    except FileNotFoundError:
        error_message = f"오류: 지정된 HML 파일을 찾을 수 없습니다 - {file_path}"
        print(error_message)
    except UnicodeDecodeError:
        error_message = f"오류: 파일 인코딩 문제. '{file_path}' 파일을 UTF-8로 디코딩하는데 실패했습니다."
        print(error_message)
    except Exception as e:
        error_message = f"파일 읽기 또는 처리 중 예기치 않은 오류 발생: {e}"
        print(error_message)

    result = {
        "SECDEF": secdef_list,
        "COLDEF": coldef if coldef else None
    }
    if error_message:
        result["error"] = error_message

    return json.dumps(result, indent=4, ensure_ascii=False)

def find_all_balanced_p_tags(hml_body_content):
    """
    중첩 구조를 고려하여 모든 최상위 <P>...</P> 블록을 정확하게 추출합니다.
    (이 함수는 변경되지 않았습니다.)
    """
    p_blocks = []
    cursor = 0
    tag_finder = re.compile(r'<(/?)P[\s>]', re.IGNORECASE)

    while cursor < len(hml_body_content):
        open_tag_match = re.search(r'<P[\s>]', hml_body_content[cursor:], re.IGNORECASE)
        if not open_tag_match:
            break

        start_index = cursor + open_tag_match.start()
        depth = 1
        scan_cursor = cursor + open_tag_match.end()

        while depth > 0:
            next_tag_match = tag_finder.search(hml_body_content, scan_cursor)
            if not next_tag_match:
                print(f"오류: 파일 끝까지 도달했으나 <P> 태그의 짝을 맞출 수 없습니다. (시작 위치: {start_index})")
                return []
            
            is_closing_tag = next_tag_match.group(1) == '/'
            if is_closing_tag:
                depth -= 1
            else:
                depth += 1
            
            scan_cursor = next_tag_match.end()

        end_index = hml_body_content.find('>', next_tag_match.start()) + 1
        p_blocks.append(hml_body_content[start_index:end_index])
        cursor = end_index

    return p_blocks

def split_hml_and_apply_defs(source_hml_path, output_directory):
    """
    HML 파일을 개별 P 태그(문단) 단위로 분리하고, <CHAR> 태그가 있는 문단만 파일로 저장합니다.
    """
    print("--- HML 분리 및 설정 적용 시작 ---")

    defs_data = json.loads(extract_hml_definitions(source_hml_path))
    if defs_data.get("error"):
        print(f"오류로 인해 처리를 중단합니다: {defs_data['error']}")
        return

    secdef_list = defs_data.get("SECDEF", [])
    coldef = defs_data.get("COLDEF")
    if not coldef or not secdef_list:
        print("오류: HML 파일에서 COLDEF 또는 SECDEF를 찾을 수 없어 처리를 중단합니다.")
        return
    
    defs_block = "\n" + coldef + "\n" + "\n".join(secdef_list) + "\n"
    print("적용할 용지 설정(SECDEF/COLDEF)을 찾았습니다.")

    try:
        with open(source_hml_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        body_open_match = re.search(r'(?s)<BODY.*?>', original_content)
        body_close_match = re.search(r'(?s)</BODY>', original_content)
        section_open_match = re.search(r'(?s)<SECTION.*?>', original_content)

        if not body_open_match or not body_close_match or not section_open_match:
            print("오류: HML 파일에서 <BODY> 또는 <SECTION> 구조를 찾을 수 없습니다.")
            return

        header_part = original_content[:body_open_match.start()]
        body_open_tag = body_open_match.group(0)
        body_content = original_content[body_open_match.end():body_close_match.start()]
        body_close_tag = body_close_match.group(0)
        footer_part = original_content[body_close_match.end():]
        section_open_tag = section_open_match.group(0)
        section_close_tag = '</SECTION>'

    except Exception as e:
        print(f"원본 HML 파일 처리 중 오류 발생: {e}")
        return

    print("사용자 정의 파서를 사용하여 중첩 구조를 고려한 문단 분리를 시작합니다...")
    all_p_blocks = find_all_balanced_p_tags(body_content)
    print(f"총 {len(all_p_blocks)}개의 P 태그 블록을 발견했습니다.")

    # --- ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★ ---
    # --- 요구사항 반영: <CHAR> 태그가 있는 P 블록만 필터링하는 로직 ---
    # --- ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★ ---
    print("실제 내용이 있는 문단(<CHAR> 태그 포함)만 필터링합니다...")
    necessary_p_blocks = [block for block in all_p_blocks if "<CHAR>" in block]
    
    if not necessary_p_blocks:
        print("오류: 파일에서 실제 내용(<CHAR> 태그)이 포함된 문단을 찾지 못했습니다.")
        return
    
    print(f"필터링 후, 총 {len(necessary_p_blocks)}개의 유효한 문단을 개별 파일로 생성합니다.")

    os.makedirs(output_directory, exist_ok=True)
    base_name = os.path.basename(source_hml_path)
    name, ext = os.path.splitext(base_name)

    # 필터링된 리스트(necessary_p_blocks)를 사용하여 파일 생성
    for i, p_block in enumerate(necessary_p_blocks):
        # 주의: 일부 문서에서 <TEXT> 내부에 SECDEF/COLDEF를 삽입하면 한/글이 충돌할 수 있음
        # HEAD에는 원래의 SECDEF/COLDEF가 유지되므로, P 블록에는 추가 삽입하지 않고 그대로 사용
        final_section = f"{section_open_tag}\n{p_block}\n{section_close_tag}"
        final_hml_content = f"{header_part}{body_open_tag}\n{final_section}\n{body_close_tag}{footer_part}"

        output_path = os.path.join(output_directory, f"{name}_paragraph_{i+1:03d}{ext}")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_hml_content)
            # 카운터가 필터링된 리스트의 길이를 기준으로 하도록 수정
            print(f"({i+1}/{len(necessary_p_blocks)}) 생성 완료: {output_path}")
        except Exception as e:
            print(f"파일 저장 중 오류 발생 '{output_path}': {e}")
            
    print("\n--- 모든 작업 완료 ---")

def extract_meaningful_p_tags(file_path):
    """
    HML 파일에서 <CHAR> 태그를 포함하는 모든 P 태그 문자열을 리스트로 추출하여 반환합니다.

    Args:
        file_path (str): 분석할 HML 파일의 경로.

    Returns:
        list: <CHAR> 태그를 포함하는 <P>...</P> 블록 문자열의 리스트.
              오류 발생 시 빈 리스트를 반환합니다.
    """
    print(f"--- '{os.path.basename(file_path)}' 파일에서 문단 추출 시작 ---")
    
    try:
        # 1. HML 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        # 2. BODY 태그 사이의 내용만 추출
        body_open_match = re.search(r'(?s)<BODY.*?>', original_content)
        body_close_match = re.search(r'(?s)</BODY>', original_content)

        if not body_open_match or not body_close_match:
            print("오류: HML 파일에서 <BODY>...</BODY> 구조를 찾을 수 없습니다.")
            return []

        body_content = original_content[body_open_match.end():body_close_match.start()]

        # 3. 모든 P 태그 블록을 정확하게 추출
        all_p_blocks = find_all_balanced_p_tags(body_content)
        print(f"총 {len(all_p_blocks)}개의 P 태그 블록을 발견했습니다.")

        # 4. <CHAR> 태그가 포함된 P 블록만 필터링
        meaningful_p_blocks = [block for block in all_p_blocks if "<CHAR>" in block]
        print(f"필터링 후, 실제 내용이 있는 유효한 문단 {len(meaningful_p_blocks)}개를 추출했습니다.")
        
        return meaningful_p_blocks

    except FileNotFoundError:
        print(f"오류: 지정된 HML 파일을 찾을 수 없습니다 - {file_path}")
        return []
    except Exception as e:
        print(f"파일 처리 중 예기치 않은 오류 발생: {e}")
        return []

# --- 코드 사용 예시 ---
if __name__ == "__main__":
    # TODO: 테스트할 HML 파일의 실제 경로로 아래 변수 값을 변경하세요.
    test_hml_file_path = r'C:\Users\USER\Documents\Github\Markdown2HWP_Program-main\한글-템플릿 (1).hml' # <<<--- 이 부분을 실제 파일 경로로 수정하세요!

    # # TODO: 결과 파일이 저장될 폴더 이름을 지정하세요.
    # output_folder = 'output_split_hml'

    # if not os.path.exists(test_hml_file_path):
    #     print(f"오류: 원본 HML 파일을 찾을 수 없습니다. 경로를 확인하세요: {test_hml_file_path}")
    # else:
    #     split_hml_and_apply_defs(test_hml_file_path, output_folder)

    meaningful_p_tags = extract_meaningful_p_tags(test_hml_file_path)
    print(meaningful_p_tags)