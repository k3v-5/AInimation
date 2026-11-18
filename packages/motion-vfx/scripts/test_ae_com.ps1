try {
    $ae = New-Object -ComObject "AfterEffects.Application"
    if ($ae) {
        Write-Host "Connected to After Effects COM!"
        Write-Host "AE Version: $($ae.Version)"
        $res = $ae.DoScript("app.project ? app.project.items.length : 0;")
        Write-Host "Project items length: $res"
    } else {
        Write-Host "Could not create COM object."
    }
} catch {
    Write-Host "COM Error: $_"
}
