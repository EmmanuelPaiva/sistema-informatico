[Setup]
AppName=Sistema Rodler
AppVersion=1.1.2
DefaultDirName={pf}\Rodler
DefaultGroupName=Rodler
OutputDir=installer
OutputBaseFilename=Rodler_Setup_v1_1_2
SetupIconFile=rodlerIcons\app_logo.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\Rodler\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Rodler"; Filename: "{app}\Rodler.exe"
Name: "{commondesktop}\Rodler"; Filename: "{app}\Rodler.exe"
