# AnimAssist
Provides a quick and easy way to mod animations in FFXIV.

You will need:
- The executables from this repository. Click releases, download the latest one, and extract the folder somewhere on your system.
- One of:
  - Python. I wrote anim.py on 3.8.10.
  - BeautifulSoup. `pip install bs4` at a terminal or command line.
- OR:
  - anim.exe, packaged in the release.
- 3DS Max. No other editors are supported with this method.
- The HavokMax plugin by PredatorCZ: https://github.com/PredatorCZ/HavokMax
  - You can place this plugin in your 3DS Max plugins folder.
- FFXIV Explorer: https://github.com/goaaats/ffxiv-explorer-fork
  - OR: Some other method of obtaining raw files from the game. They must be **raw** files, and not converted in any way.
- Godbert: https://github.com/xivapi/SaintCoinach
  - OR: Some other method of viewing game sheets, such as https://github.com/xivapi/ffxiv-datamining/tree/master/csv

# Ok, how do I do this?
Warning: this is fairly technical. It's command line. It's not as easy as using something like Textools or the quick launcher.

### Obtaining the files you need
FFXIV's files are only browsable with third party tools, like FFXIV Explorer above, which is what I use.
However, it's not always easy to tell which file you need. This is where tools like Godbert come in handy, since there aren't really
any easy to use tools for identifying animations or skeletons. I'm going to target an emote for now. I used the Fist Bump emote
back when I wrote my C++ converter, and I've been using it again, so we'll use that here.
I'll be using Godbert to view game sheets.

Popping open the emote sheet, we can see emote names, their text commands, and a list of "ActionTimeline" columns in the row.
![sheet](https://github.com/lmcintyre/AnimAssist/raw/main/gh/sheet.png)

As you can see, not all ActionTimeline entries are filled out. The main one we care about is the first entry - `emote/fistbump`.
While this is actually referring to the timeline, the animation for a timeline is almost always located at the same folder,
but for the skeleton that the animation is for. A **lot** of animations in XIV are built for male Hyur (skeleton 0101) and other
races just use that. Hard to tell without using a live path logger.

Anyways, let's just mess with male Hyur's fist bump. We know where it is now. All animation related things, barring
cutscene-specific animations, are located in 040000. Pop open FFXIV Explorer, navigate to your game folder,
and pop open 040000.win32.index. Let's grab the male Hyur skeleton first:

![male hyur skele](https://github.com/lmcintyre/AnimAssist/raw/main/gh/explorer_skl.png)

FFXIV keeps human skeletons in `chara/human/c{skele_id}/skeleton/base/b0001/skl_c{skele_id}b0001.sklb`. So, we went there, and we have
an sklb file. Extract this as "raw" using File > Extract Raw. Save it somewhere nice. Note that FFXIV Explorer will recreate
the FFXIV folder paths. If you select C:\Users\User\Desktop\tmp, it will save the file in 
`C:\Users\User\Desktop\tmp\chara\human\c0101\skeleton\base\b0001\skl_c0101b0001.sklb`. That's just the way it is.

Anyways, since we're still on male Hyur, go to `chara/human/c0101/animation/bt_common/emote` and do the same thing as above,
but with `fistbump.pap`. This is your animation file. Place them both somewhere save, **as you'll need both of them later to put the animation back into the game.**

### Using AnimAssist

AnimAssist requires two files: anim.exe and animassist.exe. Or, if you're just running the Python script itself, anim.py and animassist.exe.
I'll be using anim.exe rather than using the python script directly.

The command for turning the skeleton and animation files into something you can edit is:

`anim.exe extract -s skeleton_file.sklb -p pap_file.pap -o output_file.hkx`

where output_file.hkx will be a Havok file that you can open in 3DS Max using HavokMax.

This is what it looks like when I run this command on the files we just obtained:
![command](https://github.com/lmcintyre/AnimAssist/raw/main/gh/extract.png)

Note the skeleton warning. Skeletons mismatch don't produce an error, and will break literally everything ever.

### Opening the file properly

Open 3DS Max and check the Plug-in Manager to ensure HavokMax is properly installed.

From the Max menu, click Import and select your output_file.hkx from the previous step to open it in 3DS Max. Select **disable scale, invert top, and set Back: Top.**
Click import, and you'll get a wonderful fistbumping skeleton, read directly from what was once game files.

![skeleton](https://github.com/lmcintyre/AnimAssist/raw/main/gh/skl.png)

### Saving the file properly

You have some sweet changes to some animation, but now we need to put it back into the game.

From the Max menu, click Export and type any filename you want, and save it in a cool, dry place. In the "Save as type"
drop-down, select "Havok Export (*.HKA, *.HKX, *.,HKT)". We will be saving an hkx file once more. Export your file,
again, selecting **disable scale, invert top, and set Back: Top.** You must select those, as well 
as **Export animation and include skeleton**. **Optimize tracks is optional**.

### Using AnimAssist (cont)

You have a file containing a skeleton and an animation. But it's Havok. We need AnimAssist to turn it into an animation
file for the game.

That command is:

`anim.exe pack -s original_skeleton_file.sklb -p original_pap_file.pap -a modified_animation.hkx -o new_ffxiv_animation.pap`

where `new_ffxiv_animation.pap` is an animation file, ready to be imported into the game.

![pack](https://github.com/lmcintyre/AnimAssist/raw/main/gh/pack.png)
The output will look like this. Again, note the skeleton warning.

### That's great. How do I put it into the game? What?

There are two methods.

## FFXIV Textools

The love hate relationship we all have. Assuming you wanted to replace the animation you originally exported 
(in my case, `chara/human/c0101/animation/a0001/bt_common/emote/fistbump.pap`),

Steps:
- Open Textools
- Select Tools > Raw File Operations > Import Raw File
- Enter the path to the **game's file** in the box. Note: You can right-click on files in FFXIV Explorer to copy their path.
- Select the new pap file from the file selector button
TexTools should import the file. If it doesn't, that kinda sucks.

## Penumbra

I use Penumbra to develop things like that modify game files because it's far easier. Penumbra installation will
not be covered here, but it is assumed you have a mod directory set up and other Penumbra mods work properly.
Steps:
- Create a new mod using the + button in the bottom left of the Installed Mods menu in Penumbra.
- Name the mod.
- Navigate to the mod's folder.
- Recreate the directory structure up to the expected file. If you exported with FFXIV Explorer, you can copy that folder
structure, but be careful you don't overwrite your new pap file.
- Place your new pap file in the expected location by the game. For example, when I used AnimAssist to create my new pap file,
I named it `fistbump_new.pap`, but when I copy it into the mod folder, I need to name it `fistbump.pap` because that's what the
game is expecting.
- Go to Settings, and click Rediscover Mods.
- Go back to Installed Mods, and your replacement file should appear in the list.
- Click Enable on the mod's checkbox.
- You may have to swap races or jobs to get the game to reload an animation file live.

Congrats. You have an animation.

![comparison](https://github.com/lmcintyre/AnimAssist/raw/main/gh/both.png)

# Known Issues

Pap files with multiple animations will ask which animation to extract, but I didn't test this. I am not going to be
adding support for recreating a pap file with multiple animations in it.

This has been barely tested, and was developed over 3 days. I was still fixing stuff when I wrote this README.

# Technical Details

I was originally writing these tools to be used with the Havok content tools for asset merging and conversion manually,
as well as manual XML editing. But I was like, I could just automate that too.

Python handles:
- Parsing XIV sklb (skeleton) and pap (animation) files
- Parsing Havok XML packfiles for the skeleton remapping functionality
- Calling the C++ executable

C++ handles:
- Conversion between Havok proprietary filetypes

The overall flow goes as follows:
- Skeleton and animation are obtained from the game in the form of the sklb and pap files.
  - Both file types have a header, and some optional info in the beginning before the Havok data.
  - This Havok data is directly readable by just about any Havok tool. They are Havok Binary Tagfiles, which
  means they aren't specific to any platform.
- The following occurs when "extracting":
  - The sklb and pap are read, and their Havok data written to temporary files.
  - Those temporary files are combined in C++ by invoking animassist.exe.
  - A Havok Binary Packfile is written out with both the skeleton and animation present. HavokMax does not support
  binary or XML tagfiles, so this is how it had to be handled.
- The following occurs when "packing":
  - The original sklb and pap are read, with the sklb Havok data being written to a temporary file.
  - The temporary sklb is converted in C++ to a Havok XML Packfile. (The output of HavokMax is the same type)
  - Python parses both XMLs with beautifulsoup to determine how to remap the bone indices, since
  HavokMax rewrites the transform track order differently from how the skeleton actually is, and we
  cannot include a skeleton as XIV already has it loaded.
  - With the transform tracks remapped properly, that text is written out, and converted to a Havok Binary Tagfile
  using C++ again, but this time, it removes the skeleton from the file. The game is expecting a Binary Tagfile,
  so I just didn't want to rock the boat too much. Other formats might work.
  - Python then reads the data preceding the Havok data and the data after the Havok data in the original pap, fixing the
  offset to the data *after* the Havok data based on the size of the new Havok data.
  - Python writes pre-Havok data, new Havok data, and post-Havok data to a new pap file. Done.

# Building and Contributions

### Note
I feel bad that this workflow was thought up, designed, and then kept a secret. That's not what the XIV
developer community is about. While there are things people don't share for certain reasons - be it legal, be it automation,
monetization should not be one of them. That's my belief. Note that this project's license is WTFPL.

### Contributions
I would prefer forks rather than contributions to this repository. Please do whatever you want to make modding more fun
and easy for others, but I ask you make it public.

This repository would not have been possible without PredatorCZ's immense work on HavokLib and HavokMax.

### Building
Building animassist.exe requires the Havok 2014 SDK and an env var of `HAVOK_SDK_ROOT` set to the directory.

You can find the Havok SDK to compile with [in the description of this video](https://www.youtube.com/watch?v=U88C9K-mSHs).
Please note that is NOT a download I control, just a random one from online.