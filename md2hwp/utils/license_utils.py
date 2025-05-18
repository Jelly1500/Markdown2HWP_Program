# md2hwp/utils/license_utils.py
import json
import datetime
import requests
import keyring 
import winreg  # 윈도우 레지스트리 접근을 위한 모듈 추가

try:
    from ..config import LICENSE_SERVER_URL, API_GATEWAY_KEY
    from .machine_info import get_machine_id
except ImportError as e:
    print(f"CRITICAL ERROR: config 또는 machine_info 모듈 임포트 실패 (license_utils.py): {e}")
    LICENSE_SERVER_URL = "YOUR_FIREBASE_FUNCTION_URL_HERE"
    API_GATEWAY_KEY = "YOUR_DEFAULT_API_KEY_IF_CONFIG_FAILS"
    print(f"WARNING: Using placeholder LICENSE_SERVER_URL: {LICENSE_SERVER_URL}")
    def get_machine_id():
        print("ERROR: get_machine_id could not be imported!")
        return "import_error_machine_id" + str(datetime.datetime.now().timestamp()) # 고유성 시도

SERVICE_NAME = "MD2HWPConverterLicense" 
USERNAME = "license_data"          
PUBLISHER = "사하구청"  # 레지스트리 키 접근에 사용 (installer.iss와 동일해야 함)
APP_NAME = "마크다운 HWP 변환기"  # 레지스트리 키 접근에 사용 (installer.iss와 동일해야 함)
REG_KEY = f"SOFTWARE\\{PUBLISHER}\\{APP_NAME}"

def get_registry_license_key():
    """레지스트리에 저장된 라이선스 키를 가져옵니다."""
    try:
        # 먼저 HKLM(로컬 시스템) 확인
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY)
            license_key = winreg.QueryValueEx(key, "LicenseKey")[0]
            winreg.CloseKey(key)
            print("INFO [LicenseUtils]: HKLM 레지스트리에서 라이선스 키를 불러왔습니다.")
            return license_key
        except FileNotFoundError:
            # HKLM에 없으면 HKCU(현재 사용자) 확인
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY)
            license_key = winreg.QueryValueEx(key, "LicenseKey")[0]
            winreg.CloseKey(key)
            print("INFO [LicenseUtils]: HKCU 레지스트리에서 라이선스 키를 불러왔습니다.")
            return license_key
    except FileNotFoundError:
        print("INFO [LicenseUtils]: 레지스트리에 라이선스 키가 없습니다.")
        return None
    except Exception as e:
        print(f"ERROR [LicenseUtils]: 레지스트리에서 라이선스 키 로드 실패: {e}")
        return None

def save_license_info(license_data: dict):
    """라이선스 정보(dict)를 Windows 자격 증명 관리자에 저장"""
    if not isinstance(license_data, dict):
         print("ERROR [LicenseUtils]: save_license_info에는 dict 타입만 저장 가능합니다.")
         return False
    try:
        data_str = json.dumps(license_data, ensure_ascii=False)
        keyring.set_password(SERVICE_NAME, USERNAME, data_str)
        print("INFO [LicenseUtils]: 라이선스 정보가 자격 증명 관리자에 안전하게 저장되었습니다.")
        return True
    except Exception as e:
        print(f"ERROR [LicenseUtils]: 자격 증명 저장 실패: {e}")
        return False

def load_license_info() -> dict | None:
    """Windows 자격 증명 관리자에서 라이선스 정보(dict) 로드
    또는 설치 과정에서 레지스트리에 저장된 키가 있으면 그것을 사용"""
    # 먼저 레지스트리에서 라이선스 키 확인
    license_key = get_registry_license_key()
    if license_key and license_key == "TEST-KEY-1234-ABCD":  # 하드코딩된 테스트 키와 비교
        print("INFO [LicenseUtils]: 레지스트리에서 유효한 라이선스 키를 찾았습니다.")
        # 라이선스 키를 자격 증명 관리자에도 저장하여 추후 검증 절차 간소화
        current_time = datetime.datetime.now()
        license_info = {"key": license_key, "last_checked": current_time.isoformat()}
        save_license_info(license_info)
        return license_info
    
    # 레지스트리에 유효한 키가 없으면 자격 증명 관리자 확인
    try:
        data_str = keyring.get_password(SERVICE_NAME, USERNAME)
        if data_str:
            license_data = json.loads(data_str)
            print("INFO [LicenseUtils]: 자격 증명 관리자에서 라이선스 정보를 로드했습니다.")
            return license_data
        else:
            print("INFO [LicenseUtils]: 저장된 라이선스 정보가 없습니다.")
            return None
    except json.JSONDecodeError as e:
         print(f"ERROR [LicenseUtils]: 저장된 라이선스 데이터 형식 오류 (JSON 파싱 실패): {e}. 저장된 정보 삭제 시도.")
         delete_license_info() 
         return None
    except Exception as e:
        print(f"ERROR [LicenseUtils]: 자격 증명 로드 실패: {e}")
        return None

def delete_license_info():
    """Windows 자격 증명 관리자에서 라이선스 정보 삭제"""
    try:
        keyring.delete_password(SERVICE_NAME, USERNAME)
        print("INFO [LicenseUtils]: 자격 증명 관리자에서 라이선스 정보를 삭제했습니다.")
        return True
    except keyring.errors.PasswordDeleteError:
        print("INFO [LicenseUtils]: 삭제할 저장된 라이선스 정보가 없습니다.")
        return True
    except Exception as e:
        print(f"ERROR [LicenseUtils]: 자격 증명 삭제 실패: {e}")
        return False

def validate_license_on_server(license_key: str) -> dict:
    """라이선스 키를 서버(API Gateway)에서 검증 (API 키 포함)
    테스트 키(TEST-KEY-1234-ABCD)의 경우 서버 검증 없이 유효한 것으로 처리"""
    # 테스트 키인 경우 서버 검증 없이 유효하다고 처리
    if license_key == "TEST-KEY-1234-ABCD":
        print("INFO [LicenseUtils]: 테스트 키를 감지했습니다. 유효한 것으로 처리합니다.")
        return {"status": "valid", "message": "테스트 키 확인됨"}
    
    if not LICENSE_SERVER_URL or "YOUR_FIREBASE_FUNCTION_URL" in LICENSE_SERVER_URL: 
        print("CRITICAL ERROR [LicenseUtils]: 라이선스 서버 URL(API Gateway URL)이 설정되지 않았습니다!")
        return {"status": "error", "message": "라이선스 서버 URL 미설정"}

    if not API_GATEWAY_KEY or "YOUR_DEFAULT_API_KEY" in API_GATEWAY_KEY: 
        print("CRITICAL ERROR [LicenseUtils]: API Gateway 키가 설정되지 않았습니다!")
        return {"status": "error", "message": "API Gateway 키 미설정"}

    machine_id = get_machine_id()
    if not license_key:
         return {"status": "error", "message": "라이선스 키가 제공되지 않았습니다."}
    if not machine_id or "error" in machine_id or "fallback" in machine_id:
         print(f"WARN [LicenseUtils]: 유효한 Machine ID 생성 실패 ('{machine_id}'). 검증은 시도하나 문제가 발생할 수 있습니다.")

    request_url = f"{LICENSE_SERVER_URL}?key={API_GATEWAY_KEY}"

    payload = {"license_key": license_key, "machine_id": machine_id}
    headers = {"Content-Type": "application/json"}

    try:
        print(f"INFO [LicenseUtils]: 서버({request_url})로 라이선스 검증 요청...")
        print(f"DEBUG [LicenseUtils]: Payload - {payload}")
        response = requests.post(request_url, json=payload, headers=headers, timeout=20)

        print(f"INFO [LicenseUtils]: 서버 응답 상태 코드: {response.status_code}")

        if not response.ok:
            error_message = f"서버 오류 발생 (코드: {response.status_code})"
            try:
                error_data = response.json()
                server_msg = error_data.get("message", "서버에서 추가 메시지 없음")
                print(f"DEBUG [LicenseUtils]: Server error response: {error_data}")

                if response.status_code == 401: # API 키가 없거나 잘못된 경우
                    error_message = "API 접근 권한이 없습니다. (잘못된 API 키)"
                elif response.status_code == 403: # API 키는 맞지만, 내부 로직(라이선스 등)에서 거부
                    if "invalid_key" in server_msg: error_message = "입력하신 라이선스 키가 유효하지 않습니다."
                    elif "limit_reached" in server_msg: error_message = "라이선스 활성화 횟수를 초과했습니다."
                    elif "expired_key" in server_msg: error_message = "라이선스가 만료되었습니다."
                    elif "inactive_key" in server_msg: error_message = "라이선스가 활성 상태가 아닙니다."
                    else: error_message = f"라이선스 접근 거부됨: {server_msg}"
                elif response.status_code >= 500: error_message = "라이선스 서버 내부 오류 발생. 잠시 후 다시 시도해주세요."
                elif response.status_code == 400: error_message = f"잘못된 요청입니다: {server_msg}"
                elif response.status_code == 404: error_message = "라이선스 서버 경로를 찾을 수 없습니다."
                else: error_message = f"오류 ({response.status_code}): {server_msg}"

            except json.JSONDecodeError:
                print("WARN [LicenseUtils]: 서버 오류 응답이 JSON 형식이 아닙니다.")
                error_message = f"서버 오류 (코드: {response.status_code}, 응답 형식 오류)"
            except Exception as parse_err:
                print(f"ERROR [LicenseUtils]: 서버 오류 응답 처리 중 예외: {parse_err}")
                error_message = f"서버 오류 응답 처리 오류 (코드: {response.status_code})"

            print(f"ERROR [LicenseUtils]: {error_message}")
            return {"status": "error", "message": error_message}

        try:
             result = response.json()
             print(f"DEBUG [LicenseUtils]: Server success response: {result}")
             return result
        except json.JSONDecodeError:
             print("ERROR [LicenseUtils]: 서버 성공 응답이 유효한 JSON 형식이 아닙니다.")
             return {"status": "error", "message": "서버로부터 잘못된 형식의 응답을 받았습니다."}

    except requests.exceptions.Timeout:
        print("ERROR [LicenseUtils]: 라이선스 서버 연결 시간 초과")
        return {"status": "error", "message": "라이선스 서버 연결 시간 초과"}
    except requests.exceptions.ConnectionError as e:
         print(f"ERROR [LicenseUtils]: 라이선스 서버 연결 실패: {e}. 네트워크 또는 서버 주소를 확인하세요.")
         return {"status": "error", "message": "라이선스 서버에 연결할 수 없습니다."}
    except requests.exceptions.RequestException as e:
        print(f"ERROR [LicenseUtils]: 라이선스 서버 통신 중 오류 발생: {e}")
        return {"status": "error", "message": f"서버 통신 오류: {e}"}
    except Exception as e:
        print(f"CRITICAL ERROR [LicenseUtils]: 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"검증 중 알 수 없는 오류 발생: {e}"}