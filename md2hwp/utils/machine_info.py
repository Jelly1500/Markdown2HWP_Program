# md2hwp/utils/machine_info.py
import platform
import subprocess
import hashlib
import uuid # Fallback에 사용

def get_machine_id():
    """
    기기의 고유 식별자를 생성 (Windows: System UUID, Others: Fallback).
    Windows UUID가 일반적으로 가장 안정적입니다.
    """
    machine_id_str = None
    try:
        if platform.system() == "Windows":
            # PowerShell 명령어로 시스템 UUID 가져오기
            # CREATE_NO_WINDOW 플래그는 콘솔 창 숨김
            result = subprocess.run(
                ['powershell', '-Command', '(Get-CimInstance Win32_ComputerSystemProduct).UUID'],
                capture_output=True, text=True, check=True, encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            uuid_str = result.stdout.strip()
            # 유효성 검사 (비어있거나 알려진 잘못된 값 제외)
            if uuid_str and uuid_str.lower() not in ["ffffffff-ffff-ffff-ffff-ffffffffffff", "00000000-0000-0000-0000-000000000000"]:
                machine_id_str = uuid_str
                print(f"DEBUG [Client]: Fetched Machine ID (Windows UUID): {machine_id_str}")
            else:
                print(f"WARN [Client]: Invalid or empty UUID received: '{uuid_str}'. Falling back.")

    except FileNotFoundError:
         print("ERROR [Client]: PowerShell is not available. Cannot fetch Windows UUID.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR [Client]: Failed to execute PowerShell command for UUID: {e}")
    except Exception as e:
        print(f"ERROR [Client]: An unexpected error occurred while fetching Windows UUID: {e}")

    # --- Fallback Logic (Windows UUID 실패 또는 다른 OS) ---
    if machine_id_str is None:
        print("INFO [Client]: Attempting fallback method for Machine ID.")
        try:
            # MAC 주소 시도 (덜 안정적일 수 있음)
            node = uuid.getnode()
            mac_address = ':'.join(('%012X' % node)[i:i+2] for i in range(0, 12, 2))
            if mac_address != "00:00:00:00:00:00":
                print(f"DEBUG [Client]: Using MAC address based ID: {mac_address}")
                # 추가 정보 결합하여 고유성 높이기
                system_info = f"{platform.system()}-{platform.machine()}-{platform.node()}"
                machine_id_str = f"{mac_address}-{system_info}"
            else:
                 print("WARN [Client]: MAC address is all zeros. Using hostname based fallback.")
                 # 호스트명 기반 Fallback
                 fallback_base = f"{platform.node()}-{platform.system()}-{platform.machine()}"
                 machine_id_str = fallback_base

        except Exception as fallback_err:
            print(f"ERROR [Client]: Error during fallback ID generation: {fallback_err}")
            # 최후의 수단 (고정값은 피하는 것이 좋음)
            machine_id_str = "critical_fallback_machine_id_" + str(uuid.uuid4()) # 랜덤성 추가
            print(f"CRITICAL [Client]: Fallback failed. Using randomized constant fallback.")

    # 최종적으로 얻은 문자열을 해시하여 반환 (개인정보 보호 및 일관된 형식)
    if machine_id_str:
        hashed_id = hashlib.sha256(machine_id_str.encode('utf-8', 'ignore')).hexdigest()
        print(f"DEBUG [Client]: Final Machine ID (Hashed): {hashed_id[:8]}...")
        return hashed_id
    else:
         # 이론상 도달하면 안되지만, 만약을 위해
         print(f"CRITICAL [Client]: Failed to generate any machine ID string.")
         return hashlib.sha256("ultimate_fallback_error".encode()).hexdigest()