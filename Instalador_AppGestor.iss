[Setup]
AppName=AppGestor
AppVersion=1.0.3
DefaultDirName={pf}\AppGestor
DefaultGroupName=AppGestor
OutputBaseFilename=Instalador_AppGestor
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableWelcomePage=no
SetupIconFile=C:\Users\Maestra Flor\Gestor-Autorizaciones y Pagos\dist\AppGestor\_internal\Plantillas\IconoATM.ico

[Files]
Source: "dist\AppGestor\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "Plantillas\*"; DestDir: "{app}\Plantillas"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Firmas\*"; DestDir: "{app}\Firmas"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "autorizaciones.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "database.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "gastos_contrato.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "gerente.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "login.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "main_menu.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "proveedores.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "solicitudes.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "usuarios.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "utils.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "upgrade.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "version_local.txt"; DestDir: "{app}"; Flags: ignoreversion


[Icons]
Name: "{group}\AppGestor"; Filename: "{app}\main.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\AppGestor"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales"

[Run]
Filename: "{app}\main.exe"; Description: "Iniciar AppGestor"; Flags: nowait postinstall skipifsilent