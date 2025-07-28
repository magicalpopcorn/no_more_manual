#Requires AutoHotkey v2.0
#NoTrayIcon

SendText(text) {
    for char in StrSplit(text) {
        Send char
        Sleep Random(20, 40)
    }
}

SendText(A_Args[1])