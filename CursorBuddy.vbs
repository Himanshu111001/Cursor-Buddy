' VBScript launcher to start Animated Cursor Buddy completely silently in the background
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Check if compiled EXE exists in dist
strExe = strDir & "\dist\AnimatedCursorBuddy.exe"
If objFSO.FileExists(strExe) Then
    objShell.Run Chr(34) & strExe & Chr(34), 0, False
Else
    ' Fallback to pythonw.exe
    objShell.CurrentDirectory = strDir
    objShell.Run "pythonw.exe """ & strDir & "\main.py""", 0, False
End If
