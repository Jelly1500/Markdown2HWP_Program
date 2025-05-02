# md2hwp/utils/machine_info.py

import uuid
import hashlib
import platform

def get_machine_id():
    """
    기기의 고유 식별자를 생성 (MAC 주소 기반 + 플랫폼 정보).
    """
    try:
        node_id = uuid.getnode()
        mac_address = ':'.join(('%012X' % node_id)[i:i+2] for i in range(0, 12, 2))
        if mac_address == "00:00:00:00:00:00":
             mac_address = f"node-{platform.node()}"

        system_info = f"{platform.system()}-{platform.machine()}-{platform.processor()}"
        raw_id = f"{mac_address}-{system_info}"
        hashed_id = hashlib.sha256(raw_id.encode('utf-8', 'ignore')).hexdigest()
        return hashed_id
    except Exception as e:
        print(f"Machine ID 생성 오류: {e}")
        try:
             fallback_id = str(uuid.uuid4())
             print(f"Using fallback machine ID: {fallback_id}")
             return hashlib.sha256(fallback_id.encode()).hexdigest()
        except:
             return hashlib.sha256("fallback_error_id".encode()).hexdigest()