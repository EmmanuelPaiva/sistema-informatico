[Setup]
AppName=Sistema Rodler
AppVersion=1.0.0
DefaultDirName={pf}\Rodler
DefaultGroupName=Rodler
OutputDir=installer
OutputBaseFilename=Rodler_Setup
SetupIconFile=rodlerIcons\app_logo.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\Rodler\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Rodler"; Filename: "{app}\Rodler.exe"
Name: "{commondesktop}\Rodler"; Filename: "{app}\Rodler.exe"
