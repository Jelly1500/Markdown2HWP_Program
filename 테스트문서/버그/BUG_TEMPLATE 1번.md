---
name: 버그 리포트 템플릿
about: 버그 발생 시 사용하는 템플릿입니다
title: "버그 리포트: &lt;br&gt; "
labels: "🐞 BUG"
assignees: 
---

# 버그 리포트

## 어떤 버그인가요?
> markdown 문법 중 ``` 으로 작성되는 코드블럭 문법내부의 글들이 변환시 삭제되는 문제가 있음.

<br><br>

## 어떤 상황에서 겪으셨나요?
1. 실행 환경: 
   - OS: Windows 11
   - Python: 3.12

2. 테스트를 수행한 마크다운 문서:
```
```json
{
  "frontend": "JSP / jQuery",
  "backend": "Spring MVC",
  "database": "Oracle 11g"
}```
```
   

3. 사용했던 템플릿: 
   - template_ex_01.hml
   - template_ex_02.hml  
   - template_ex_03.hml
   - template_ex_04.hml

<br><br>

## 어떤 과정에서 버그가 발생하였나요?
> 마크다운 문법에 코드블럭이 포함되면 내부의 글이 변환시 삭제 됨.
