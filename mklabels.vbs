' Get banner from command line
Set args = Wscript.Arguments
if args.count = 0 Then
   Wscript.Echo "Missing banner parameter"
   Wscript.Quit
End if
labelBanner = args.Item(0)

Const LabelsTemplateFile = ".\Labels-Template.doc"
Const LabelsPrintFile = ".\Labels-Print.doc"
Const LabelsInputFile = ".\labels-input.txt"
' template file available?
Set objFSO = CreateObject("Scripting.FileSystemObject")
If objFSO.fileExists(LabelsTemplateFile) = False Then
	Wscript.Echo "File does not exist: " + LabelsTemplateFile
    Wscript.Quit
End If
objFSO.CopyFile LabelsTemplateFile, LabelsPrintFile

Dim WordApp
Dim WordDoc
Set WordApp = CreateObject("Word.Application")
WordApp.Visible = True

strPath = Wscript.ScriptFullName
Set objFile = objFSO.GetFile(strPath)
strFolder = objFSO.GetParentFolderName(objFile)
resultsFile = strFolder & LabelsPrintFile

Set objInputFile = objFSO.OpenTextFile(LabelsInputFile,1)
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
