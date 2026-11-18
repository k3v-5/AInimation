// ExtendScript for After Effects
// Imports a given file (PSD, CHPROJ, MP4) and adds it to a new composition.

var fileToImport = "PATH_TO_REPLACE";
var compName = "COMP_NAME_TO_REPLACE";

app.beginUndoGroup("Import and Rig");

try {
    var importOptions = new ImportOptions(new File(fileToImport));
    if (importOptions.canImportAs(ImportAsType.COMP)) {
        importOptions.importAs = ImportAsType.COMP;
    }

    var importedItem = app.project.importFile(importOptions);

    if (importedItem) {
        var comp = app.project.items.addComp(compName, 1920, 1080, 1, 10, 30);
        var layer = comp.layers.add(importedItem);
        // Basic rigging: scale to fit if necessary
        var scale = Math.min(1920 / importedItem.width, 1080 / importedItem.height) * 100;
        layer.property("Scale").setValue([scale, scale]);

        // Write success state to a standard output that our MCP bridge might read if stdout is captured
        $.writeln(JSON.stringify({ success: true, comp_name: comp.name }));
    } else {
        $.writeln(JSON.stringify({ success: false, error: "Failed to import item." }));
    }
} catch (e) {
    $.writeln(JSON.stringify({ success: false, error: e.toString() }));
}

app.endUndoGroup();
