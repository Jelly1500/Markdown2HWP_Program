# functions/main.py
import firebase_admin
from firebase_admin import firestore,initialize_app
from firebase_functions import https_fn # 최신 SDK 임포트
import google.cloud.firestore # Firestore 클라이언트 타입 힌트 위해
import datetime
from datetime import timezone # 표준 라이브러리 사용
import json # JSON 응답 생성을 위해
from flask import Flask, jsonify

# --- Firebase Admin SDK 초기화 (전역 범위에서 단순하게 시도) ---
# 기본 예제가 이렇게 작동했으므로 다시 시도해봅니다.
# 만약 이 방식으로 또 Timeout 오류가 발생하면 지연 초기화 로직을 다시 고려해야 합니다.
try:
    initialize_app()
except ValueError:
    pass # 이미 초기화된 경우 무시
# --------------------------------------------------------

@https_fn.on_request() # 데코레이터 변경
def validate_license(req: https_fn.Request) -> https_fn.Response: # 요청/응답 타입 변경
    """라이선스 검증 HTTP Cloud Function (firebase_functions SDK 사용)"""
    # CORS 설정 (필요시)
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    if req.method == 'OPTIONS':
        return https_fn.Response("", status=204, headers=headers)
    if req.method != 'POST':
        # Response 객체 생성 방식으로 변경, jsonify 대신 json.dumps 사용
        response_data = {"status": "error", "message": "Method Not Allowed"}
        return https_fn.Response(json.dumps(response_data), status=405, headers=headers, mimetype='application/json')

    try:
        # Firestore 클라이언트 가져오기 (Admin SDK 초기화는 전역에서 수행)
        db = firestore.client()

        # 요청 본문 파싱 (https_fn.Request는 .json 속성 사용 가능)
        try:
            data = req.json # .json 속성 사용 또는 req.get_json(silent=True)
            if not data:
                 raise ValueError("Request body is empty or not valid JSON")
        except Exception as parse_error: # JSON 파싱 오류 처리
            print(f"JSON parsing error: {parse_error}")
            response_data = {"status": "error", "message": "Invalid JSON request"}
            return https_fn.Response(json.dumps(response_data), status=400, headers=headers, mimetype='application/json')

        license_key = data.get('license_key')
        machine_id = data.get('machine_id')

        print("-" * 30)
        print(f"DEBUG [Server]: 수신된 라이선스 키: '{license_key}'") # 따옴표로 감싸서 공백 확인 용이하게
        print(f"DEBUG [Server]: 수신된 Machine ID: '{machine_id}'")
        print("-" * 30)


        if not license_key or not machine_id:
            response_data = {"status": "error", "message": "Missing license_key or machine_id"}
            return https_fn.Response(json.dumps(response_data), status=400, headers=headers, mimetype='application/json')

        # Firestore 문서 조회
        doc_ref = db.collection('licenses').document(license_key)
        doc = None # 미리 정의
        try:
            print(f"DEBUG [Server]: Firestore에서 문서 '{license_key}' 조회 시도...")
            doc = doc_ref.get() # Firestore 읽기 시도
            print(f"DEBUG [Server]: Firestore 조회 완료. 문서 존재 여부: {doc.exists}")
        except Exception as firestore_error:
            print(f"ERROR [Server]: Firestore 조회 중 오류 발생: {firestore_error}")
            # Firestore 접근 오류 시 500 에러 반환
            import traceback
            traceback.print_exc()
            return jsonify({"status": "error", "message": "데이터베이스 접근 중 오류 발생"}), 500, headers

        if not doc.exists:
            print(f"DEBUG [Server]: 문서 '{license_key}' 찾지 못함.")
            return jsonify({"status": "invalid_key", "message": "라이선스 키가 유효하지 않습니다."}), 403, headers


        if not doc.exists:
            response_data = {"status": "invalid_key", "message": "라이선스 키가 유효하지 않습니다."}
            return https_fn.Response(json.dumps(response_data), status=403, headers=headers, mimetype='application/json')

        license_data = doc.to_dict()

        # --- 검증 로직 (이전과 동일) ---
        # 1. 상태 확인
        if license_data.get('status') != 'active':
            response_data = {"status": "inactive_key", "message": "라이선스가 활성 상태가 아닙니다."}
            return https_fn.Response(json.dumps(response_data), status=403, headers=headers, mimetype='application/json')
        # 2. 만료일 확인
        expiry_date_utc = license_data.get('expiryDate')
        if expiry_date_utc:
             if isinstance(expiry_date_utc, datetime.datetime):
                  now_utc = datetime.datetime.now(timezone.utc)
                  if now_utc > expiry_date_utc.replace(tzinfo=timezone.utc):
                       response_data = {"status": "expired_key", "message": "라이선스가 만료되었습니다."}
                       return https_fn.Response(json.dumps(response_data), status=403, headers=headers, mimetype='application/json')
             else: print(f"Warning: expiryDate format is not datetime: {type(expiry_date_utc)}")
        # 3. 활성화 확인
        activations = license_data.get('activations', [])
        max_activations = int(license_data.get('maxActivations', 1))
        is_already_active = machine_id in activations
        if is_already_active:
             response_data = {"status": "valid", "message": "이미 이 기기에서 활성화된 라이선스입니다."}
             return https_fn.Response(json.dumps(response_data), status=200, headers=headers, mimetype='application/json')
        else:
            if len(activations) < max_activations:
                try:
                    doc_ref.update({'activations': firestore.ArrayUnion([machine_id])})
                    response_data = {"status": "valid", "message": "라이선스가 성공적으로 활성화되었습니다."}
                    return https_fn.Response(json.dumps(response_data), status=200, headers=headers, mimetype='application/json')
                except Exception as db_error:
                     print(f"Firestore update error: {db_error}")
                     response_data = {"status": "error", "message": "활성화 정보 업데이트 중 오류 발생"}
                     return https_fn.Response(json.dumps(response_data), status=500, headers=headers, mimetype='application/json')
            else:
                 response_data = {"status": "limit_reached", "message": f"라이선스 활성화 횟수({max_activations}대)를 초과했습니다."}
                 return https_fn.Response(json.dumps(response_data), status=403, headers=headers, mimetype='application/json')
        # --- 검증 로직 끝 ---

    except Exception as e:
        print(f"Error validating license: {e}")
        import traceback
        traceback.print_exc() # 상세 오류 로깅
        response_data = {"status": "error", "message": f"서버 내부 오류 발생"}
        return https_fn.Response(json.dumps(response_data), status=500, headers=headers, mimetype='application/json')