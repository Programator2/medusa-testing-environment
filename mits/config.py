# -*- coding: utf-8 -*-
"""
@package mits.commons
Contains definitions of tests and contents of a config file which is used for Constable when testing.
"""
import commons
import locale

# Definitions of tests
testing_suites = {'Sequential test': 'do_tests', 'Concurrent test': 'do_concurrent_tests'}
inv_testing_suites = {v: k for k, v in testing_suites.items()}
tests = {}
tests['symlink'] = {
    "config": """\
all_domains symlink allowed {
    log_proc("allowed-symlink['"+oldname+"' --> '"+filename+"']");
    return OK;
}
all_domains symlink restricted {
    log_proc("denied-symlink['"+oldname+"' --> '"+filename+"']");
    return DENY;
}
    """,
    "command": "ln -s test.txt link.ln",
    "command_denied": "ln -s restricted/test.txt restricted/link.ln",
    "before_async": False,
    "before": None,
    "after": "rm link.ln",
    "output_expect": None,
    "dmesg_expect": "allowed-symlink['test.txt' --> 'link.ln']",
    "output_expect_denied_sk": "ln: failed to create symbolic link 'restricted/link.ln': Operácia nie je povolená",
    "output_expect_denied_en": "ln: failed to create symbolic link 'restricted/link.ln': Permission denied",
    "dmesg_expect_denied": "denied-symlink['restricted/test.txt' --> 'link.ln']"
}
tests['link'] = {
    "config": """\
all_domains link allowed {
    log_proc("allowed-link['"+filename+"' --> '"+newname+"']");
    return OK;
}
all_domains link restricted {
    log_proc("denied-link['"+filename+"' --> '"+newname+"']");
    return DENY;
}
    """,
    "command": "ln test2.txt link2.ln",
    "command_denied": "ln restricted/test2.txt restricted/link2.ln",
    "before_async": False,
    "before": "touch test2.txt restricted/test2.txt",
    "after": "rm link2.ln test2.txt restricted/test2.txt",
    "output_expect": None,
    "dmesg_expect": "link['test2.txt' --> 'link2.ln']",
    "output_expect_denied_sk": "ln: failed to create hard link 'restricted/link2.ln' => 'restricted/test2.txt': Operácia nie je povolená",
    "output_expect_denied_en": "ln: failed to create hard link 'restricted/link2.ln' => 'restricted/test2.txt': Permission denied",
    "dmesg_expect_denied": "denied-link['test2.txt' --> 'link2.ln']"
}
tests['readlink'] = {
    "config": """\
all_domains readlink allowed {
    log_proc("allowed-readlink['"+filename+"' --> '"+newname+"']");
    return OK;
}
all_domains readlink restricted {
    log_proc("denied-readlink['"+filename+"' --> '"+newname+"']");
    return DENY;
}
    """,
    "command": "ls",
    "command_denied": "ls restricted",
    "before_async": False,
    "before": ["touch test3.txt restricted/test3.txt", "ln -s test3.txt link3.txt",
               "ln -s restricted/test3.txt restricted/link3.txt"],
    "after": "rm test3.txt link3.txt restricted/test3.txt restricted/link3.txt",
    "output_expect": "***",
    "dmesg_expect": "allowed-readlink['test3.txt' --> 'link3.txt']",
    "output_expect_denied_sk": "***",
    "output_expect_denied_en": "***",
    "dmesg_expect_denied": "denied-readlink['restricted/test3.txt' --> 'restricted/link3.txt']"
}
# TODO preview config in html
tests['mkdir'] = {
    "config": """\
all_domains mkdir allowed {
    log_proc("allowed-mkdir['"+filename+"']");
    return OK;
}
all_domains mkdir restricted {
    log_proc("denied-mkdir['"+filename+"']");
    return DENY;
}
    """,
    "command": "mkdir test",
    "command_denied": "mkdir restricted/test",
    "before_async": False,
    "before": None,
    "after": "rmdir test",
    "output_expect": None,
    "dmesg_expect": "allowed-mkdir['test']",
    "output_expect_denied_sk": "mkdir: nie je možné vytvoriť adresár `restricted/test': Operácia nie je povolená",
    "output_expect_denied_en": "mkdir: cannot create directory ‘restricted/test’: Permission denied",
    "dmesg_expect_denied": "denied-mkdir['test']"
}
tests['rmdir'] = {
    "config": """\
all_domains rmdir allowed {
    log_proc("allowed-rmdir['"+filename+"']");
    return OK;
}
all_domains rmdir restricted {
    log_proc("denied-rmdir['"+filename+"']");
    return DENY;
}
    """,
    "command": "rmdir folder",
    "command_denied": "rmdir restricted/folder",
    "before_async": False,
    "before": "mkdir folder restricted/folder",
    "after": "rmdir restricted/folder",
    "output_expect": None,
    "dmesg_expect": "allowed-rmdir['folder']",
    "output_expect_denied_sk": "rmdir: nepodarilo sa odstrániť 'restricted/folder': Operácia nie je povolená",
    "output_expect_denied_en": "rmdir: failed to remove 'restricted/folder': Permission denied",
    "dmesg_expect_denied": "denied-rmdir['folder']"
}
tests['unlink'] = {
    "config": """\
all_domains unlink allowed {
    log_proc("allowed-unlink['"+filename+"']");
    return OK;
}
all_domains unlink restricted {
    log_proc("denied-unlink['"+filename+"']");
    return DENY;
}
    """,
    "command": "unlink file.txt",
    "command_denied": "unlink restricted/file.txt",
    "before_async": False,
    "before": "touch file.txt restricted/file.txt",
    "after": "rm restricted/file.txt",
    "output_expect": None,
    "dmesg_expect": "allowed-unlink['file.txt']",
    "output_expect_denied_sk": "unlink: nie je možné odpojiť (unlink) 'restricted/file.txt': Operácia nie je povolená",
    "output_expect_denied_en": "unlink: cannot unlink 'restricted/file.txt': Permission denied",
    "dmesg_expect_denied": "denied-unlink['file.txt']"
}
tests['rename'] = {
    "config": """\
all_domains rename allowed {
    log_proc("allowed-rename['"+filename+"' --> '"+newname+"']");
    return OK;
}
all_domains rename restricted {
    log_proc("denied-rename['"+filename+"' --> '"+newname+"']");
    return DENY;
}
    """,
    "command": "mv rename_me renamed",
    "command_denied": "mv restricted/rename_me restricted/renamed",
    "before_async": False,
    "before": "touch rename_me restricted/rename_me",
    "after": "rm renamed restricted/rename_me",
    "output_expect": None,
    "dmesg_expect": "allowed-rename['rename_me' --> 'renamed']",
    "output_expect_denied_sk": "mv: cannot move 'restricted/rename_me' to 'restricted/renamed': Operácia nie je povolená",
    "output_expect_denied_en": "mv: cannot move 'restricted/rename_me' to 'restricted/renamed': Permission denied",
    "dmesg_expect_denied": "denied-rename['rename_me' --> 'renamed']"
}
tests['create'] = {
    "config": """\
all_domains create allowed {
    log_proc("allowed-create['" + filename + " " + mode + "']");
    return OK;
}
all_domains create restricted {
    log_proc("denied-create['" + filename + " " + mode + "']");
    return DENY;
}
    """,
    "command": "touch hello.c",
    "command_denied": "touch restricted/hello.c",
    "before_async": False,
    "before": None,
    "after": "rm hello.c",
    "output_expect": None,
    "dmesg_expect": "allowed-create['hello.c 0000ffff']",
    "output_expect_denied_sk": "touch: nie je možné vykonať touch 'restricted/hello.c': Prístup odmietnutý",
    "output_expect_denied_en": "touch: cannot touch 'restricted/hello.c': Permission denied",
    "dmesg_expect_denied": "denied-create['hello.c 0000ffff']"
}
tests['mknod'] = {
    "config": """\
all_domains mknod allowed {
    log_proc("allowed-mknod['"+filename+" "+uid+" "+gid+"']");
    return OK;
}
all_domains mknod restricted {
    log_proc("denied-mknod['"+filename+" "+uid+" "+gid+"']");
    return DENY;
}
    """,
    "command": "mknod fifo p",
    "command_denied": "mknod restricted/fifo p",
    "before_async": False,
    "before": None,
    "after": "rm fifo",
    "output_expect": None,
    "dmesg_expect": "allowed-mknod['fifo 0 0']",
    "output_expect_denied_sk": "mknod: restricted/fifo: Operácia nie je povolená",
    "output_expect_denied_en": "mknod: restricted/fifo: Permission denied",
    "dmesg_expect_denied": "denied-mknod['fifo 0 0']"
}
tests['fork'] = {
    "config": """\
all_domains fork {
    log("fork");
    return OK;
}
    """,
    "command": "./fork",
    "before_async": False,
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
    return OK;
}
    """,
    "command": "killall top",
    "before_async": True,
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
                  - recursive "%(allowed)s";
space allowed =   recursive "%(allowed)s"
                  - recursive "%(restricted)s";
space restricted = recursive "%(restricted)s";

all_domains     ENTER   all_domains,
                READ    all_domains, all_files, allowed, restricted,
                WRITE   all_domains, all_files, allowed, restricted,
                SEE     all_domains, all_files, allowed, restricted;

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
""" % {'allowed': commons.TESTING_PATH, 'restricted': commons.TESTING_PATH + '/restricted'}

constable_config = 'config "' + commons.TESTING_PATH + '/medusa.conf";' + '\n"test" file "/dev/medusa";'

current_locale = locale.getdefaultlocale()[0][:2]
print('Using ' + current_locale + ' locale for outputs')
for key, value in tests.items():
    if 'command_denied' in value:
        tests[key]['output_expect_denied'] = value['output_expect_denied_' + current_locale]

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
