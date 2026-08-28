; Soulkeep installer — installs the app per-user and places the in-game addon
; into the World of Warcraft folder (auto-detected, or browsed to by the user).
; Compile: ISCC.exe /DAppVer=x.y.z installer\soulkeep.iss

#ifndef AppVer
  #define AppVer "0.0.0"
#endif

[Setup]
AppId={{8E2B7B62-5OUL-4EEP-0000-C0FFEE5EEL5A}
AppName=Soulkeep
AppVersion={#AppVer}
AppPublisher=Oblivion & Ser Claude
DefaultDirName={localappdata}\Soulkeep
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=SoulkeepSetup
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\Soulkeep.exe
WizardStyle=modern
DisableWelcomePage=no
Compression=lzma2
SolidCompression=yes

[Files]
Source: "..\dist\Soulkeep.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\addon\WoWRosterExport\*"; DestDir: "{code:AddonTargetDir}\WoWRosterExport"; Flags: ignoreversion recursesubdirs; Check: AddonChosen

[Icons]
Name: "{userdesktop}\Soulkeep"; Filename: "{app}\Soulkeep.exe"
Name: "{userprograms}\Soulkeep"; Filename: "{app}\Soulkeep.exe"

[Run]
Filename: "{app}\Soulkeep.exe"; Description: "Launch Soulkeep"; Flags: nowait postinstall skipifsilent

[Code]
var
  WoWPage: TInputDirWizardPage;

function ResolveAddons(Dir: String): String;
begin
  Result := '';
  Dir := Trim(Dir);
  if Dir = '' then exit;
  { they picked the WoW root (contains _retail_) }
  if DirExists(Dir + '\_retail_\Interface') or DirExists(Dir + '\_retail_') then
    Result := Dir + '\_retail_\Interface\AddOns'
  { they picked _retail_ itself }
  else if DirExists(Dir + '\Interface') or FileExists(Dir + '\Wow.exe') then
    Result := Dir + '\Interface\AddOns';
end;

function TryAutodetect(): String;
var
  reg: String;
  cands: TArrayOfString;
  i: Integer;
begin
  Result := '';
  if RegQueryStringValue(HKLM32, 'SOFTWARE\Blizzard Entertainment\World of Warcraft', 'InstallPath', reg) then
    if ResolveAddons(reg) <> '' then begin Result := reg; exit; end;
  SetArrayLength(cands, 8);
  cands[0] := 'C:\Program Files (x86)\World of Warcraft';
  cands[1] := 'C:\World of Warcraft';
  cands[2] := 'D:\Games\World of Warcraft';
  cands[3] := 'D:\World of Warcraft';
  cands[4] := 'E:\Games\World of Warcraft';
  cands[5] := 'E:\World of Warcraft';
  cands[6] := 'C:\Games\World of Warcraft';
  cands[7] := 'D:\SteamLibrary\World of Warcraft';
  for i := 0 to GetArrayLength(cands) - 1 do
    if ResolveAddons(cands[i]) <> '' then begin Result := cands[i]; exit; end;
end;

procedure InitializeWizard();
var
  seed: String;
begin
  WoWPage := CreateInputDirPage(wpSelectDir,
    'World of Warcraft folder',
    'Soulkeep''s in-game companion addon exports gold, vault, bags and /played.',
    'Point at your World of Warcraft folder (the one containing _retail_) and the addon installs itself. Leave blank to skip — you can install it later from Soulkeep''s Settings.',
    False, '');
  WoWPage.Add('');
  seed := ExpandConstant('{param:WOWDIR|}');
  if seed = '' then seed := TryAutodetect();
  WoWPage.Values[0] := seed;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  v: String;
begin
  Result := True;
  if (WoWPage <> nil) and (CurPageID = WoWPage.ID) then begin
    v := Trim(WoWPage.Values[0]);
    if (v <> '') and (ResolveAddons(v) = '') then begin
      MsgBox('That does not look like a World of Warcraft folder — it should contain _retail_\Interface (or be the _retail_ folder itself).'#13#10#13#10'Fix the path, or leave it blank to skip the addon.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function CurrentWoWDir(): String;
begin
  Result := ExpandConstant('{param:WOWDIR|}');
  if (WoWPage <> nil) and (Trim(WoWPage.Values[0]) <> '') then
    Result := Trim(WoWPage.Values[0]);
end;

function AddonChosen(): Boolean;
begin
  Result := ResolveAddons(CurrentWoWDir()) <> '';
end;

function AddonTargetDir(Param: String): String;
begin
  Result := ResolveAddons(CurrentWoWDir());
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ec: Integer;
begin
  if CurStep = ssPostInstall then begin
    if (not FileExists(ExpandConstant('{app}\bnet.env'))) and (not WizardSilent) then begin
      MsgBox('One key remains: copy the bnet.env file the Highlord gave you into this folder, next to Soulkeep.exe:'#13#10#13#10 + ExpandConstant('{app}') + #13#10#13#10'The folder opens for you now.', mbInformation, MB_OK);
      ShellExec('open', ExpandConstant('{app}'), '', '', SW_SHOW, ewNoWait, ec);
    end;
  end;
end;
