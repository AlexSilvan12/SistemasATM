[Setup]
AppName=AppGestor
AppVersion=1.1.0
DefaultDirName={pf}\AppGestor
DefaultGroupName=AppGestor
OutputBaseFilename=actualización_AppGestor
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableWelcomePage=no
SetupIconFile=C:\Users\Maestra Flor\Gestor-Autorizaciones y Pagos\dist\AppGestor\_internal\Plantillas\IconoATM.ico
AllowNoIcons=yes
PrivilegesRequired=admin


[Files]
Source: "dist\AppGestor\main.exe"; DestDir: "{app}"; Flags: ignoreversion alwaysoverwrite
Source: "dist\AppGestor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs alwaysoverwrite


[Icons]
Name: "{group}\AppGestor"; Filename: "{app}\main.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\AppGestor"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales"

[Run]
Filename: "{app}\main.exe"; Description: "Iniciar AppGestor"; Flags: nowait postinstall skipifsilent

