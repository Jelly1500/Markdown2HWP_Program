# functions/main.py
import firebase_admin
from firebase_admin import firestore, initialize_app
from firebase_functions import https_fn
import google.cloud.firestore
import datetime
from datetime import timezone
import json
# from flask import Flask, jsonify # Flask 및 jsonify는 직접 응답 생성 방식으로 변경하면서 필요 없어졌을 수 있습니다. 확인 후 삭제 고려.

try:
    initialize_app()
except ValueError:
    pass # 이미 초기화된 경우 무시
# --------------------------------------------------------

@https_fn.on_request()
def validate_license(req: https_fn.Request) -> https_fn.Response:
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
        response_data = {"status": "error", "message": "Method Not Allowed"}
        return https_fn.Response(json.dumps(response_data), status=405, headers=headers, mimetype='application/json')

    try:
        db = firestore.client()

        try:
            data = req.json
            if not data:
                 raise ValueError("Request body is empty or not valid JSON")
        except Exception as parse_error:
            # print(f"JSON parsing error: {parse_error}") # 디버그 print 삭제/주석 처리
            response_data = {"status": "error", "message": "Invalid JSON request"}
            return https_fn.Response(json.dumps(response_data), status=400, headers=headers, mimetype='application/json')

        license_key = data.get('license_key')
        machine_id = data.get('machine_id')

        # print("-" * 30) # 디버그 print 삭제/주석 처리
        # print(f"DEBUG [Server]: 수신된 라이선스 키: '{license_key}'") # 디버그 print 삭제/주석 처리
        # print(f"DEBUG [Server]: 수신된 Machine ID: '{machine_id}'") # 디버그 print 삭제/주석 처리
        # print("-" * 30) # 디버그 print 삭제/주석 처리


        if not license_key or not machine_id:
            response_data = {"status": "error", "message": "Missing license_key or machine_id"}
            return https_fn.Response(json.dumps(response_data), status=400, headers=headers, mimetype='application/json')

        doc_ref = db.collection('licenses').document(license_key)
        doc = None
        try:
            # print(f"DEBUG [Server]: Firestore에서 문서 '{license_key}' 조회 시도...") # 디버그 print 삭제/주석 처리
            doc = doc_ref.get()
            # print(f"DEBUG [Server]: Firestore 조회 완료. 문서 존재 여부: {doc.exists}") # 디버그 print 삭제/주석 처리
        except Exception as firestore_error:
            print(f"ERROR [Server]: Firestore 조회 중 오류 발생: {firestore_error}") # 오류 로깅은 유지하는 것이 좋습니다.
            import traceback
            traceback.print_exc() # 오류 트레이스백 로깅도 유지하는 것이 좋습니다.
            # response_data = {"status": "error", "message": "데이터베이스 접근 중 오류 발생"} # jsonify 대신 json.dumps 사용하도록 이미 수정되어 있음
            return https_fn.Response(json.dumps({"status": "error", "message": "데이터베이스 접근 중 오류 발생"}), status=500, headers=headers, mimetype='application/json')


        if not doc.exists:
            # print(f"DEBUG [Server]: 문서 '{license_key}' 찾지 못함.") # 디버그 print 삭제/주석 처리
            response_data = {"status": "invalid_key", "message": "라이선스 키가 유효하지 않습니다."}
            # jsonify 대신 json.dumps 사용하도록 이미 수정되어 있음
            return https_fn.Response(json.dumps(response_data), status=403, headers=headers, mimetype='application/json')


        license_data = doc.to_dict()

        # --- 검증 로직 (이전과 동일) ---
        if license_data.get('status') != 'active':
            response_data = {"status": "inactive_key", "message": "라이선스가 활성 상태가 아닙니다."}
            return https_fn.Response(json.dumps(response_data), status=403, headers=headers, mimetype='application/json')

        expiry_date_utc = license_data.get('expiryDate')
        if expiry_date_utc:
             if isinstance(expiry_date_utc, datetime.datetime):
                  now_utc = datetime.datetime.now(timezone.utc)
                  if now_utc > expiry_date_utc.replace(tzinfo=timezone.utc):
                       response_data = {"status": "expired_key", "message": "라이선스가 만료되었습니다."}
                       return https_fn.Response(json.dumps(response_data), status=403, headers=headers, mimetype='application/json')
             # else: print(f"Warning: expiryDate format is not datetime: {type(expiry_date_utc)}") # 경고 print 삭제/주석 처리

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
                     print(f"Firestore update error: {db_error}") # 오류 로깅은 유지하는 것이 좋습니다.
                     response_data = {"status": "error", "message": "활성화 정보 업데이트 중 오류 발생"}
                     return https_fn.Response(json.dumps(response_data), status=500, headers=headers, mimetype='application/json')
            else:
                 response_data = {"status": "limit_reached", "message": f"라이선스 활성화 횟수({max_activations}대)를 초과했습니다."}
                 return https_fn.Response(json.dumps(response_data), status=403, headers=headers, mimetype='application/json')
        # --- 검증 로직 끝 ---

    except Exception as e:
        print(f"Error validating license: {e}") 
        import traceback
        traceback.print_exc() 
        response_data = {"status": "error", "message": f"서버 내부 오류 발생"}
        return https_fn.Response(json.dumps(response_data), status=500, headers=headers, mimetype='application/json')

