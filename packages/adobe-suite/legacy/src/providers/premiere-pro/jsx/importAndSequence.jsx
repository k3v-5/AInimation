// ExtendScript for Adobe Premiere Pro
// Imports an array of video files and sequences them consecutively on the timeline.

var filePathsStr = "PATHS_TO_REPLACE"; // Expects a comma-separated string of paths
var sequenceName = "SEQUENCE_NAME_TO_REPLACE";

try {
    var files = filePathsStr.split(",");
    var project = app.project;
    var importResult = project.importFiles(files, true, project.rootItem, false);

    if (importResult) {
        // Create a new sequence based on the first imported item if possible,
        // or just create an empty one (requires a sequence preset in a real prod env,
        // but for this prototype we assume default settings or rely on an existing blank sequence)

        var seq;
        var firstClip = project.rootItem.children[project.rootItem.children.numItems - files.length];

        if (firstClip) {
            // Premiere's API to create a sequence from a clip
            seq = project.createNewSequenceFromClips(sequenceName, [firstClip], project.rootItem);

            // Append the rest
            var videoTrack = seq.videoTracks[0];
            var audioTrack = seq.audioTracks[0];

            var currentTime = firstClip.getOutPoint(); // start at the end of the first clip

            for (var i = 1; i < files.length; i++) {
                var clipToInsert = project.rootItem.children[project.rootItem.children.numItems - files.length + i];
                videoTrack.insertClip(clipToInsert, currentTime.ticks);
                currentTime.seconds += clipToInsert.getOutPoint().seconds; // Increment time
            }

            $.writeln(JSON.stringify({ success: true, sequence_name: seq.name }));
        } else {
            $.writeln(JSON.stringify({ success: false, error: "Clips failed to load into project bin." }));
        }
    } else {
        $.writeln(JSON.stringify({ success: false, error: "Failed to import items." }));
    }
} catch (e) {
    $.writeln(JSON.stringify({ success: false, error: e.toString() }));
}
