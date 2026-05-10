# Curve Bookmark Manger

## GitHub Repository
https://github.com/rodrmart1024/3311-FP-ObjectAnnotationTool.git 

## Description
The Curve Bookmark Manager is a Maya tool built for animators working with
rigged characters. When animating, every control on a rig has its own important
moments — a contact pose, an anticipation, a peak — and without a way to track
them per control, those details get lost mid-session.

The tool gives each NURBS curve control its own set of bookmarks, where each
one stores a name, a frame range, and a description, keeping notes organized by
control rather than scattered across a notebook or forgotten entirely. From a
two panel window, you select a control on the left and see its bookmarks on
the right, where a single click jumps the timeline to that moment and selects
the control automatically. Every bookmark saves to a JSON file next to the
Maya scene, so nothing is lost between sessions and the notes follow the file
wherever it goes.