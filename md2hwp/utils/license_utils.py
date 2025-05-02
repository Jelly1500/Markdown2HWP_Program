# md2hwp/utils/license_utils.py
import os
import json
import datetime
import requests # requests 임포트 추가

try:
    from ..config import LICENSE_FILE_PATH, LICENSE_SERVER_URL
    from .machine_info import get_machine_id
except ImportError:
    print("오류: config 또는 machine_info 모듈 임포트 실패 (license_utils.py)")
    LICENSE_FILE_PATH = "license.dat"
    LICENSE_SERVER_URL = None
    def get_machine_id(): return None


def save_license_info(license_data):
    """라이선스 정보를 로컬 파일에 JSON으로 저장 (간단 버전)"""
    try:
        with open(LICENSE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(license_data, f, ensure_ascii=False, indent=4) # 가독성 위해 indent 추가
        try:
             if os.name != 'nt': 
                  os.chmod(LICENSE_FILE_PATH, 0o600)
        except OSError:
             pass 
        return True
    except Exception as e:
        print(f"라이선스 정보 저장 오류: {e}")
        return False

def load_license_info():
    """로컬 파일에서 라이선스 정보 로드"""
    try:
        if os.path.exists(LICENSE_FILE_PATH):
            with open(LICENSE_FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                     print("라이선스 파일이 비어 있습니다.")
                     delete_license_info() 
                     return None
                try:
                     return json.loads(content)
                except json.JSONDecodeError:
                     print("라이선스 파일 형식이 잘못되었습니다 (JSON 오류).")
                     delete_license_info()
                     return None
        return None 
    except Exception as e:
        print(f"라이선스 정보 로드 오류: {e}")
        delete_license_info() 
        return None

def delete_license_info():
    """로컬 라이선스 정보 파일 삭제"""
    try:
        if os.path.exists(LICENSE_FILE_PATH):
            os.remove(LICENSE_FILE_PATH)
            print("로컬 라이선스 정보 삭제됨.")
        return True
    except Exception as e:
        print(f"라이선스 정보 삭제 오류: {e}")
        return False

def validate_license_on_server(license_key):
    """라이선스 키를 서버(Cloud Function)에서 검증"""
    if not LICENSE_SERVER_URL or "YOUR_DEPLOYED_CLOUD_FUNCTION_URL" in LICENSE_SERVER_URL:
        print("오류: 라이선스 서버 URL이 올바르게 설정되지 않았습니다.")
        return {"status": "error", "message": "라이선스 서버 URL 미설정"}

    machine_id = get_machine_id()
    if not license_key:
        return {"status": "error", "message": "라이선스 키가 제공되지 않았습니다."}
    if not machine_id:
        print("경고: Machine ID 생성 실패. 검증은 시도하나 비정상 동작 가능성 있음.")

    payload = json.dumps({
        "license_key": license_key,
        "machine_id": machine_id 
    })
    headers = {"Content-Type": "application/json"}

    try:
        print(f"서버({LICENSE_SERVER_URL})로 라이선스 검증 요청 전송...")
        response = requests.post(LICENSE_SERVER_URL, data=payload, headers=headers, timeout=20) # 타임아웃 20초

        print(f"서버 응답 상태 코드: {response.status_code}")

        response.raise_for_status()

        try:
             return response.json()
        except json.JSONDecodeError:
             print("서버 응답이 유효한 JSON 형식이 아닙니다.")
             return {"status": "error", "message": "서버로부터 잘못된 형식의 응답을 받았습니다."}

    except requests.exceptions.Timeout:
        print("라이선스 서버 연결 시간 초과")
        return {"status": "error", "message": "라이선스 서버 연결 시간 초과"}
    except requests.exceptions.RequestException as e:
        error_message = "라이선스 서버 통신 오류"
        status_code = e.response.status_code if e.response is not None else "N/A"
        print(f"License server communication error: {e}, Status Code: {status_code}")
        try:
             error_content_type = e.response.headers.get('Content-Type', '') if e.response is not None else ''
             if e.response is not None and 'application/json' in error_content_type:
                  error_details = e.response.json().get("message", "")
                  if error_details:
                       if status_code == 403 and "유효하지 않습니다" in error_details:
                            error_message = "입력하신 라이선스 키가 유효하지 않습니다."
                       elif status_code == 403 and "활성화 횟수" in error_details:
                            error_message = "라이선스 활성화 횟수를 초과했습니다."
                       elif status_code == 403 and "만료" in error_details:
                             error_message = "라이선스가 만료되었습니다."
                       elif status_code == 403 and "활성 상태가 아" in error_details:
                             error_message = "라이선스가 활성 상태가 아닙니다."
                       else: 
                            error_message = f"오류({status_code}): {error_details}"
             else:
                  error_message = f"서버 통신 오류 (코드: {status_code})"

        except Exception as parse_err:
             print(f"Error parsing error response: {parse_err}")
             error_message = f"서버 오류 응답 처리 중 문제 발생 (코드: {status_code})"

        return {"status": "error", "message": error_message}
    except Exception as e: 
        print(f"Unexpected error during license validation: {e}")
        return {"status": "error", "message": f"검증 중 알 수 없는 오류 발생"}