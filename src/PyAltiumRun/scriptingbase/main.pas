
Const
  ProjectFilePath = '{ProjectFilePath}';
  DataFolder = '{DataFolder}';

Procedure SCRIPTING_SYSTEM_MAIN;
Var
  Document: IDocument;
Begin
  write_str_to_log('Starting script');
  If AnsiCompareStr(ProjectFilePath, 'None') then
  Begin
    write_str_to_log('Opening project: ' + ProjectFilePath);
    Document := Client.OpenDocument('PcbProject', ProjectFilePath);
    Client.ShowDocument(Document);
  End;
  {FunctionName}({FunctionParameters});
  DeleteFile(DataFolder + 'running')
End;