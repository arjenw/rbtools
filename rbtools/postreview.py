    def __init__(self, url, body='', headers={}, method="PUT"):
            self.api_post(
            self.api_put(review_request['links']['self']['href'], {
        debug('HTTP DELETing %s' % url)
            r = HTTPRequest(url, method='DELETE')
                splversions.pop()
                            hlist.index(name)

                return None
    def __init__(self):
        SCMClient.__init__(self)
        # Store the 'correct' way to invoke git, just plain old 'git' by default
        self.git = 'git'

            # CreateProcess (launched via subprocess, used by check_install)
            # does not automatically append .cmd for things it finds in PATH.
            # If we're on Windows, and this works, save it for further use.
            if sys.platform.startswith('win') and check_install('git.cmd --help'):
                self.git = 'git.cmd'
            else:
                return None
        git_dir = execute([self.git, "rev-parse", "--git-dir"],
        self.head_ref = execute([self.git, 'symbolic-ref', '-q', 'HEAD']).strip()
            data = execute([self.git, "svn", "info"], ignore_errors=True)
                version = execute([self.git, "svn", "--version"],
                svn_remote = execute([self.git, "config", "--get",
        merge = execute([self.git, 'config', '--get',
        remote = execute([self.git, 'config', '--get',
        remoteOutput = execute([self.git, "remote", "show", "-n", upstream_remote])
        gitRemoteMatch = re.search('URL: (.*)', remoteOutput)
        origin_url = gitRemoteMatch.group(1)
        url = execute([self.git, "config", "--get", "reviewboard.url"],
        self.merge_base = execute([self.git, "merge-base", self.upstream_branch,
            options.summary = execute([self.git, "log", "--pretty=format:%s",
                [self.git, "log", "--pretty=format:%s%n%n%b",
            diff_lines = execute([self.git, "diff", "--no-color", "--no-prefix",
            return execute([self.git, "diff", "--no-color", "--full-index",
        rev = execute([self.git, "svn", "find-rev", parent_branch]).strip()
                    [self.git, "log", "--pretty=format:%s", revision_range + ".."],
                    [self.git, "log", "--pretty=format:%s%n%n%b", revision_range + ".."],
                    [self.git, "log", "--pretty=format:%s", "%s..%s" % (r1, r2)],
                    [self.git, "log", "--pretty=format:%s%n%n%b", "%s..%s" % (r1, r2)],
        subprocess.Popen(command.split(' '),
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        # NOTE: In Review Board 1.5.2 through 1.5.3.1, the changenum support
        #       is broken, so we have to force the deprecated API.
        if (parse_version(server.rb_version) >= parse_version('1.5.2') and
            parse_version(server.rb_version) <= parse_version('1.5.3.1')):
            debug('Using changenums on Review Board %s, which is broken. '
                  'Falling back to the deprecated 1.0 API' % server.rb_version)