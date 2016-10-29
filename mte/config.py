"""@package mte.commons
Contains definitions of tests and contents of a config file which is used for Constable when testing.
"""
import commons

# Definitions of tests
testing_suites = {'Sequential test': 'do_tests', 'Concurrent test': 'do_concurrent_tests'}
inv_testing_suites = {v: k for k, v in testing_suites.items()}
tests = {}
tests['symlink'] = {
    "config": """\
all_domains symlink domov {
    log_proc("symlink['"+oldname+"' --> '"+filename+"']");
    return ALLOW;
}
    """,
    "command": "ln -s test.txt link.ln",
    "before": None,
    "after": "rm link.ln",
    "output_expect": None,
    "dmesg_expect": "symlink['test.txt' --> 'link.ln']"
}
tests['link'] = {
    "config": """\
all_domains link domov {
    log_proc("link['"+filename+"' --> '"+newname+"']");
    return ALLOW;
}
    """,
    "command": "ln test2.txt link2.ln",
    "before": "touch test2.txt",
    "after": "rm link2.ln test2.txt",
    "output_expect": None,
    "dmesg_expect": "link['test2.txt' --> 'link2.ln']"
}
tests['readlink'] = {
    "config": """\
all_domains readlink domov {
    log_proc("readlink['"+filename+"' --> '"+newname+"']");
    return ALLOW;
}
    """,
    "command": "ls",
    "before": ["touch test3.txt", "ln -s test3.txt link3.txt"],
    "after": "rm test3.txt link3.txt",
    "output_expect": None,
    # add ignore output
    "dmesg_expect": "readlink['test3.txt' --> 'link3.txt']"
}
# TODO preview config in html
tests['mkdir'] = {
    "config": """\
all_domains mkdir domov {
    log_proc("mkdir['"+filename+"']");
    return ALLOW;
}
    """,
    "command": "mkdir test",
    "before": None,
    "after": "rmdir test",
    "output_expect": None,
    "dmesg_expect": "mkdir['test']"
}
tests['rmdir'] = {
    "config": """\
all_domains rmdir domov {
    log_proc("rmdir['"+filename+"']");
    return ALLOW;
}
    """,
    "command": "rmdir folder",
    "before": "mkdir folder",
    "after": None,
    "output_expect": None,
    "dmesg_expect": "rmdir['folder']"
}
tests['unlink'] = {
    "config": """\
all_domains unlink domov {
    log_proc("unlink['"+filename+"']");
    return ALLOW;
}
    """,
    "command": "unlink file.txt",
    "before": "touch file.txt",
    "after": None,
    "output_expect": None,
    "dmesg_expect": "unlink['file.txt']"
}
tests['rename'] = {
    "config": """\
all_domains rename domov {
    log_proc("rename['"+filename+"' --> '"+newname+"']");
    return ALLOW;
}
    """,
    "command": "mv rename_me renamed",
    "before": "touch rename_me",
    "after": "rm renamed",
    "output_expect": None,
    "dmesg_expect": "rename['rename_me' --> 'renamed']"
}
tests['create'] = {
    "config": """\
all_domains create domov {
    log_proc("create['" + filename + " " + mode + "']");
    return ALLOW;
}
    """,
    "command": "touch hello.c",
    "before": None,
    "after": "rm hello.c",
    "output_expect": None,
    "dmesg_expect": "create['hello.c 0000ffff']"
}
tests['mknod'] = {
    "config": """\
all_domains mknod domov {
    log_proc("mknod['"+filename+" "+uid+" "+gid+"']");
    return ALLOW;
}
    """,
    "command": "mknod fifo p",
    "before": None,
    "after": "rm fifo",
    "output_expect": None,
    "dmesg_expect": "mknod['fifo 0 0']"
}
tests['fork'] = {
    "config": """\
all_domains fork {
    log("fork");
    return ALLOW;
}
    """,
    "command": "./fork",
    'before': ['sudo cp ' + commons.VM_MTE_PATH + '/fork ' + commons.TESTING_PATH, 'sudo chmod +x ' +
               commons.TESTING_PATH + '/fork'],
    "after": "rm fork",
    "output_expect": ['Detsky proces, pid =', 'Rodicovsky proces, pid dietata ='],
    "dmesg_expect": "fork"
}
tests['kill'] = {
    "config": """\
all_domains kill all_domains {
    log("kill");
    return ALLOW;
}
    """,
    "command": "killall top",
    "before": "top",
    "after": None,
    "output_expect": None,
    "dmesg_expect": "kill"
}
beginning = """\
tree	"fs" clone of file by getfile getfile.filename;
primary tree "fs";
tree	"domain" of process;

space all_domains = recursive "domain";
space all_files	= recursive "/"
                  - recursive "/home";
space domov =   recursive "/home";

all_domains     ENTER   all_domains,
                READ    all_domains, all_files, domov,
                WRITE   all_domains, all_files, domov,
                SEE     all_domains, all_files, domov;

function log
{
    local printk buf.message=$1 + "\\n";
    update buf;
}

function log_proc {
    log ("" + $1 + " pid="+process.pid+" domain="+primaryspace(process,@"domain")
        +" uid="+process.uid+" luid="+process.luid +" euid="+process.euid+" suid="+process.suid
        +" pcap="+process.pcap+" icap="+process.icap+" ecap="+process.ecap
        +" med_sact="+process.med_sact+" vs=["+spaces(process.vs)+"] vsr=["+spaces(process.vsr)+"] vsw=["
        +spaces(process.vsw)+"] vss=["+spaces(process.vss)+"]"
        +" cmdline="+process.cmdline
//      +" sync-trace=["+process.syscall+"]"
    );
}
* getprocess {
    enter(process,@"domain/init");
    log_proc("getprocess");
    return OK;
}
function _init {}
"""

constable_config = 'config "' + commons.TESTING_PATH + '/medusa.conf";' + '\n"test" file "/dev/medusa";'


def make_config(list_of_tests):
    """
    Creates configuration file based on selected tests
    @param list_of_tests: List of selected tests to be run
    @return: Configuration file to be written on the hard drive
    """
    config = ""
    config += beginning
    for test in list_of_tests:
        config += tests[test]['config']
    return config
