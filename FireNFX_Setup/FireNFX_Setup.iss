
[Setup]
AppName=FireNFX Script
AppVersion=0.2-pre
AppId={{4BED38F2-2CE5-447D-84FB-1E48CBD9912E}
WizardStyle=modern
UsePreviousSetupType=False
UsePreviousTasks=False
UninstallDisplayName=FireNFX Script
DefaultDirName={code:FLSharedFolder}\FL Studio\Settings\Hardware\FireNFX\
UsePreviousAppDir=False
AllowUNCPath=False
AppendDefaultDirName=False
OutputBaseFilename=FireNFX_Installer

[Files]
Source: "..\device_Fire.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\fireNFX.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\gt.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\harmonicScales.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\midi.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\nfxChords.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\nfxFire.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\nfxFireColors.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\nfxFirePadDefs.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\utils.py"; DestDir: "{app}"; Flags: ignoreversion; Components: InstallScripts
Source: "..\nfxFire_Template.zip"; DestDir: "{code:FLSharedFolder}\FL Studio\Projects\Templates\FireNFX"; Flags: ignoreversion; Components: InstallTemplates
Source: "..\nfxFire_Template_2.zip"; DestDir: "{code:FLSharedFolder}\FL Studio\Projects\Templates\FireNFX"; Flags: ignoreversion; Components: InstallTemplates

[Components]
Name: "InstallScripts"; Description: "Install the FireNFX Scripts"; Types: compact custom full; Flags: checkablealone
Name: "InstallTemplates"; Description: "Install Example FireNFX Templates"; Types: custom full; Flags: checkablealone

[Tasks]
Name: "StartFireNFXTemplate"; Description: "Start FL Studio with the demo FireNFX Template"
Name: "CopyLatestVersion"; Description: "Copies the latest version downloaded from github to a folder"; Components: InstallScripts

[Messages]
WizardSelectDir=Select your FL Studio User Data Folder
SharedFileLocationLabel=FL Studio User Data:

[Run]
Filename: "{code:FLExecutable}"; Parameters: "{code:FLSharedFolder}\FL Studio\Projects\Templates\FireNFX\nfxFire_Template_2.zip"; Flags: nowait postinstall runascurrentuser; Description: "Start FL Studio with the Demo FireNFX Template"; Components: InstallTemplates; Tasks: StartFireNFXTemplate

[Code]
function FLSharedFolder(Param: String): String;
var
  V: string;
begin
  V := '';
  if RegQueryStringValue(HKCU, 'SOFTWARE\Image-Line\Shared\Paths', 'Shared Data', V) then
    Result := V
  else if RegQueryStringValue(HKLM, 'SOFTWARE\Image-Line\Shared\Paths', 'Shared Data', V) then
    Result := V;
end;

function FLExecutable(Param: String): String;
var
  V: string;
begin
  V := '';
  if RegQueryStringValue(HKCU, 'SOFTWARE\Image-Line\Shared\Paths', 'FL Studio', V) then
    Result := V
  else if RegQueryStringValue(HKLM, 'SOFTWARE\Image-Line\Shared\Paths', 'FL Studio', V) then
    Result := V;
end;

function OnDownloadProgress(const Url, Filename: string; const Progress, ProgressMax: Int64): Boolean;
begin
  if ProgressMax <> 0 then
    Log(Format('  %d of %d bytes done.', [Progress, ProgressMax]))
  else
    Log(Format('  %d bytes done.', [Progress]));
  Result := True;
end;

function InitializeSetup: Boolean;
begin
  try
    DownloadTemporaryFile('https://github.com/nfxbeats/FireNFX/archive/refs/heads/master.zip', 'nfxFire.zip', '', @OnDownloadProgress);
    Result := True;
    MsgBox('Hello. ' + ExpandConstant('{tmp}'), mbInformation, MB_OK);
  except
    Log(GetExceptionMessage);
    Result := False;
  end;
end;


