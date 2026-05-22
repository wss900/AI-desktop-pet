' 无命令行窗口启动桌宠（推荐双击此文件）
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
pyw = dir & "\.venv\Scripts\pythonw.exe"
If Not fso.FileExists(pyw) Then
  pyw = dir & "\.venv\Scripts\python.exe"
End If
CreateObject("WScript.Shell").Run """" & pyw & """ """ & dir & "\main.py""", 0, False
