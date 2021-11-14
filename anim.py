from bs4 import BeautifulSoup
import argparse
import struct
import tempfile
import subprocess
import os
import sys

debug = False
def dbgprint(text: str) -> None:
    if debug:
        print(f"[dbg] {text}")


def define_parser():
    parser = argparse.ArgumentParser(description="Utilities for the manual animation modding workflow in XIV.",
                                    formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(title="Requires (one of)", dest="command")

    extract_parser = subparsers.add_parser("extract", help="Extract a Havok binary packfile for editing in 3DS Max, using a pap and sklb file from XIV.")
    extract_parser.add_argument("-s", "--skeleton-file", type=argparse.FileType("rb"), help="The input skeleton sklb file.", required=True)
    extract_parser.add_argument("-p", "--pap-file", type=argparse.FileType("rb"), help="The input animation pap file.", required=True)
    extract_parser.add_argument("-o", "--out-file", type=str, help="The output Havok binary packfile.", required=True)

    pack_parser = subparsers.add_parser("pack", help="Repack an existing pap file with a new animation. Requires the input skeleton.")
    pack_parser.add_argument("-s", "--skeleton-file", type=argparse.FileType("rb"), help="The input skeleton sklb file.", required=True)
    pack_parser.add_argument("-p", "--pap-file", type=argparse.FileType("rb"), help="The input pap file.", required=True)
    pack_parser.add_argument("-a", "--anim-file", type=argparse.FileType("rb"), help="The modified animation Havok XML packfile.", required=True)
    pack_parser.add_argument("-o", "--out-file", type=str, help="The output pap file.", required=True)

    import textwrap
    parser.epilog = textwrap.dedent(
        f"""\
        commands usage:
        {extract_parser.format_usage()}
        {pack_parser.format_usage()}
        Remember that each command also has its own, more descriptive, -h/--help arg, describing what file types are expected.
        """
    )
    return parser

def animassist_check():
    if not os.path.exists("animassist.exe"):
            print("Animassist.exe is missing :(")
            sys.exit(1)

def assist_skl_tag(skeleton_path, out_path) -> None:
    animassist_check()

    complete = subprocess.run(["animassist.exe", "1", skeleton_path, out_path], capture_output=True, encoding="utf8")
    dbgprint(f"{complete.returncode}")
    dbgprint(f"{complete.stdout}")
    if not os.path.exists(out_path):
        dbgprint("Something went really wrong :(")
    else:
        dbgprint(f"Saved skeleton xml to {out_path}")

def assist_skl_anim_pack(skeleton_path, out_path) -> None:
    animassist_check()

    complete = subprocess.run(["animassist.exe", "2", skeleton_path, out_path], capture_output=True, encoding="utf8")
    dbgprint(f"{complete.returncode}")
    dbgprint(f"{complete.stdout}")
    if not os.path.exists(out_path):
        dbgprint("Something went really wrong :(")
    else:
        dbgprint(f"Saved packfile to {out_path}")

def assist_combine(skeleton_path, animation_path, animation_index, out_path) -> None:
    animassist_check()
    
    complete = subprocess.run(["animassist.exe", "3", skeleton_path, animation_path, animation_index, out_path], capture_output=True, encoding="utf8")
    dbgprint(f"{complete.returncode}")
    dbgprint(f"{complete.stdout}")

    if not os.path.exists(out_path):
        print("Something went really wrong :(")
    else:
        print(f"Saved importable file to {out_path}")


def extract(skeleton_file, anim_file, out_path):
    sklb_data = skeleton_file.read()
    pap_data = anim_file.read()
    sklb_hdr = read_sklb_header(sklb_data)
    pap_hdr = read_pap_header(pap_data)

    print(f"The input skeleton is for ID {sklb_hdr['skele_id']}.")
    print(f"The input animation is for ID {pap_hdr['skele_id']}.")
    print(f"If these mismatch, things will go very badly.")

    num_anims = len(pap_hdr["anim_infos"])
    if num_anims > 1:
        print("[WARNING] This pap file has multiple animations.")
        print("[WARNING] You will not be able to re-import this edited animation back into this pap at the moment.")
        print("[WARNING] You will need to find a single-animation pap to replace.")
        print("Please choose which one number to use and press enter:")
        for i in range(num_anims):
            print(f"{i + 1}: {pap_hdr['anim_infos'][i]['name']}")
        print(f"{num_anims + 1}: Quit")
        while True:
            try:
                choice = int(input())
            except ValueError:
                continue
            if choice and choice > -1 and choice <= num_anims + 1:
                break
        if choice == num_anims + 1:
            sys.exit(1)
        havok_anim_index = pap_hdr["anim_infos"][choice]["havok_index"]
    else:
        havok_anim_index = 0

    with tempfile.TemporaryDirectory() as tmp_folder:
        tmp_skel_path = os.path.join(tmp_folder, "tmp_skel")
        tmp_anim_path = os.path.join(tmp_folder, "tmp_anim")
        dbgprint(f"we have {tmp_skel_path} as tmp_skel")
        dbgprint(f"we have {tmp_anim_path} as tmp_anim")
        havok_skel = get_havok_from_sklb(sklb_data)
        havok_anim = get_havok_from_pap(pap_data)
        with open(tmp_skel_path, "wb") as tmp_skel:
            tmp_skel.write(havok_skel)
        with open(tmp_anim_path, "wb") as tmp_anim:
            tmp_anim.write(havok_anim)
        assist_combine(tmp_skel_path, tmp_anim_path, str(havok_anim_index), out_path)


def repack(skeleton_file, anim_file, mod_file, out_path):
    orig_sklb_data = skeleton_file.read()
    orig_pap_data = anim_file.read()

    sklb_hdr = read_sklb_header(orig_sklb_data)
    pap_hdr = read_pap_header(orig_pap_data)

    print(f"The input skeleton is for ID {sklb_hdr['skele_id']}.")
    print(f"The input animation is for ID {pap_hdr['skele_id']}.")
    print(f"If these mismatch, things will go very badly.")

    with tempfile.TemporaryDirectory() as tmp_folder:
        skel_bin_path = os.path.join(tmp_folder, "tmp_skel_bin")
        skel_xml_path = os.path.join(tmp_folder, "tmp_skel_xml")
        tmp_mod_xml_path = os.path.join(tmp_folder, "tmp_mod_xml")
        tmp_mod_bin_path = os.path.join(tmp_folder, "tmp_mod_bin")

        with open(skel_bin_path, "wb") as sklbin:
            sklbin.write(get_havok_from_sklb(orig_sklb_data))
        assist_skl_tag(skel_bin_path, skel_xml_path)

        with open(skel_xml_path, "r", encoding="utf8") as sklxml:
            skl_xml_str = sklxml.read()
        mod_xml_str = mod_file.read()

        new_xml = get_remapped_xml(skl_xml_str, mod_xml_str)
        with open(tmp_mod_xml_path, "w") as tmpxml:
            tmpxml.write(new_xml)

        assist_skl_anim_pack(tmp_mod_xml_path, tmp_mod_bin_path)

        with open(tmp_mod_bin_path, "rb") as modbin:
            new_havok = modbin.read()

        pre_havok = bytearray(orig_pap_data[:pap_hdr["havok_offset"]])
        new_timeline_offset = 26 + 40 + len(new_havok)
        offs_bytes = new_timeline_offset.to_bytes(4, "little")
        for i in range(4):
            pre_havok[22 + i] = offs_bytes[i]

        post_havok = orig_pap_data[pap_hdr["timeline_offset"]:]

        with open(out_path, "wb") as out:
            out.write(pre_havok)
            out.write(new_havok)
            out.write(post_havok)
        print(f"Wrote new pap to {out_path}!")

def get_remapped_xml(skl_xml: str, skl_anim_xml: str) -> list:
    sk_soup = BeautifulSoup(skl_xml, features="html.parser")
    anim_soup = BeautifulSoup(skl_anim_xml, features="html.parser")

    sk_bones = sk_soup.find("hkparam", {"name": "bones"}).find_all("hkparam", {"name": "name"})
    base_bonemap = list(map(lambda x: x.text, sk_bones))

    anim_bones = anim_soup.find("hkparam", {"name": "annotationTracks"}).find_all("hkparam", {"name": "trackName"})
    anim_bonemap = list(map(lambda x: x.text, anim_bones))

    new_bonemap = []
    for i in range(len(anim_bonemap)):
        search_bone = anim_bonemap[i]
        for i, bone in enumerate(base_bonemap):
            if bone == search_bone:
                new_bonemap.append(i)
                break
    bonemap_str = ' '.join(str(x) for x in new_bonemap)
    dbgprint(f"New bonemap is: {bonemap_str}")

    tt_element = anim_soup.find("hkparam", {"name": "transformTrackToBoneIndices"})
    return str(skl_anim_xml, encoding="utf8").replace(tt_element.text, bonemap_str)

SKLB_HDR_1 = ['magic', 'version', 'offset1', 'havok_offset', 'skele_id', 'other_ids']
def read_sklb_header_1(sklb_data) -> dict:
    # 4 byte magic
    # 4 byte version
    # 2 byte offset to ?
    # 2 byte offset to havok
    # 4 byte skeleton id
    # 4 x 4 byte other skeleton ids

    hdr = { k: v for k, v in zip(SKLB_HDR_1, struct.unpack('<4sIHHI4I', sklb_data[0:32])) }
    for key in hdr.keys():
        dbgprint(f"{key} : {hdr[key]}")
    return hdr

SKLB_HDR_2 = ['magic', 'version', 'offset1', 'havok_offset', 'unknown1', 'skele_id', 'other_ids']
def read_sklb_header_2(sklb_data) -> dict:
    # 4 byte magic
    # 4 byte version
    # 4 byte offset to ?
    # 4 byte offset to havok
    # 4 byte ?
    # 4 byte skeleton id
    # 4 x 4 byte other skeleton ids

    hdr = { k: v for k, v in zip(SKLB_HDR_2, struct.unpack('<4sIIIII4I', sklb_data[0:44])) }
    for key in hdr.keys():
        dbgprint(f"{key} : {hdr[key]}")
    return hdr

def read_sklb_header(sklb_data) -> dict:
    magic, ver = struct.unpack("<II", sklb_data[0:8])
    if ver != 0x31333030:
        hdr = read_sklb_header_1(sklb_data)
    else:
        hdr = read_sklb_header_2(sklb_data)
    return hdr

def get_havok_from_sklb(sklb_data):
    hdr = read_sklb_header(sklb_data)
    dbgprint(f"This skeleton file is for the skeleton c{hdr['skele_id']}.")

    havok_start = hdr['havok_offset']
    havok_end = len(sklb_data)
    new_data = sklb_data[havok_start:havok_end]

    return new_data

PAP_HDR = ['magic', 'version', 'anim_count', 'skele_id', 'info_offset', 'havok_offset', 'timeline_offset']
ANIM_INFO = ['name', 'unknown1', 'havok_index', 'unknown2']
def read_pap_header(pap_data) -> dict:
    # 4 byte magic 4
    # uint version 8
    # ushort info num 10
    # uint skele id 14
    # uint offset to info 18
    # uint offset to havok container 22
    # uint offset to timeline 26

    hdr = { k: v for k, v in zip(PAP_HDR, struct.unpack('<4sIHIIII', pap_data[0:26])) }

    hdr["anim_infos"] = []
    for i in range(hdr["anim_count"]):
        start = 26 + 40 * i
        end = 26 + 40 * (i + 1)
        anim_info = { k: v for k, v in zip(ANIM_INFO, struct.unpack('<32sHHI', pap_data[start:end])) }
        anim_info["name"] = str(anim_info["name"], encoding="utf8").split("\0")[0]
        hdr["anim_infos"].append(anim_info)

    for key in hdr.keys():
        dbgprint(f"{key} : {hdr[key]}")

    return hdr

def get_havok_from_pap(pap_data):
    hdr = read_pap_header(pap_data)
    dbgprint(f"This pap file is for the skeleton c{hdr['skele_id']}. It has {hdr['anim_count']} animation(s).")

    havok_start = hdr['havok_offset']
    havok_end = hdr['timeline_offset']
    new_data = pap_data[havok_start:havok_end]

    return new_data

def main():
    parser = define_parser()

    try:
        args = parser.parse_args()
    except FileNotFoundError:
        print("All input files must exist!")

    if args.command == "extract":
        extract(args.skeleton_file, args.pap_file, args.out_file)

    if args.command == "pack":
        repack(args.skeleton_file, args.pap_file, args.anim_file, args.out_file)


if __name__ == "__main__":
    main()