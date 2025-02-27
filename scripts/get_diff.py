import datetime
import re
import logging
from deepdiff import DeepDiff
from pprint import pprint

LOG_FILE_PATH = "/home/aviuser/logfile_get_diff.log"
logging.basicConfig(filename=LOG_FILE_PATH,
                    filemode='a',
                    format='%(asctime)s.%(msecs)d %(name)s line.%(lineno)d %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

log = logging.getLogger("gitFetch")
log.info("--------------- Starting Fetch -------------")


def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def sortd(diffs):
    return sorted(diffs, key=lambda diff: natural_key(diff["to"]))

UNKNOWN = 1
DICT = 2
LIST = 3

def print_wip(s, wip):
    recursions, diffs = wip
    print(s + str(diff_len(diffs)) + ": " + str([("UNKNOWN" if r[0] == UNKNOWN else ("DICT" if r[0] == DICT else "LIST"), r[1], r[2]) for r in recursions]))

def diff_len(elem):
    if elem is None:
        return 0
    if type(elem) in (str, str):
        return len(elem)
    if type(elem) in (int, int, float, bool):
        return len(str(elem))
    if type(elem) in (list, tuple):
        return sum([diff_len(v) for v in elem])
    if type(elem) == dict:
        return sum([diff_len(k) + diff_len(v) for k,v in elem.items()])
    log.error("unrecognized: %s", type(elem))
    try:
        return len(str(elem))
    except Exception as e:
        log.error("error: %s", e)
    return 0



def get_diffs_unknown(old_value, new_value, recursions, path, diffs):
    # print "UNKNOWN: %s" % (path,)
    if isinstance(old_value, dict):
        return [(recursions + [(DICT, path, 0, old_value, new_value)], diffs)]
    if isinstance(old_value, list):
        return [(recursions + [(LIST, path, (0, 0), old_value, new_value)], diffs)]
    if old_value == new_value:
        return [(recursions, diffs)]
    return [(recursions, diffs + [{
        "to": path,
        "before": old_value,
        "after": new_value,
    }])]

def get_dict_diffs(old_dict, new_dict, i, recursions, path, diffs):
    # print "DICT: %s %d" % (path, i)
    keys = sorted(set(list(new_dict.keys()) + list(old_dict.keys())))
    for i in range(i, len(keys)):
        k = keys[i]
        new_path = path + "." + k
        if k not in old_dict:
            return [(
                recursions + [(DICT, path, i+1, old_dict, new_dict)],
                diffs + [{
                    "to": new_path,
                    "after": new_dict[k],
                }]
            )]
        elif k not in new_dict:
            return [(
                recursions + [(DICT, path, i+1, old_dict, new_dict)],
                diffs + [{
                    "to": new_path,
                    "before": old_dict[k],
                }]
            )]
        elif old_dict[k] != new_dict[k]:
            return [(
                recursions + [
                    (DICT, path, i+1, old_dict, new_dict),
                    (UNKNOWN, new_path, None, old_dict[k], new_dict[k])
                ],
                diffs
            )]
    return [(recursions, diffs)]

MAX_LIST_DIFFS = 5
def get_list_diffs(old_list, new_list, old_i, new_i, recursions, path, diffs):
    # otherwise, seek for next diff
    while True:
        if old_i >= len(old_list) or new_i >= len(new_list):
            diffs += [{"to": path + "@" + str(i), "after": new_list[i]}
                      for i in range(new_i, len(new_list))]
            diffs += [{"to": path + "@" + str(new_i), "before": old_list[i + old_i]}
                      for i in range(0, len(old_list) - old_i)]
            return [(recursions, diffs)]
        old_val = old_list[old_i]
        new_val = new_list[new_i]
        if old_val == new_val:
            old_i += 1
            new_i += 1
        else:
            new_path = path + "@" + str(new_i)
            return [
                # APPEND
                (
                    recursions + [(LIST, path, (old_i, new_i + 1), old_list, new_list)],
                    diffs + [{"to": new_path, "after": new_val}]
                ),
                # REMOVE
                (
                    recursions + [(LIST, path, (old_i + 1, new_i), old_list, new_list)],
                    diffs + [{"to": new_path, "before": old_val}]
                ),
                # UPDATE
                (
                    recursions + [
                        (LIST, path, (old_i + 1, new_i + 1), old_list, new_list),
                        (UNKNOWN, new_path, None, old_val, new_val)
                    ],
                    diffs
                ),
            ]

def get_diffs(old_value, new_value):
    best = None
    # a "wip" consistent of two lists: a list of "stacktraces", and a list of "diffs"
    # a "diff" is just a representation of one change
    # a "stacktrace" is method name, path, args, old_val, new_val
    wips = [([(UNKNOWN, "root", None, old_value, new_value)], [])]
    start = datetime.datetime.now()
    timed_out = False
    while len(wips) > 0:
        now = datetime.datetime.now()
        #if now - start > datetime.timedelta(seconds=1):
        #    timed_out = True
        #    break
        wip = wips.pop(0)
        # print_wip("NEXT: ", wip)
        recursions, diffs = wip
        if best is not None and diff_len(best) <= diff_len(diffs):
            # print "SKIPPING, TOO LONG"
            continue
        recursions = list(recursions)
        diffs = list(diffs)
        # DONE
        if len(recursions) == 0:
            best = diffs
            # print "WINNER: " + str(diff_len(diffs))
            continue

        # NOT DONE
        f, path, args, old_v, new_v = recursions[-1]
        # print "OLD_V: " + str(old_v)
        # print "NEW_V: " + str(new_v)
        recursions = recursions[:-1]
        diffs = sortd(diffs)
        if f == UNKNOWN:
            new_wips = get_diffs_unknown(old_v, new_v, recursions, path, diffs)
        elif f == DICT:
            i = args
            new_wips = get_dict_diffs(old_v, new_v, i, recursions, path, diffs)
        elif f == LIST:
            i, j = args
            new_wips = get_list_diffs(old_v, new_v, i, j, recursions, path, diffs)
        else:
            raise Exception("unknown function " + str(f))
        # for wip in new_wips:
            # print_wip("ADDED: ", wip)
        wips += new_wips
        # print "new len: " + str(len(wips))
    if timed_out and not best:
        best = [{
            'to': 'root',
            'before': old_value,
            'after': new_value,
        }]
    return best

import json
with open("/home/aviuser/automation_stuff/scripts/get_diff_val.json", "r") as f:
    data = json.loads(f.read())

old_value = data["old_value_1"]
new_value = data["new_value_1"]
deepdiff = DeepDiff(old_value, new_value)

pprint(deepdiff, indent=2)

print(get_diffs(old_value, new_value))