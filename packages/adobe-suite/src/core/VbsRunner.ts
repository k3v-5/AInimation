import fs from 'fs';
import path from 'path';
import os from 'os';
import { execFile } from 'child_process';
import util from 'util';

const execFileAsync = util.promisify(execFile);

export class VbsRunner {
  /**
   * Executes an ExtendScript (.jsx) file in Adobe Illustrator via the Windows COM / VBScript bridge.
   */
  public static async runIllustratorScript(
    scriptPathOrContent: string,
    isContent: boolean = false,
    timeoutMs: number = 60000
  ): Promise<{ success: boolean; output?: string; error?: string }> {
    const tempDir = os.tmpdir();
    const timestamp = Date.now();

    let finalJsxPath = scriptPathOrContent;
    let tempJsxCreated = false;

    if (isContent) {
      finalJsxPath = path.join(tempDir, `ai_script_${timestamp}.jsx`);
      fs.writeFileSync(finalJsxPath, scriptPathOrContent, 'utf8');
      tempJsxCreated = true;
    } else {
      finalJsxPath = path.resolve(scriptPathOrContent);
      if (!fs.existsSync(finalJsxPath)) {
        return { success: false, error: `ExtendScript file does not exist: ${finalJsxPath}` };
      }
    }

    // Windows backslash normalization for VBScript string literal
    const vbsJsxPath = finalJsxPath.replace(/\\/g, '\\\\');

    const vbsContent = `
On Error Resume Next
Set app = CreateObject("Illustrator.Application")
If Err.Number <> 0 Then
    WScript.StdErr.WriteLine "COM_ERROR: Unable to bind to Illustrator.Application. Ensure Illustrator is installed and licensed. " & Err.Description
    WScript.Quit 1
End If

Dim res
res = app.DoJavaScriptFile("${vbsJsxPath}")
If Err.Number <> 0 Then
    WScript.StdErr.WriteLine "SCRIPT_ERROR: " & Err.Description
    WScript.Quit 2
End If

If Not IsEmpty(res) And Not IsNull(res) Then
    WScript.StdOut.WriteLine res
End If
`;

    const vbsPath = path.join(tempDir, `ai_bridge_${timestamp}.vbs`);
    fs.writeFileSync(vbsPath, vbsContent, 'utf8');

    try {
      const { stdout, stderr } = await execFileAsync(
        'cscript',
        ['//nologo', `//T:${Math.ceil(timeoutMs / 1000)}`, vbsPath],
        { encoding: 'utf8', timeout: timeoutMs }
      );

      if (stderr && stderr.trim().length > 0) {
        return { success: false, error: stderr.trim() };
      }

      return { success: true, output: stdout.trim() };
    } catch (err: any) {
      return {
        success: false,
        error: err.stderr || err.message || 'VBScript execution failed'
      };
    } finally {
      // Cleanup temp files
      try {
        if (fs.existsSync(vbsPath)) fs.unlinkSync(vbsPath);
        if (tempJsxCreated && fs.existsSync(finalJsxPath)) fs.unlinkSync(finalJsxPath);
      } catch {
        // ignore cleanup errors
      }
    }
  }
}
