Sub FeedMarkedMediationForms_Click()
    Dim wsDB As Worksheet
    Dim wsMed1 As Worksheet, wsMed2 As Worksheet, wsMed3 As Worksheet, wsEnvelope As Worksheet
    Dim wsStatementOptions As Worksheet
    Dim wsMed4 As Worksheet, wsMed5 As Worksheet, wsMed6 As Worksheet
    Dim wsMed8 As Worksheet, wsMed9 As Worksheet
    Dim formSheets As Collection
    Dim item As Variant
    Dim lastRow As Long, i As Long
    Dim printCol As Long
    Dim printedCount As Long
    Dim formName As String
    Dim formSheet As Worksheet
    Dim printFlag As String
    Dim pageCount As Integer

    ' === Define Source and Form Sheets ===
    Set wsDB = ThisWorkbook.Sheets("DATABASE")
    Set wsMed1 = ThisWorkbook.Sheets("STATEMENT OF ACCOUNT")
    Set wsMed2 = ThisWorkbook.Sheets("Mediation Form 2")
    Set wsMed3 = ThisWorkbook.Sheets("Mediation Form 3")
    Set wsMed3a = ThisWorkbook.Sheets("Mediation Form 3.a")
    Set wsMed4 = ThisWorkbook.Sheets("Mediation Form 4")
    Set wsMed5 = ThisWorkbook.Sheets("Mediation Form 5")
    Set wsMed6 = ThisWorkbook.Sheets("Mediation Form 6")
    Set wsMed7 = ThisWorkbook.Sheets("Mediation Form 7")
    Set wsMed8 = ThisWorkbook.Sheets("Mediation Form 8")
    Set wsMed9 = ThisWorkbook.Sheets("Mediation Form 9")
    Set wsMed10 = ThisWorkbook.Sheets("Mediation Form 10")
    Set wsEnvelope = ThisWorkbook.Sheets("ENVELOPE")
    Set wsStatementOptions = ThisWorkbook.Sheets("Mediation Statement Options")

    ' === Define Form Sheet Collection ===
    Set formSheets = New Collection
    formSheets.Add Array("STATEMENT OF ACCOUNT", wsMed1, "STATEMENT")
    formSheets.Add Array("Mediation Form 2", wsMed2, "MED2")
    formSheets.Add Array("Mediation Form 3", wsMed3, "MED3")
    formSheets.Add Array("Mediation Form 3.a", wsMed3, "MED3a")
    formSheets.Add Array("Mediation Form 4", wsMed4, "MED4")
    formSheets.Add Array("Mediation Form 5", wsMed5, "MED5")
    formSheets.Add Array("Mediation Form 6", wsMed6, "MED6")
    formSheets.Add Array("Mediation Form 7", wsMed6, "MED7")
    formSheets.Add Array("Mediation Form 8", wsMed8, "MED8")
    formSheets.Add Array("Mediation Form 9", wsMed9, "MED9")
    formSheets.Add Array("Mediation Form 10", wsMed10, "MED10")
    formSheets.Add Array("ENVELOPE", wsEnvelope, "ENVELOPE")
    formSheets.Add Array("DATABASE", wsDB, "DATABASE")
    formSheets.Add Array("Mediation Statement Options", wsStatementOptions, "STATEMENT_OPTIONS")

    ' === Setup PRINT Column and Row Range ===
    printCol = 38 ' Column AL (PRINT column as specified)
    lastRow = wsDB.Cells(wsDB.Rows.Count, printCol).End(xlUp).Row
    printedCount = 0

    ' === Loop Through Rows Marked for Printing ===
    For i = 8 To lastRow
        printFlag = UCase(Trim(wsDB.Cells(i, printCol).Value))
        
        If printFlag = "PRINT ALL MED" Or printFlag = "PRINT ALL LETTER" Or printFlag = "MED2" Or _
            printFlag = "MED3" Or printFlag = "MED3A" Or printFlag = "MED4" Or printFlag = "MED5" Or _
            printFlag = "MED6" Or printFlag = "MED7" Or printFlag = "MED8" Or _
            printFlag = "MED9" Or printFlag = "MED10" Or _
            printFlag = "STATEMENT" Or printFlag = "STATEMENT 1" Or _
            printFlag = "ENVELOPE" Or printFlag = "DATABASE" Then

            ' === Feed Data to Each Form Sheet ===
            For Each item In formSheets
                formName = item(0)
                Set formSheet = item(1)
                Call FeedForm(wsDB, formSheet, formName, i)
            Next item

            ' === Print Forms Based on Print Flag ===
            
            Select Case printFlag
            
                Case "PRINT ALL MED"
                    wsMed6.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    wsStatementOptions.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    wsMed1.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    wsMed9.PrintOut Copies:=4, Collate:=True, IgnorePrintAreas:=False
                    wsMed8.PrintOut Copies:=4, Collate:=True, IgnorePrintAreas:=False
                    wsMed5.PrintOut Copies:=4, Collate:=True, IgnorePrintAreas:=False
                    wsMed4.PrintOut Copies:=4, Collate:=True, IgnorePrintAreas:=False
                
                Case "PRINT ALL LETTER"
                    'wsMed2.PrintOut Copies:=4, Collate:=True, IgnorePrintAreas:=False
                    wsMed3a.PrintOut Copies:=5, Collate:=True, IgnorePrintAreas:=False
                                       
                Case "MED2"
                    wsMed2.PrintOut Copies:=4, Collate:=True, IgnorePrintAreas:=False
                    
                Case "MED3"
                    wsMed3.PrintOut Copies:=5, Collate:=True, IgnorePrintAreas:=False
                    
                Case "MED4"
                    wsMed4.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    
                Case "MED5"
                    wsMed5.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    
                Case "MED6"
                    wsMed6.PrintOut Copies:=13, Collate:=True, IgnorePrintAreas:=False
                    
                    
                Case "MED7"
                    wsMed7.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    
                Case "MED8"
                    wsMed8.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    
                Case "MED9"
                    wsMed9.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    
                Case "MED10"
                    wsMed10.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    
                Case "ENVELOPE"
                    wsEnvelope.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    
                Case "STATEMENT"
                    wsMed1.PrintOut Copies:=1, Collate:=True, IgnorePrintAreas:=False
                    
                Case "STATEMENT 1"
                    wsStatementOptions.PrintOut From:=1, To:=1, Copies:=1, Collate:=True, IgnorePrintAreas:=False
                                        
            End Select

            ' === Clear PRINT Flag from DATABASE only ===
            wsDB.Cells(i, printCol).ClearContents
            printedCount = printedCount + 1
        End If
    Next i

    ' Return to DATABASE sheet when done
    wsDB.Activate
    
    MsgBox printedCount & " case(s) processed.", vbInformation
End Sub

' ===== UPDATED FEEDFORM SUBROUTINE =====
Sub FeedForm(wsDB As Worksheet, wsForm As Worksheet, formName As String, rowNum As Long)
    On Error GoTo FeedFormError
    
    Select Case formName
        Case "STATEMENT OF ACCOUNT"
            With wsForm
                ' Updated mapping with column letters as specified
                .Range("C1").Value = wsDB.Cells(rowNum, 2).Value  ' B. MEMBER-PATRON'S
                .Range("C3").Value = wsDB.Cells(rowNum, 3).Value  ' C. BILLING ADDRESS
                .Range("C5").Value = wsDB.Cells(rowNum, 11).Value ' K. KIND OF LOAN
                .Range("J1").Value = wsDB.Cells(rowNum, 12).Value ' L. LOAN GRANTED|PRINCIPAL
                .Range("F1").Value = wsDB.Cells(rowNum, 13).Value ' M. DATE GRANTED
                .Range("F3").Value = wsDB.Cells(rowNum, 14).Value ' N. MATURITY DATE
                .Range("I9").Value = wsDB.Cells(rowNum, 15).Value ' O. END OF CALCULATION
                .Range("H1").Value = wsDB.Cells(rowNum, 10).Value ' J. VOUCHER NUMBER
                .Range("C7").Value = wsDB.Cells(rowNum, 12).Value ' L. PRINCIPAL
                .Range("C8").Value = wsDB.Cells(rowNum, 18).Value ' R. BALANCE
                .Range("C9").Value = wsDB.Cells(rowNum, 17).Value ' Q. AMORTIZATION
                .Range("G16").Value = wsDB.Cells(rowNum, 21).Value ' U. LESS TOTAL PDI
                .Range("H16").Value = wsDB.Cells(rowNum, 22).Value ' V. LESS TOTAL PEN
                .Range("I79").Value = wsDB.Cells(rowNum, 37).Value ' V. CBU
            End With

        Case "Mediation Form 2"
            With wsForm
                ' Updated mapping with column letters as specified
                .Range("E10").Value = wsDB.Cells(rowNum, 10).Value ' J. VOUCHER NUMBER
                .Range("H10").Value = wsDB.Cells(rowNum, 1).Value  ' A. CASE NO.
                
                ' Member-Patron's Name in merged cells A:E, row 24
                .Range("A24:E24").Value = wsDB.Cells(rowNum, 2).Value ' B. MEMBER-PATRON'S
                
                .Range("F24").Value = wsDB.Cells(rowNum, 4).Value  ' D. Age
                .Range("G24").Value = wsDB.Cells(rowNum, 5).Value  ' E. Gender
                .Range("H24").Value = wsDB.Cells(rowNum, 6).Value  ' F. Civil Status
                
                ' Address in merged cells A:E, row 26
                .Range("A26:E26").Value = wsDB.Cells(rowNum, 3).Value ' C. BILLING ADDRESS
                
                ' Livelihood/Occupation in merged cells F:H, row 26
                .Range("F26:H26").Value = wsDB.Cells(rowNum, 7).Value ' G. LIVELIHOOD/OCCUPATION
                
                ' Contact Number in merged cells F:H, row 30
                .Range("F30:H30").Value = wsDB.Cells(rowNum, 8).Value ' H. CONTACT NUMBER
                
                ' Email/Social Media Address in merged cells F:H, row 32
                .Range("F32:H32").Value = wsDB.Cells(rowNum, 9).Value ' I. EMAIL/SOCIAL MEDIA ADDRESS
            End With

        Case "Mediation Form 3"
            With wsForm
                ' Updated mapping with column letters as specified
                .Range("D9").Value = wsDB.Cells(rowNum, 10).Value  ' J. VOUCHER NUMBER
                .Range("G9").Value = wsDB.Cells(rowNum, 1).Value   ' A. CASE NO.
                
                ' Member-Patron's Name in merged cells B:G, row 11
                .Range("B11:G11").Value = wsDB.Cells(rowNum, 2).Value  ' B. MEMBER-PATRON'S
                
                ' Address in merged cells B:G, row 12
                .Range("B12:G12").Value = wsDB.Cells(rowNum, 3).Value  ' C. BILLING ADDRESS
                .Range("I5").Value = wsDB.Cells(rowNum, 24).Value  ' C. BILLING ADDRESS
                
                
            End With
            
        Case "Mediation Form 6"
            With wsForm
                ' Map DATABASE columns to Mediation Form 6 cells
                .Range("J8").Value = wsDB.Cells(rowNum, 25).Value  ' Y column
                .Range("J9").Value = wsDB.Cells(rowNum, 26).Value  ' Z column
                .Range("J5").Value = wsDB.Cells(rowNum, 27).Value   ' AA column
                .Range("K5").Value = wsDB.Cells(rowNum, 28).Value   ' AB column
                .Range("J1").Value = wsDB.Cells(rowNum, 29).Value   ' AC column
                .Range("J2").Value = wsDB.Cells(rowNum, 30).Value   ' AD column
                .Range("J3").Value = wsDB.Cells(rowNum, 31).Value   ' AE column
                .Range("J4").Value = wsDB.Cells(rowNum, 32).Value   ' AF column
                .Range("K4").Value = wsDB.Cells(rowNum, 33).Value   ' AG column
                .Range("J6").Value = wsDB.Cells(rowNum, 34).Value   ' AH column
                .Range("J7").Value = wsDB.Cells(rowNum, 35).Value   ' AI column
                
            End With
            
        Case "ENVELOPE"
            With wsForm
                ' Member-Patron's Name in merged cells D:J, rows 8-9
                .Range("D19").Value = wsDB.Cells(rowNum, 2).Value  ' B. MEMBER-PATRON'S
                
                ' Address in merged cells D:J, row 10
                .Range("D21").Value = wsDB.Cells(rowNum, 3).Value  ' C. BILLING ADDRESS
            End With
            
        ' Add cases for other forms as needed
    End Select
    
    Exit Sub
    
FeedFormError:
    MsgBox "Error " & Err.Number & ": " & Err.Description & " in FeedForm for " & formName, vbCritical
End Sub
    


