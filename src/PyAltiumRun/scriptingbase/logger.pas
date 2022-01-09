
Const
  LogFilePath = '{LogFilePath}';

Procedure log_str(Const data : String);
Var
  logFile : TextFile;
  currentTime : TDataTime;
  toWrite: String;
Begin
  AssignFile(logFile, LogFilePath);
  Append(logFile);
  currentTime := Now;
  toWrite := '[' + FormatDateTime('dd/mm/yy hh:nn:ss.zzz', currentTime) + ']: ' + data;
  WriteLn(logFile, toWrite);
  CloseFile(logFile);
End;

Procedure log_frm(Const frm : String; Const data : array);
Var
  toWrite: String;
Begin
  toWrite := Format(frm, data);
  log_str(toWrite);
End;