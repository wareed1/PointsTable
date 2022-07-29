Dim WordApp
Dim WordDoc
Set WordApp = CreateObject("Word.Application")
WordApp.Visible = True
Set objFSO = CreateObject("Scripting.FileSystemObject")

objFSO.CopyFile ".\Labels-Template.doc", ".\Labels-Print.doc"

' Assumed that if you are generating labels, its for this
' year's swim meet.  Get the year and form the banner for
' each label.
thisYear = Year(Date)
labelBanner = "Kemptville Bluefins Swim Meet " & thisYear

If objFSO.fileExists(".\Labels-Template.doc") = False Then
	MsgBox "File Does Not Exist"
End If

strPath = Wscript.ScriptFullName
Set objFile = objFSO.GetFile(strPath)
strFolder = objFSO.GetParentFolderName(objFile)
resultsFile = strFolder & ".\Labels-Print.doc"

Set objInputFile = objFSO.OpenTextFile(".\labels-input.txt",1)
Set WordDoc = WordApp.Documents.Open(resultsFile)

curColumn = 1
curRow = 1
Do until objInputFile.AtEndofStream
	strcomputer = objInputFile.ReadLine
	Set objSelection = WordApp.Selection
	'Set myCell = objSelection.Tables(1).Columns(curColumn).Select
	objSelection.Tables(1).Cell(curRow, curColumn).Select
	strarray = split(strcomputer,",")
	'Only print labels for swimmers that have results
	If UBound(strarray) >= 2 Then
		If strarray(2) <> "" Then
			objSelection.TypeText labelBanner & VbCrLf
			For i = LBound(strarray) To UBound(strarray) 
				objSelection.TypeText strarray(i)
				If i <> Ubound(strarray) Then
					objSelection.TypeText VbCrLf
				End If
			Next 
			If curColumn = 1 then
			   curColumn = 3
			Elseif curColumn = 3 then
			   curColumn = 1
			   curRow = curRow + 1
			End If
		End If
	End If
Loop

objInputFile.Close
WordDoc.SaveAs (".\labels")
