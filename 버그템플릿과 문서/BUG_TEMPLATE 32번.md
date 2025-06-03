---
name: 복잡한 HTML 구조(시맨틱 태그, 인라인 스타일, form 요소) 완전 무시로 웹사이트 설계안 핵심 내용 소실되는 심각한 버그
about: 마크다운 문서에 HTML5 시맨틱 태그, 인라인 스타일, form 요소, 복잡한 레이아웃이 포함되어 있을 때 해당 HTML 구조가 완전히 무시되어 웹사이트 설계안, UI 프로토타입, 시스템 화면 구성안 등의 핵심 시각적 요소와 기능 설명이 통째로 사라지는 심각한 문제
title: "복잡한 HTML 구조(시맨틱 태그, 인라인 스타일, form 요소) 완전 무시로 웹사이트 설계안 핵심 내용 소실되는 심각한 버그"
labels: "🐛 심각", "📝 서식 미지원"
assignees: bum103103, 김범준

---

# 버그 리포트

## 어떤 버그인가요?

> 마크다운 문서에 **복잡한 HTML 구조**가 포함되어 있을 때, **HTML5 시맨틱 태그, 인라인 CSS 스타일, form 요소, 레이아웃 구조** 등이 **완전히 무시**되어 변환되지 않는 심각한 문제입니다. **웹사이트 설계안, 사용자 인터페이스 프로토타입, 시스템 화면 구성** 등을 문서화할 때 사용되는 **시각적 구조와 기능 설명**이 **통째로 사라져** 문서의 **핵심 내용이 완전히 소실**됩니다. 이는 **공공기관의 웹사이트 개편, 시스템 구축, 디지털 서비스 설계** 등에서 **화면 설계안과 기능 명세**를 문서화할 때 필수적으로 사용되는 구조로, 이러한 **전문 문서의 가장 중요한 시각적 정보가 변환되지 않아** 문서 자체가 **무의미**해지는 치명적 결함입니다.

<br><br>

## 어떤 상황에서 겪으셨나요?

1. 실행 환경: Windows 10, Python 가상환경
2. 테스트를 수행한 마크다운 문서: 신규 '국민소통포털' 화면 구성 및 주요 기능 설계(안)
3. 테스트한 템플릿: 
   - template_ex_01.hml
   - template_ex_02.hml
   - template_ex_03.hml
   - 새템플릿.hml
   - 템플릿문서.hml
   - 템플릿문서1.hml

테스트한 마크다운 텍스트:
```markdown
# 신규 '국민소통포털' 화면 구성 및 주요 기능 설계(안)

## 1. 포털 메인 화면 구성

<div style="border: 1px solid #ccc; padding: 15px; background-color: #f9f9f9; margin-bottom: 20px;">
  <header style="border-bottom: 1px solid #eee; margin-bottom: 10px; padding-bottom: 10px;">
    <h3 style="margin:0; color:#337ab7;">국민소통포털 <small>(베타 버전)</small></h3>
  </header>
  <nav style="margin-bottom:10px;">
    <a href="#section1" style="margin-right:10px; text-decoration:none;">정책제안</a> |
    <a href="#section2" style="margin-right:10px; text-decoration:none;">국민토론</a> |
    <a href="#section3" style="text-decoration:none;">민원신청</a>
  </nav>
  <article>
    <h4>주요 서비스 안내</h4>
    <p>국민 여러분의 목소리를 듣고, 정책에 반영하기 위한 온라인 소통 공간입니다. <em>자유롭게 의견을 개진</em>해주시기 바랍니다.</p>
    <details open style="margin-top:10px;">
      <summary style="font-weight:bold; cursor:pointer; color:#555;">플랫폼 이용 가이드 보기 (클릭)</summary>
      <ul style="list-style-type:square; margin-top:5px;">
        <li>회원가입 후 모든 서비스 이용 가능</li>
        <li>정책 제안 시 <strong style="color:red;">실명 인증</strong> 필요</li>
        <li><span style="text-decoration:underline;">비방이나 욕설</span>은 사전 통보 없이 삭제될 수 있습니다.</li>
      </ul>
    </details>
  </article>
  <aside style="float:right; width:200px; padding:10px; margin-left:15px; border:1px dotted #aaa; background-color:#eef;">
    <h5><strong>참고 자료</strong></h5>
    <p><small><a href="#">운영규정</a><br><a href="#">FAQ (자주묻는질문)</a></small></p>
  </aside>
  <div style="clear:both;"></div>
  <footer style="border-top: 1px solid #eee; margin-top: 10px; padding-top: 10px; text-align:center; font-size:0.9em;">
    <p>&copy; 2025 대한민국 OOO부처. All rights reserved. <br> 문의: <code>helpdesk@example.go.kr</code></p>
  </footer>
</div>

## 2. 정책 제안 상세 기능

-   **제안서 작성 화면 예시**
    1.  제목 입력 필드: <code>&lt;input type="text" name="proposal_title" style="width:80%; padding:5px;" placeholder="제안 제목을 입력하세요"&gt;</code>
    2.  내용 입력 영역:
        <textarea name="proposal_content" rows="8" style="width:100%; padding:5px;" placeholder="제안 내용을 상세히 작성해주세요. (최대 5000자)"></textarea>
    3.  파일 첨부 (최대 3개, 각 10MB 이하): <code>&lt;input type="file" name="attachment" multiple&gt;</code>
    4.  제출 버튼: <button type="submit" style="background-color: #28a745; color: white; padding: 8px 15px; border: none; border-radius: 4px;">제안서 제출</button>

-   **제안서 검토 상태 표시**
    <p>제안된 내용은 다음 단계로 표시됩니다:</p>
    <ol>
      <li><span style="color:gray;">접수 대기</span> → </li>
      <li><span style="color:orange;">검토 중</span> <progress value="50" max="100" style="width:100px;"></progress> → </li>
      <li><span style="color:green;">답변 완료</span> / <span style="color:red;">반려</span></li>
    </ol>

## 3. 사용자 의견 수렴 (설문조사 예시)

<div style="background-color:#fff8e1; border-left:5px solid #ffc107; padding:10px; margin-top:10px;">
  <p><strong>설문 참여 안내:</strong> 더 나은 서비스를 위해 여러분의 소중한 의견을 들려주세요.</p>
  <label for="satisfaction">1. 전반적인 서비스 만족도는 어떠십니까?</label><br>
  <select name="satisfaction" id="satisfaction" style="padding:5px; margin-top:5px;">
    <option value="5">매우 만족</option>
    <option value="4">만족</option>
    <option value="3">보통</option>
    <option value="2">불만족</option>
    <option value="1">매우 불만족</option>
  </select>
</div>
```

<br><br>

## 어떤 과정에서 버그가 발생했나요?

1. 위 마크다운 텍스트를 파일로 저장
2. 각각의 템플릿으로 변환 시도
3. 변환 결과 확인:
   - **모든 템플릿에서 동일한 치명적 오류 발생:**
     * **모든 HTML 구조와 시각적 요소가 완전히 무시됨**
     * **웹사이트 화면 구성의 핵심 정보가 모두 사라짐**
     * **제목과 기본 텍스트만 남고 UI 설계 내용 전무**
     * **복잡한 레이아웃과 기능 설명이 통째로 소실됨**

### 구체적인 문제 상황:
1. **기대되는 결과:**
   - **포털 메인 화면**: 헤더, 네비게이션, 주요 서비스 안내, 이용 가이드 접이식 메뉴, 참고자료 사이드바, 푸터가 체계적으로 구성된 완전한 레이아웃
   - **정책 제안 기능**: 입력 필드, 텍스트 에어리어, 파일 첨부, 제출 버튼 등의 실제 form 요소들과 검토 상태 진행바
   - **설문조사**: 배경색이 있는 안내 박스, 드롭다운 선택 메뉴 등 실제 사용자 인터페이스 요소
   - **각 화면 요소가 시각적으로 구분**되어 **실제 웹사이트 프로토타입** 형태로 표시

2. **실제 발생하는 결과:**
   ```
   # 신규 '국민소통포털' 화면 구성 및 주요 기능 설계(안)

   ## 1. 포털 메인 화면 구성

   ## 2. 정책 제안 상세 기능

   - 제안서 작성 화면 예시
     1. 제목 입력 필드:
     2. 내용 입력 영역:
     3. 파일 첨부 (최대 3개, 각 10MB 이하):
     4. 제출 버튼:

   - 제안서 검토 상태 표시

   ## 3. 사용자 의견 수렴 (설문조사 예시)
   ```
   - **모든 HTML 구조와 시각적 요소가 완전히 사라짐**
   - **웹사이트 화면의 핵심 구성 요소와 기능 설명 전무**
   - **설계안의 가장 중요한 UI/UX 정보 100% 소실**

### 완전히 무시되는 복잡한 HTML 구조:
1. **HTML5 시맨틱 태그**
   ```html
   <header>, <nav>, <article>, <aside>, <footer>
   <details>, <summary>
   ```

2. **인라인 CSS 스타일링**
   ```html
   style="border: 1px solid #ccc; padding: 15px; background-color: #f9f9f9;"
   style="float:right; width:200px; border:1px dotted #aaa;"
   style="color:red;", style="text-decoration:underline;"
   ```

3. **Form 요소들**
   ```html
   <input type="text" placeholder="제안 제목을 입력하세요">
   <textarea rows="8" placeholder="제안 내용을 상세히 작성해주세요.">
   <button type="submit">제안서 제출</button>
   <select name="satisfaction">
   <progress value="50" max="100">
   ```

4. **복잡한 레이아웃 구조**
   ```html
   <div style="border: 1px solid #ccc; padding: 15px;">
     <header>...</header>
     <nav>...</nav>
     <article>...</article>
     <aside style="float:right;">...</aside>
     <footer>...</footer>
   </div>
   ```

5. **인터랙티브 요소**
   ```html
   <details open>
     <summary style="cursor:pointer;">플랫폼 이용 가이드 보기</summary>
     <ul>...</ul>
   </details>
   ```

### 특히 문제가 되는 상황:
1. **공공기관 웹사이트 개편 프로젝트**
   - **시민 서비스 포털, 정부 24시간 서비스** 등의 **화면 설계안 작성**
   - **개발 업체와의 소통**, **발주 기관 내부 검토** 시 **상세한 UI 구성 공유** 필요
   - **화면 구성 정보 소실**로 **설계 의도 전달 불가** 및 **개발 방향 혼란**

2. **디지털 정부 서비스 설계**
   - **정책 참여 플랫폼, 국민신문고, 온라인 민원서비스** 등의 **기능 설계서**
   - **사용자 경험(UX) 설계**와 **접근성 요구사항** 문서화
   - **UI 요소 정보 부재**로 **접근성 검토 불가** 및 **사용자 편의성 평가 제약**

3. **시스템 구축 제안서 및 요구사항 명세**
   - **정보시스템 구축 사업**의 **화면 설계서, 기능 명세서**
   - **입찰 과정**에서 **구축 업체의 이해도 평가** 및 **기술 제안 검토**
   - **핵심 요구사항 소실**로 **사업 수행 품질 저하** 및 **계약 분쟁 가능성**

4. **내부 직원 교육 및 매뉴얼**
   - **새로운 시스템 도입** 시 **직원 대상 사용법 안내서**
   - **화면별 기능 설명**, **입력 방법 가이드** 등의 **시각적 교육 자료**
   - **UI 구성 정보 부재**로 **교육 효과 급감** 및 **업무 적응 지연**

### 예상되는 원인:
1. **복잡한 HTML 구조 파싱 한계**
   - **HTML5 시맨틱 태그**에 대한 **인식 및 처리 기능 부재**
   - **인라인 CSS 스타일** 무시 및 **시각적 구조 정보 폐기**
   - **블록 레벨과 인라인 레벨이 혼재**된 **복합 구조 파싱 실패**

2. **Form 요소 및 인터랙티브 태그 미지원**
   - **`<input>`, `<textarea>`, `<button>`, `<select>` 등 form 태그** 완전 무시
   - **`<details>`, `<summary>`, `<progress>` 등 HTML5 요소** 인식 부재
   - **웹 표준 태그**와 **한글 문서 서식** 간 **매핑 기능 없음**

3. **레이아웃 구조 변환 한계**
   - **CSS 레이아웃 정보**를 **한글 문서 형식으로 변환**하는 **알고리즘 부재**
   - **시각적 구조**와 **논리적 계층**을 **표현하는 방법 없음**
   - **복잡한 웹 레이아웃**을 **문서 서식으로 대체 표현**하는 **기능 부족**

4. **마크다운 확장 HTML 지원 한계**
   - **기본 마크다운 문법 외 HTML 확장 기능**에 대한 **근본적 지원 부족**
   - **웹 문서 작성 표준**과 **한글 문서 작성 표준** 간 **변환 체계 부재**
   - **현대적인 웹 개발 문서화 요구사항**에 **대응하지 못하는** 구조적 한계

### 심각도:
- 🐛 심각 (Critical)
- 📝 서식 미지원
- **절대 최고 심각도** - 웹사이트 설계안의 핵심 내용 100% 소실
- **공공기관 디지털 서비스 설계, 시스템 구축 프로젝트**의 **가장 중요한 화면 설계 정보 완전 무시**
- **웹 개발 프로젝트 문서의 실질적 가치 완전 상실**
- **설계 의도 전달 및 소통 기능 완전 마비**
- 모든 템플릿에서 동일한 문제로 **대체 방안 전혀 없음**
- **디지털 정부 서비스 설계 문서화 기능 원천 차단**
- **웹 표준 기반 문서 작성 환경에서 완전히 배제**

### 임시 해결 방안:
1. **스크린샷과 텍스트 조합**
   - HTML 구조를 **브라우저에서 렌더링 후 스크린샷** 캡처
   - 마크다운에서는 **이미지 삽입**과 **텍스트 설명** 조합
   ```markdown
   ![포털 메인 화면 구성](portal_main_screenshot.png)
   
   **주요 구성 요소:**
   - 헤더: 사이트 제목 및 베타 버전 표시
   - 네비게이션: 정책제안, 국민토론, 민원신청 메뉴
   ```
   - **시각적 정보는 보존**되지만 **텍스트 편집 불가** 및 **접근성 저하**

2. **마크다운 대체 문법 사용**
   ```markdown
   ## 포털 메인 화면 구성
   
   **📱 화면 레이아웃**
   ```
   ┌─────────────────────────────────────┐
   │ 국민소통포털 (베타 버전)              │
   ├─────────────────────────────────────┤
   │ 정책제안 | 국민토론 | 민원신청       │
   ├─────────────────────────────────────┤
   │ 주요 서비스 안내                     │
   │ ...                                │
   └─────────────────────────────────────┘
   ```
   - **구조는 표현**되지만 **시각적 완성도 대폭 저하**

3. **테이블을 활용한 UI 요소 정리**
   ```markdown
   | UI 요소 | 유형 | 설명 | 속성 |
   |---------|------|------|------|
   | 제목 입력 | input text | 제안 제목 입력 | width: 80%, placeholder: "제안 제목을 입력하세요" |
   | 내용 입력 | textarea | 제안 내용 작성 | rows: 8, 최대 5000자 |
   ```
   - **기능은 설명**되지만 **실제 UI 구조와 시각적 효과 상실**

4. **별도 HTML 파일 첨부**
   - 마크다운에서는 **기본 설명**만 제공
   - **상세한 HTML 구조**는 **별도 파일로 첨부**
   - **문서 일관성 저하** 및 **관리 복잡성 증가**

### 근본적 해결 방안 제안:
1. **HTML5 완전 지원**
   - **모든 HTML5 시맨틱 태그**와 **form 요소** 완전 파싱
   - **인라인 CSS 스타일**을 **한글 문서 서식으로 매핑**
   - **웹 표준 완전 준수**

2. **HWPML 고급 레이아웃 매핑**
   - **복잡한 웹 레이아웃**을 **한글 문서의 고급 서식**으로 변환
   - **표, 텍스트 박스, 도형** 등을 활용한 **시각적 구조 재현**
   - **색상, 테두리, 여백** 등 **CSS 속성을 한글 서식으로 변환**

3. **웹 문서 전용 변환 모드**
   - **HTML이 많이 포함된 문서**를 **자동 감지**
   - **웹사이트 설계안, UI 프로토타입** 등에 **특화된 변환 옵션**
   - **시각적 구조**를 **최대한 보존**하는 **지능형 변환**

4. **하이브리드 웹-문서 표준 구축**
   - **웹 개발 표준**과 **문서 작성 표준**을 **연결하는 브리지**
   - **현대적인 웹 문서화 요구사항**에 **완전 대응**하는 고급 변환기
   - **디지털 정부 시대**에 **적합한 문서 작성 환경** 제공

<br><br> 