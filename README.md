![tumbnail](imgs/tumb.jpg)

This is a couple of blender addons along with a guide on how to import Aion .geo files into the blender, create navmeshes and export them in .nav format compatible with [ARP](https://github.com/Yoress/ARP/tree/master) and [Aion 5.8 Community Project](https://github.com/MATTYOneInc/AionEncomBase).

Few things to note:

1. I'm not a programmer - don't expect the code to be perfect in any way.

2. The guide is pretty thorough and I've tried to mention every key combination and action I do. The actual process is pretty fast once you learn it.

3. Blender 4.3.0 is used. Compatibility with other versions is not guaranteed.

4. Only monono2 geodata is supported.

5. Before making navmeshes, check out [5.8 navmesh pack](https://drive.google.com/file/d/1ulkx0TwdDZnFZL5ildkVFtD1WQ3jGA7p/view?usp=sharing) and [other versions](https://drive.google.com/file/d/1sL8kpHc3-oO75roO4dmTgLCJi_7obmuL/view?usp=sharing) to see if navmeshes for these maps were already built. Nav files themselves are not version dependent - 5.8 navmeshes will work on lower versions as long as the maps themselves didn't change between versions.

### I. Importing .geo into blender:
1. Start blender, remove everything from the scene ("A" + "X").

2. Install io_import_aion_geo_mono2.py like any blender addon (Edit -> Preferences -> Add-ons -> Install from disk -> select the .py file).

3. Once the addon is installed, you can load geo with File -> Import -> Aion .geo map (.geo).

Importing should take from a couple of seconds to a minute depending on the map complexity and your cpu.

Many aion maps are large and don't display well inside blender with default settings. To fix that, move your cursor into the 3D viewport, press "N", go to "View" tab and change "Clip Start" and "End" to 1m and 7000m respectively.

### II. Building the navmesh:
Sadly, we can't build navmeshes for large maps within blender itself. For that we will need some external tools and extra steps.

#### For small maps:

1. Install [RecastBlenderAddon](https://github.com/przemir/RecastBlenderAddon). Github page for it has installation instructions.

2. Select all objects you want to have navmesh built for (or the entire scene by pressing "A")

Go to Scene properties -> recast navmesh.

3. Play with the settings and press "Build Navigation Mesh".

This will create and select a navmesh. If it didn't, then your map is probably too large and you will have to follow the alternate approach. You can also try to build several smaller navmeshes by selecting only parts of the level. Those navmeshes can then be combined with "Ctrl + J".

4. With navmesh selected, press "Tab" to switch to edit mode. There, select everything with "A", then press "M -> By distance". Repeat this action until you see "Removed 0 vertice(s)".

(optional) To make the navmesh more optimized, you can apply a "Decimate" modifier with whatever ratio you want. For me ratio of 0.5 works pretty well. After that, you have to repeat the previous step of pressing "M -> By distance" until you see 0 removed.

(optional) You can also remove inaccessible parts of the navmesh by switching to edit mode and selecting whatever polygons you want to remove, shortcut "L" works well here, selecting all connected polygons at your mouse cursor. Selected polygons can be deleted by pressing "X".

Done! You can now go to the “Exporting the navmesh” step.

#### For large maps:

This is a (still) DUMB approach. If you have a better way - feel free to share.

You will need:

A lot of RAM or swap space for certain large maps - over 24GB.

recast4j to build tiled navmeshes. You can either build the specific recast-demo from [source](https://github.com/234523413432634/recast4j), or download a [prebuilt one](https://drive.google.com/file/d/1b5SCkmNJGnylvI_XI1pBsoAKOdyPAvoN/view?usp=sharing).

1. While inside blender, export our scene as .obj (File -> Export -> Wavefront(.obj) -> Export Wavefront OBJ).

2. Launch recast-demo with Start.bat.

3. Load the exported .obj into the recast-demo. On the right panel, enable the tiled option, set the tile size to 3600 - 4000 range. The higher the value, the faster the process will be, but increasing the tile size may cause recast-demo to throw an exception. Most large maps can be generated with 3x3 tiles, some colossal maps may require 4x4 or even 5x5. Now generate the navmesh with the "build" button. Process will take several minutes. If after generation there is a navmesh over the entire map and the console has no exceptions, Then we are safe to export the navmesh.

4. Once all tiles are built, press "Save Nav Mesh...". The resulting .obj file can be exported into the blender for cleaninng, fixing and exporting in the .nav format.

5. After loading the navmesh into the blender and selecting it, press "Tab" to switch to edit mode. There, select everything with "A", then press "M -> By distance". Repeat this action until you see "Removed 0 vertice(s)". You can also use "Shift + R'' to repeat the last action to make this process a bit faster.

(optional) To make the navmesh more optimized, you can apply a "Decimate" modifier with whatever ratio you want. For me ratio of 0.5 works pretty well. After that, you have to repeat the previous step of pressing "M -> By distance" until you see 0 removed.

(optional) You can also remove inaccessible parts of the navmesh by switching to edit mode and selecting whatever polygons you want to remove, shortcut "L" works well here, selecting all connected polygons at your mouse cursor. Selected polygons can be deleted by pressing "X"

### III. Exporting the navmesh:
Install "io_export_aion_nav.py" like any blender addon.

Select your navmesh, File -> Export -> Aion Navmesh (.nav).