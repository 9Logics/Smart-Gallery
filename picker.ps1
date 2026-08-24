Add-Type -AssemblyName System.windows.forms
$f = New-Object System.Windows.Forms.FolderBrowserDialog
$f.Description = 'Select Media Folder'
$form = New-Object System.Windows.Forms.Form
$form.TopMost = $true
$result = $f.ShowDialog($form)
if ($result -eq 'OK') {
    Write-Output $f.SelectedPath
}
