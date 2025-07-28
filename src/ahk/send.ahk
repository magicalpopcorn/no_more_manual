#Requires AutoHotkey v2.0
#NoTrayIcon

SendKey(key) {
    SetTitleMatchMode("2")
    if WinExist("Rise of Kingdoms") {
        WinActivate()
        Send(key)
    }
}

SendKey(A_Args[1])