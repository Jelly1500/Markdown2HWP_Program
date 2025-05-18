#define MyAppName "마크다운 HWP 변환기"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "사하구청"
#define MyAppURL "https://www.saha.go.kr/"
#define MyAppExeName "마크다운_HWP_변환기.exe"
#define MyAppAssocName MyAppName + " 파일"
#define MyAppAssocExt ".md"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; 애플리케이션 정보
AppId={{83C94CF0-4DFE-4EAA-9CB2-22200957F7B2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=yes
; 관리자 권한 필요 (키보드 후킹을 위해)
PrivilegesRequiredOverridesAllowed=dialog
OutputBaseFilename=마크다운_HWP_변환기_설치프로그램
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; 한국어 언어 설정
SetupLogging=yes
LanguageDetectionMethod=locale
ShowLanguageDialog=no

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 배포 폴더의 모든 파일을 인스톨러에 포함
Source: "dist\마크다운_HWP_변환기\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 참고: 애플리케이션이 공식적으로 ".md" 확장자를 지원할 경우 다음 줄의 주석을 제거하세요
; Source: "dist\마크다운_HWP_변환기\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; 라이선스 키를 저장할 레지스트리 항목 추가
Root: HKLM; Subkey: "SOFTWARE\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "LicenseKey"; ValueData: "{code:GetLicenseKey}"; Flags: uninsdeletekey; Check: IsAdminInstallMode
Root: HKCU; Subkey: "SOFTWARE\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "LicenseKey"; ValueData: "{code:GetLicenseKey}"; Flags: uninsdeletekey; Check: not IsAdminInstallMode

[Messages]
; 한글 메시지 오버라이드
WelcomeLabel1=마크다운 HWP 변환기 설치 마법사입니다
WelcomeLabel2=이 프로그램은 마크다운 문서를 한글(HWP) 파일 형식으로 변환해주는 도구입니다.%n%n계속하기 전에 다른 프로그램을 모두 종료하는 것이 좋습니다.
FinishedHeadingLabel=마크다운 HWP 변환기 설치 완료
FinishedLabel=마크다운 HWP 변환기가 성공적으로 설치되었습니다.%n%n'마침'을 클릭하여 설치 프로그램을 종료하세요.

[Dirs]
; 출력 폴더에 대한 권한 설정 - 실행 파일과 같은 폴더에 생성
Name: "{app}\convertedDocs"; Permissions: users-full; Flags: uninsneveruninstall
Name: "{app}\new_template"; Permissions: users-full; Flags: uninsneveruninstall

[Code]
var
  LicensePage: TInputQueryWizardPage;
  LicenseKey: String;

// 발급된 라이선스 키 검증 함수
function IsValidLicenseKey(Key: String): Boolean;
var
  i: Integer;
  KeyNoSpace: String;
begin
  Result := False;
  
  // 입력값의 공백 제거 및 대문자 변환
  KeyNoSpace := Uppercase(Trim(Key));
  
  // 1. 마스터키 확인 (대소문자 구분 없음)
  if CompareText(KeyNoSpace, 'TEST-KEY-1234-ABCD') = 0 then
  begin
    Result := True;
    Exit;
  end;
  
  // 2. 사용자에게 발급된 키 확인 (15자리, 문자+숫자 조합)
  if Length(KeyNoSpace) = 15 then
  begin
    // 모든 문자가 영문자 또는 숫자인지 확인
    for i := 1 to Length(KeyNoSpace) do
    begin
      // 영문자(A-Z) 또는 숫자(0-9)가 아니면 유효하지 않음
      if not (((KeyNoSpace[i] >= 'A') and (KeyNoSpace[i] <= 'Z')) or 
              ((KeyNoSpace[i] >= '0') and (KeyNoSpace[i] <= '9')) or
              (KeyNoSpace[i] = '-')) then
        Exit;
    end;
    
    // 여기에 추가적인 검증 로직을 넣을 수 있음
    // 예: 특정 패턴 확인, 체크섬 등
    
    // 간단한 검증을 통과했으므로 유효한 키로 간주
    Result := True;
  end;
end;

procedure InitializeWizard;
begin
  { 라이선스 키 입력 페이지 생성 }
  LicensePage := CreateInputQueryPage(wpWelcome,
    '라이선스 키 입력', 
    '마크다운 HWP 변환기를 사용하기 위한 라이선스 키를 입력해주세요.',
    '라이선스 키가 없으시면 관리자에게 문의해주세요.');
  
  { 입력 필드 추가 }
  LicensePage.Add('라이선스 키:', False);
  
  { 기본값 설정 - 더 나은 사용자 경험을 위해 테스트 키를 미리 입력해둘 수 있음 }
  LicensePage.Values[0] := '';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  { 라이선스 키 페이지인 경우 키 검증 }
  if CurPageID = LicensePage.ID then
  begin
    LicenseKey := Trim(LicensePage.Values[0]);
    
    { 라이선스 키 검증 }
    if not IsValidLicenseKey(LicenseKey) then
    begin
      MsgBox('올바른 라이선스 키를 입력해주세요.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function GetLicenseKey(Param: String): String;
begin
  Result := LicenseKey;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  
  { 최종 검증 - 이 시점에서 라이선스 키가 여전히 유효한지 확인 }
  if not IsValidLicenseKey(LicenseKey) then
  begin
    Result := '유효하지 않은 라이선스 키입니다. 설치를 중단합니다.';
  end;
end; 