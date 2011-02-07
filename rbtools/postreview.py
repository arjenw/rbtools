import base64
from pkg_resources import parse_version
    # Specifically import json_loads, to work around some issues with
    # installations containing incompatible modules named "json".
    from json import loads as json_loads
    from simplejson import loads as json_loads
from rbtools import get_package_version, get_version_string


ADD_REPOSITORY_DOCS_URL = \
    'http://www.reviewboard.org/docs/manual/dev/admin/management/repositories/'
GNU_DIFF_WIN32_URL = 'http://gnuwin32.sourceforge.net/packages/diffutils.htm'

    def __init__(self, http_status, error_code, rsp=None, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.http_status = http_status
        self.error_code = error_code
        self.rsp = rsp

    def __str__(self):
        code_str = "HTTP %d" % self.http_status

        if self.error_code:
            code_str += ', API Error %d' % self.error_code

        if self.rsp and 'err' in self.rsp:
            return '%s (%s)' % (self.rsp['err']['msg'], code_str)
        else:
            return code_str


class HTTPRequest(urllib2.Request):
    def __init__(self, url, body, headers={}, method="PUT"):
        urllib2.Request.__init__(self, url, body, headers)
        self.method = method

    def get_method(self):
        return self.method
    def __init__(self, path, base_path, uuid, supports_parent_diffs=False):
        RepositoryInfo.__init__(self, path, base_path,
                                supports_parent_diffs=supports_parent_diffs)
            if e.error_code == 210:
        if rootdirs != pathdirs[:len(rootdirs)]:
            return '/' + '/'.join(pathdirs[len(rootdirs):])
class PresetHTTPAuthHandler(urllib2.BaseHandler):
    """urllib2 handler that conditionally presets the use of HTTP Basic Auth.

    This is used when specifying --username= on the command line. It will
    force an HTTP_AUTHORIZATION header with the user info, asking the user
    for any missing info beforehand. It will then try this header for that
    first request.

    It will only do this once.
    """
    handler_order = 480 # After Basic auth

    def __init__(self, url, password_mgr):
        self.url = url
        self.password_mgr = password_mgr
        self.used = False

    def reset(self):
        self.password_mgr.rb_user = None
        self.password_mgr.rb_pass = None
        self.used = False

    def http_request(self, request):
        if options.username and not self.used:
            # Note that we call password_mgr.find_user_password to get the
            # username and password we're working with. This allows us to
            # prompt if, say, --username was specified but --password was not.
            username, password = \
                self.password_mgr.find_user_password('Web API', self.url)
            raw = '%s:%s' % (username, password)
            request.add_header(
                urllib2.HTTPBasicAuthHandler.auth_header,
                'Basic %s' % base64.b64encode(raw).strip())
            self.used = True

        return request

    https_request = http_request


class ReviewBoardHTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    """Processes HTTP error codes.

    Python 2.6 gets HTTP error code processing right, but 2.4 and 2.5 only
    accepts HTTP 200 and 206 as success codes. This handler ensures that
    anything in the 200 range is a success.
    """
    def http_response(self, request, response):
        if not (200 <= response.code < 300):
            response = self.parent.error('http', request, response,
                                         response.code, response.msg,
                                         response.info())

        return response

    https_response = http_response


class ReviewBoardHTTPBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
    """Custom Basic Auth handler that doesn't retry excessively.

    urllib2's HTTPBasicAuthHandler retries over and over, which is useless.
    This subclass only retries once to make sure we've attempted with a
    valid username and password. It will then fail so we can use
    tempt_fate's retry handler.
    """
    def __init__(self, *args, **kwargs):
        urllib2.HTTPBasicAuthHandler.__init__(self, *args, **kwargs)
        self._retried = False

    def retry_http_basic_auth(self, *args, **kwargs):
        if not self._retried:
            self._retried = True
            response = urllib2.HTTPBasicAuthHandler.retry_http_basic_auth(
                self, *args, **kwargs)

            if response.code != 401:
                self._retried = False

            return response
        else:
            return None


    def __init__(self, reviewboard_url, rb_user=None, rb_pass=None):
        self.rb_user = rb_user
        self.rb_pass = rb_pass
                if options.diff_filename == '-':
                    die('HTTP authentication is required, but cannot be '
                        'used with --diff-filename=-')

                print 'Enter authorization information for "%s" at %s' % \

                if not self.rb_user:
                    self.rb_user = raw_input('Username: ')

                if not self.rb_pass:
                    self.rb_pass = getpass.getpass('Password: ')
        self.root_resource = None
        self.deprecated_api = False
        if self.cookie_file:
            try:
                self.cookie_jar.load(self.cookie_file, ignore_expires=True)
            except IOError:
                pass
        # Set up the HTTP libraries to support all of the features we need.
        cookie_handler      = urllib2.HTTPCookieProcessor(self.cookie_jar)
        password_mgr        = ReviewBoardHTTPPasswordMgr(self.url,
                                                         options.username,
                                                         options.password)
        basic_auth_handler  = ReviewBoardHTTPBasicAuthHandler(password_mgr)
        digest_auth_handler = urllib2.HTTPDigestAuthHandler(password_mgr)
        self.preset_auth_handler = PresetHTTPAuthHandler(self.url, password_mgr)
        http_error_processor = ReviewBoardHTTPErrorProcessor()

        opener = urllib2.build_opener(cookie_handler,
                                      basic_auth_handler,
                                      digest_auth_handler,
                                      self.preset_auth_handler,
                                      http_error_processor)
        opener.addheaders = [('User-agent', 'RBTools/' + get_package_version())]
    def check_api_version(self):
        """Checks the API version on the server to determine which to use."""
        try:
            root_resource = self.api_get('api/')
            rsp = self.api_get(root_resource['links']['info']['href'])

            if (parse_version(rsp['info']['product']['package_version']) >=
                parse_version('1.5.2')):
                self.deprecated_api = False
                self.root_resource = root_resource
                debug('Using the new web API')
                return
        except APIError, e:
            if e.http_status != 404:
                # We shouldn't reach this. If there's a permission denied
                # from lack of logging in, then the basic auth handler
                # should have hit it.
                die("Unable to access the root /api/ URL on the server.")

        # This is an older Review Board server with the old API.
        self.deprecated_api = True
        debug('Using the deprecated Review Board 1.0 web API')

        if not self.root_resource:
            self.check_api_version()

        if (options.diff_filename == '-' and
            not options.username and not options.submit_as and
            not options.password):
            die('Authentication information needs to be provided on '
                'the command line when using --diff-filename=-')

        if self.deprecated_api:
            print "==> Review Board Login Required"
            print "Enter username and password for Review Board at %s" % \
                  self.url

            if options.username:
                username = options.username
            elif options.submit_as:
                username = options.submit_as
            elif not force and self.has_valid_cookie():
                # We delay the check for a valid cookie until after looking
                # at args, so that it doesn't override the command line.
                return
            else:
                username = raw_input('Username: ')
            if not options.password:
                password = getpass.getpass('Password: ')
            else:
                password = options.password
            debug('Logging in with username "%s"' % username)
            try:
                self.api_post('api/json/accounts/login/', {
                    'username': username,
                    'password': password,
                })
            except APIError, e:
                die("Unable to log in: %s" % e)
            debug("Logged in.")
        elif force:
            self.preset_auth_handler.reset()
            # Cookie files also append .local to bare hostnames
            if '.' not in host:
                host += '.local'


        # If repository_path is a list, find a name in the list that's
        # registered on the server.
        if isinstance(self.info.path, list):
            repositories = self.get_repositories()

            debug("Repositories on Server: %s" % repositories)
            debug("Server Aliases: %s" % self.info.path)

            for repository in repositories:
                if repository['path'] in self.info.path:
                    self.info.path = repository['path']
                    break

            if isinstance(self.info.path, list):
                sys.stderr.write('\n')
                sys.stderr.write('There was an error creating this review '
                                 'request.\n')
                sys.stderr.write('\n')
                sys.stderr.write('There was no matching repository path'
                                 'found on the server.\n')
                sys.stderr.write('List of configured repositories:\n')

                for repository in repositories:
                    sys.stderr.write('\t%s\n' % repository['path'])

                sys.stderr.write('Unknown repository paths found:\n')

                for foundpath in self.info.path:
                    sys.stderr.write('\t%s\n' % foundpath)

                sys.stderr.write('Ask the administrator to add one of '
                                 'these repositories\n')
                sys.stderr.write('to the Review Board server.\n')
                sys.stderr.write('For information on adding repositories, '
                                 'please read\n')
                sys.stderr.write(ADD_REPOSITORY_DOCS_URL + '\n')
                die()

            debug("Attempting to create review request on %s for %s" %
                  (self.info.path, changenum))
            data = {}
            if self.deprecated_api:
                data['repository_path'] = self.info.path
                rsp = self.api_post('api/json/reviewrequests/new/', data)
            else:
                data['repository'] = self.info.path

                links = self.root_resource['links']
                assert 'review_requests' in links
                review_request_href = links['review_requests']['href']
                rsp = self.api_post(review_request_href, data)
            if e.error_code == 204: # Change number in use
                rsp = e.rsp
                if options.diff_only:
                    # In this case, fall through and return to tempt_fate.
                    debug("Review request already exists.")
                    debug("Review request already exists. Updating it...")
                    self.update_review_request_from_changenum(
                        changenum, rsp['review_request'])
            elif e.error_code == 206: # Invalid repository
                sys.stderr.write('\n')
                sys.stderr.write('There was an error creating this review '
                                 'request.\n')
                sys.stderr.write('\n')
                sys.stderr.write('The repository path "%s" is not in the\n' %
                                 self.info.path)
                sys.stderr.write('list of known repositories on the server.\n')
                sys.stderr.write('\n')
                sys.stderr.write('Ask the administrator to add this '
                                 'repository to the Review Board server.\n')
                sys.stderr.write('For information on adding repositories, '
                                 'please read\n')
                sys.stderr.write(ADD_REPOSITORY_DOCS_URL + '\n')
                die()
            else:
                raise e
        else:
            debug("Review request created")
    def update_review_request_from_changenum(self, changenum, review_request):
        if self.deprecated_api:
            rsp = self.api_post(
                'api/json/reviewrequests/%s/update_from_changenum/'
                % review_request['id'])
        else:
            rsp = self.api_put(review_request['links']['self']['href'], {
                'changenum': review_request['changenum'],
            })

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/draft/set/' % rid, {
                field: value,
            })
        else:
            self.api_put(review_request['links']['draft']['href'], {
                field: value,
            })
        if self.deprecated_api:
            url = 'api/json/reviewrequests/%s/'
        else:
            url = '%s%s/' % (
                self.root_resource['links']['review_requests']['href'], rid)

        rsp = self.api_get(url)

        if self.deprecated_api:
            rsp = self.api_get('api/json/repositories/')
            repositories = rsp['repositories']
        else:
            rsp = self.api_get(
                self.root_resource['links']['repositories']['href'])
            repositories = rsp['repositories']

            while 'next' in rsp['links']:
                rsp = self.api_get(rsp['links']['next']['href'])
                repositories.extend(rsp['repositories'])

        return repositories
        if self.deprecated_api:
            url = 'api/json/repositories/%s/info/' % rid
        else:
            rsp = self.api_get(
                '%s%s/' % (self.root_resource['links']['repositories']['href'],
                           rid))
            url = rsp['repository']['links']['info']['href']

        rsp = self.api_get(url)

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/draft/save/' % \
                          review_request['id'])
        else:
            self.api_put(review_request['links']['draft']['href'], {
                'public': 1,
            })

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/diff/new/' %
                          review_request['id'], fields, files)
        else:
            self.api_post(review_request['links']['diffs']['href'],
                          fields, files)

    def reopen(self, review_request):
        """
        Reopen discarded review request.
        """
        debug("Reopening")

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/reopen/' %
                          review_request['id'])
        else:
            self.api_put(review_request['links']['self']['href'], {
                'status': 'pending',
            })

        if self.deprecated_api:
            self.api_post('api/json/reviewrequests/%s/publish/' %
                          review_request['id'])
        else:
            self.api_put(review_request['links']['draft']['href'], {
                'public': 1,
            })
        rsp = json_loads(data)
            # With the new API, we should get something other than HTTP
            # 200 for errors, in which case we wouldn't get this far.
            assert self.deprecated_api
            self.process_error(200, data)
    def process_error(self, http_status, data):
        """Processes an error, raising an APIError with the information."""
        try:
            rsp = json_loads(data)

            assert rsp['stat'] == 'fail'

            debug("Got API Error %d (HTTP code %d): %s" %
                  (rsp['err']['code'], http_status, rsp['err']['msg']))
            debug("Error data: %r" % rsp)
            raise APIError(http_status, rsp['err']['code'], rsp,
                           rsp['err']['msg'])
        except ValueError:
            debug("Got HTTP error: %s: %s" % (http_status, data))
            raise APIError(http_status, None, None, data)

        rsp = urllib2.urlopen(url).read()
        except IOError, e:
            debug('Failed to write cookie file: %s' % e)
        return rsp
        if path.startswith('http'):
            # This is already a full path.
            return path


        try:
            return self.process_json(self.http_get(path))
        except urllib2.HTTPError, e:
            self.process_error(e.code, e.read())
            try:
                self.cookie_jar.save(self.cookie_file)
            except IOError, e:
                debug('Failed to write cookie file: %s' % e)
            return data
        except urllib2.HTTPError, e:
            # Re-raise so callers can interpret it.
            raise e
        except urllib2.URLError, e:
            try:
                debug(e.read())
            except AttributeError:
                pass

            die("Unable to access %s. The host path may be invalid\n%s" % \
                (url, e))

    def http_put(self, path, fields):
        """
        Performs an HTTP PUT on the specified path, storing any cookies that
        were set.
        """
        url = self._make_url(path)
        debug('HTTP PUTting to %s: %s' % (url, fields))

        content_type, body = self._encode_multipart_formdata(fields, None)
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(body))
        }

        try:
            r = HTTPRequest(url, body, headers, method='PUT')
            data = urllib2.urlopen(r).read()
        except urllib2.HTTPError, e:
            # Re-raise so callers can interpret it.
            raise e

    def http_delete(self, path):
        """
        Performs an HTTP DELETE on the specified path, storing any cookies that
        were set.
        """
        url = self._make_url(path)
        debug('HTTP DELETing %s: %s' % (url, fields))

        try:
            r = HTTPRequest(url, body, headers, method='DELETE')
            data = urllib2.urlopen(r).read()
            self.cookie_jar.save(self.cookie_file)
            return data
            # Re-raise so callers can interpret it.
            raise e
        except urllib2.URLError, e:
            try:
                debug(e.read())
            except AttributeError:
                pass

            die("Unable to access %s. The host path may be invalid\n%s" % \
                (url, e))
        try:
            return self.process_json(self.http_post(path, fields, files))
        except urllib2.HTTPError, e:
            self.process_error(e.code, e.read())

    def api_put(self, path, fields=None):
        """
        Performs an API call using HTTP PUT at the specified path.
        """
        try:
            return self.process_json(self.http_put(path, fields))
        except urllib2.HTTPError, e:
            self.process_error(e.code, e.read())

    def api_delete(self, path):
        """
        Performs an API call using HTTP DELETE at the specified path.
        """
        try:
            return self.process_json(self.http_delete(path))
        except urllib2.HTTPError, e:
            self.process_error(e.code, e.read())
            content += str(fields[key]) + "\r\n"
    def check_options(self):
        pass

            # If repository_info is a list, check if any one entry is in trees.
            path = None

            if isinstance(repository_info.path, list):
                for path in repository_info.path:
                    if path in trees:
                        break
                else:
                    path = None
            elif repository_info.path in trees:
                path = repository_info.path

            if path and 'REVIEWBOARD_URL' in trees[path]:
                return trees[path]['REVIEWBOARD_URL']
        return self.do_diff(revs + args)
        return RepositoryInfo(path=options.repository_url,
                              base_path=options.repository_url,
                ["cleartool", "desc", "-pre", elem_path], split_lines=True)
                    if vkey.rfind("vobs") != -1 :
                        bpath = vkey[:vkey.rfind("vobs")+4]
                        fpath = vkey[vkey.rfind("vobs")+5:]
                    else :
                       bpath = vkey[:0]
                       fpath = vkey[1:]
        revs = revision_range.split(":")
        return self.do_diff(revs)[0]


                if cpath.isdir(filenam):
                    content = [
                        '%s\n' % s
                        for s in sorted(os.listdir(filenam))
                    ]
                    file_data.append(content)
                else:
                    fd = open(cpath.normpath(fn))
                    fdata = fd.readlines()
                    fd.close()
                    file_data.append(fdata)
                    # If the file was temp, it should be removed.
                    if do_rem:
                        os.remove(filenam)



        # Now that we know it's SVN, make sure we have GNU diff installed,
        # and error out if we don't.
        check_gnu_diff()

    def check_options(self):
        if (options.repository_url and
            not options.revision_range and
            not options.diff_filename):
            sys.stderr.write("The --repository-url option requires either the "
                             "--revision-range option or the --diff-filename "
                             "option.\n")
            sys.exit(1)

            files = []
            if len(args) == 1:
            elif len(args) > 1:
                files = args
            # When the source revision is zero, assume the user wants to
            # upload a diff containing all the files in ``base_path`` as new
            # files. If the base path within the repository is added to both
            # the old and new URLs, the ``svn diff`` command will error out
            # since the base_path didn't exist at revision zero. To avoid
            # that error, use the repository's root URL as the source for
            # the diff.
            if revisions[0] == "0":
                url = repository_info.path

            old_url = url + '@' + revisions[0]

                                 new_url] + files,
            # without much work. The info can also contain tabs after the
            # initial one; ignore those when splitting the string.
            parts = s.split("\t", 1)

            # If aliases exist for hostname, create a list of alias:port
            # strings for repository_path.
            if info[1]:
                servers = [info[0]] + info[1]
                repository_path = ["%s:%s" % (server, port)
                                   for server in servers]
            else:
                repository_path = "%s:%s" % (info[0], port)
        m = re.search(r'^Server version: [^ ]*/([0-9]+)\.([0-9]+)/[0-9]+ .*$',
                      data, re.M)
        self.p4d_version = int(m.group(1)), int(m.group(2))

        if len(args) == 0:
            return "default"
        elif len(args) == 1:
            if args[0] == "default":
                return "default"

                # (if it isn't a number, it can't be a cln)
                return None
        # there are multiple args (not a cln)
        else:
            return None
        if options.p4_passwd:
            os.environ['P4PASSWD'] = options.p4_passwd

                if record['action'] not in ('delete', 'move/delete'):
                    if record['action'] not in ('delete', 'move/delete'):
                elif first_record['rev'] == second_record['rev']:
                    # We when we know the revisions are the same, we don't need
                    # to do any diffing. This speeds up large revision-range
                    # diffs quite a bit.
                    continue
    """
    Return a "sanitized" change number for submission to the Review Board
    server. For default changelists, this is always None. Otherwise, use the
    changelist number for submitted changelists, or if the p4d is 2002.2 or
    newer.

    This is because p4d < 2002.2 does not return enough information about
    pending changelists in 'p4 describe' for Review Board to make use of them
    (specifically, the list of files is missing). This would result in the
    diffs being rejected.
    """
    def sanitize_changenum(self, changenum):
        if changenum == "default":
            return None
        else:
            v = self.p4d_version

            if v[0] < 2002 or (v[0] == "2002" and v[1] < 2):
                describeCmd = ["p4"]

                if options.p4_passwd:
                    describeCmd.append("-P")
                    describeCmd.append(options.p4_passwd)

                describeCmd = describeCmd + ["describe", "-s", changenum]

                description = execute(describeCmd, split_lines=True)

                if '*pending*' in description[0]:
                    return None

        return changenum

        description = []
        if changenum == "default":
        else:
            describeCmd = ["p4"]

            if options.p4_passwd:
                describeCmd.append("-P")
                describeCmd.append(options.p4_passwd)

            describeCmd = describeCmd + ["describe", "-s", changenum]

            description = execute(describeCmd, split_lines=True)

            if re.search("no such changelist", description[0]):
                die("CLN %s does not exist." % changenum)

            # Some P4 wrappers are addding an extra line before the description
            if '*pending*' in description[0] or '*pending*' in description[1]:
                cl_is_pending = True

        v = self.p4d_version

        if cl_is_pending and (v[0] < 2002 or (v[0] == "2002" and v[1] < 2)
                              or changenum == "default"):
            # Pre-2002.2 doesn't give file list in pending changelists,
            # or we don't have a description for a default changeset,
            # so we have to get it a different way.
            info = execute(["p4", "opened", "-c", str(changenum)],
                           split_lines=True)

            if len(info) == 1 and info[0].startswith("File(s) not opened on this client."):
                die("Couldn't find any affected files for this change.")

            for line in info:
                data = line.split(" ")
                description.append("... %s %s" % (data[0], data[2]))
            # Get the file list
            for line_num, line in enumerate(description):
                if 'Affected files ...' in line:
                    break
            else:
                # Got to the end of all the description lines and didn't find
                # what we were looking for.
                die("Couldn't find any affected files for this change.")
            description = description[line_num+2:]
            m = re.search(r'\.\.\. ([^#]+)#(\d+) '
                          r'(add|edit|delete|integrate|branch|move/add'
                          r'|move/delete)',
                          line)
            if changetype in ['edit', 'integrate']:
            elif changetype in ['add', 'branch', 'move/add']:
            elif changetype in ['delete', 'move/delete']:
           dl[0].startswith('Files %s and %s differ' %
                            (old_file, new_file)):
            dl = ['Binary files %s and %s differ\n' % (old_file, new_file)]
        elif len(dl) > 1:
            # Not everybody has files that end in a newline (ugh). This ensures
            # that the resulting diff file isn't broken.
            if dl[-1][-1] != '\n':
                dl.append('\n')
        else:
            die("ERROR, no valid diffs: %s" % dl[0])


        try:
            return where_output[-1]['path']
        except:
            # XXX: This breaks on filenames with spaces.
            return where_output[-1]['data'].split(' ')[2].strip()

    def __init__(self):
        self.hgrc = {}
        self._type = 'hg'
        self._hg_root = ''
        self._remote_path = ()
        self._hg_env = {
            'HGRCPATH': os.devnull,
            'HGPLAIN': '1',
        }

        # `self._remote_path_candidates` is an ordered set of hgrc
        # paths that are checked if `parent_branch` option is not given
        # explicitly.  The first candidate found to exist will be used,
        # falling back to `default` (the last member.)
        self._remote_path_candidates = ['reviewboard', 'origin', 'parent',
                                        'default']

        self._load_hgrc()

        if not self.hg_root:
        svn_info = execute(["hg", "svn", "info"], ignore_errors=True)
        if (not svn_info.startswith('abort:') and
            not svn_info.startswith("hg: unknown command") and
            not svn_info.lower().startswith('not a child of')):
            return self._calculate_hgsubversion_repository_info(svn_info)
        self._type = 'hg'
        path = self.hg_root
        base_path = '/'
        if self.hgrc:
            self._calculate_remote_path()
            if self._remote_path:
                path = self._remote_path[1]
                base_path = ''
        return RepositoryInfo(path=path, base_path=base_path,
                              supports_parent_diffs=True)
    def _calculate_remote_path(self):
        for candidate in self._remote_path_candidates:
            rc_key = 'paths.%s' % candidate
            if (not self._remote_path and self.hgrc.get(rc_key)):
                self._remote_path = (candidate, self.hgrc.get(rc_key))
                debug('Using candidate path %r: %r' % self._remote_path)
                return
    def _calculate_hgsubversion_repository_info(self, svn_info):
        self._type = 'svn'
        m = re.search(r'^Repository Root: (.+)$', svn_info, re.M)
            return None
        path = m.group(1)
        m2 = re.match(r'^(svn\+ssh|http|https|svn)://([-a-zA-Z0-9.]*@)(.*)$',
                        path)
        if m2:
            path = '%s://%s' % (m2.group(1), m2.group(3))
        m = re.search(r'^URL: (.+)$', svn_info, re.M)

        if not m:
            return None

        base_path = m.group(1)[len(path):] or "/"
        return RepositoryInfo(path=path, base_path=base_path,
                              supports_parent_diffs=True)

    @property
    def hg_root(self):
        if not self._hg_root:
            root = execute(['hg', 'root'], env=self._hg_env,
                           ignore_errors=True)

            if not root.startswith('abort:'):
                self._hg_root = root.strip()
            else:
                self._hg_root = '.'

        return self._hg_root

    def _load_hgrc(self):
        for line in execute(['hg', 'showconfig'], split_lines=True):
            key, value = line.split('=', 1)
            self.hgrc[key] = value.strip()

    def extract_summary(self, revision):
        """
        Extracts the first line from the description of the given changeset.
        """
        return execute(['hg', 'log', '-r%s' % revision, '--template',
                        r'{desc|firstline}\n'], env=self._hg_env)

    def extract_description(self, rev1, rev2):
        """
        Extracts all descriptions in the given revision range and concatenates
        them, most recent ones going first.
        """
        numrevs = len(execute([
            'hg', 'log', '-r%s:%s' % (rev2, rev1),
            '--follow', '--template', r'{rev}\n'], env=self._hg_env
        ).strip().split('\n'))

        return execute(['hg', 'log', '-r%s:%s' % (rev2, rev1),
                        '--follow', '--template',
                        r'{desc}\n\n', '--limit',
                        str(numrevs - 1)], env=self._hg_env).strip()
        files = files or []
        if self._type == 'svn':
            return self._get_hgsubversion_diff(files)
        else:
            return self._get_outgoing_diff(files)
    def _get_hgsubversion_diff(self, files):
        parent = execute(['hg', 'parent', '--svn', '--template',
                          '{node}\n']).strip()
        if options.parent_branch:
            parent = options.parent_branch

        if options.guess_summary and not options.summary:
            options.summary = self.extract_summary(".")

        if options.guess_description and not options.description:
            options.description = self.extract_description(parent, ".")

        return (execute(["hg", "diff", "--svn", '-r%s:.' % parent]), None)

    def _get_outgoing_diff(self, files):
        """
        When working with a clone of a Mercurial remote, we need to find
        out what the outgoing revisions are for a given branch.  It would
        be nice if we could just do `hg outgoing --patch <remote>`, but
        there are a couple of problems with this.

        For one, the server-side diff parser isn't yet equipped to filter out
        diff headers such as "comparing with..." and "changeset: <rev>:<hash>".
        Another problem is that the output of `outgoing` potentially includes
        changesets across multiple branches.

        In order to provide the most accurate comparison between one's local
        clone and a given remote -- something akin to git's diff command syntax
        `git diff <treeish>..<treeish>` -- we have to do the following:

            - get the name of the current branch
            - get a list of outgoing changesets, specifying a custom format
            - filter outgoing changesets by the current branch name
            - get the "top" and "bottom" outgoing changesets
            - use these changesets as arguments to `hg diff -r <rev> -r <rev>`


        Future modifications may need to be made to account for odd cases like
        having multiple diverged branches which share partial history -- or we
        can just punish developers for doing such nonsense :)
        """
        files = files or []
        remote = self._remote_path[0]
        if not remote and options.parent_branch:
            remote = options.parent_branch

        current_branch = execute(['hg', 'branch'], env=self._hg_env).strip()

        outgoing_changesets = \
            self._get_outgoing_changesets(current_branch, remote)

        top_rev, bottom_rev = \
            self._get_top_and_bottom_outgoing_revs(outgoing_changesets)

        full_command = ['hg', 'diff', '-r', str(bottom_rev), '-r',
                        str(top_rev)] + files

        return (execute(full_command, env=self._hg_env), None)

    def _get_outgoing_changesets(self, current_branch, remote):
        """
        Given the current branch name and a remote path, return a list
        of outgoing changeset numbers.
        """
        outgoing_changesets = []
        raw_outgoing = execute(['hg', '-q', 'outgoing', '--template',
                                'b:{branches}\nr:{rev}\n\n', remote],
                               env=self._hg_env)

        for pair in raw_outgoing.split('\n\n'):
            if not pair.strip():
                continue

            branch, rev = pair.strip().split('\n')

            branch_name = branch[len('b:'):].strip()
            branch_name = branch_name or 'default'
            revno = rev[len('r:'):]

            if branch_name == current_branch and revno.isdigit():
                debug('Found outgoing changeset %s for branch %r'
                      % (revno, branch_name))
                outgoing_changesets.append(int(revno))

        return outgoing_changesets

    def _get_top_and_bottom_outgoing_revs(cls, outgoing_changesets):
        # This is a classmethod rather than a func mostly just to keep the
        # module namespace clean.  Pylint told me to do it.
        top_rev = max(outgoing_changesets)
        bottom_rev = min(outgoing_changesets)
        bottom_rev = max([0, bottom_rev - 1])

        return top_rev, bottom_rev

    # postfix decorators to stay pre-2.5 compatible
    _get_top_and_bottom_outgoing_revs = \
        classmethod(_get_top_and_bottom_outgoing_revs)
        if self._type != 'hg':

        if options.guess_summary and not options.summary:
            options.summary = self.extract_summary(r2)

        if options.guess_description and not options.description:
            options.description = self.extract_description(r1, r2)

        return execute(["hg", "diff", "-r", r1, "-r", r2],
                       env=self._hg_env)

    def scan_for_server(self, repository_info):
        # Scan first for dot files, since it's faster and will cover the
        # user's $HOME/.reviewboardrc
        server_url = \
            super(MercurialClient, self).scan_for_server(repository_info)

        if not server_url and self.hgrc.get('reviewboard.url'):
            server_url = self.hgrc.get('reviewboard.url').strip()

        if not server_url and self._type == "svn":
            # Try using the reviewboard:url property on the SVN repo, if it
            # exists.
            prop = SVNClient().scan_for_server_property(repository_info)

            if prop:
                return prop

        return server_url
    def _strip_heads_prefix(self, ref):
        """ Strips prefix from ref name, if possible """
        return re.sub(r'^refs/heads/', '', ref)

        self.head_ref = execute(['git', 'symbolic-ref', '-q', 'HEAD']).strip()

        # what it is. We'll try SVN first, but only if there's a .git/svn
        # directory. Otherwise, it may attempt to create one and scan
        # revisions, which can be slow.
        git_svn_dir = os.path.join(git_dir, 'svn')
        if os.path.isdir(git_svn_dir) and len(os.listdir(git_svn_dir)) > 0:
            data = execute(["git", "svn", "info"], ignore_errors=True)

            m = re.search(r'^Repository Root: (.+)$', data, re.M)
                path = m.group(1)
                m = re.search(r'^URL: (.+)$', data, re.M)

                if m:
                    base_path = m.group(1)[len(path):] or "/"
                    m = re.search(r'^Repository UUID: (.+)$', data, re.M)

                    if m:
                        uuid = m.group(1)
                        self.type = "svn"
                        self.upstream_branch = options.parent_branch or \
                                               'master'

                        return SvnRepositoryInfo(path=path,
                                                 base_path=base_path,
                                                 uuid=uuid,
                                                 supports_parent_diffs=True)
            else:
                # Versions of git-svn before 1.5.4 don't (appear to) support
                # 'git svn info'.  If we fail because of an older git install,
                # here, figure out what version of git is installed and give
                # the user a hint about what to do next.
                version = execute(["git", "svn", "--version"],
                                  ignore_errors=True)
                version_parts = re.search('version (\d+)\.(\d+)\.(\d+)',
                                          version)
                svn_remote = execute(["git", "config", "--get",
                                      "svn-remote.svn.url"],
                                      ignore_errors=True)

                if (version_parts and
                    not self.is_valid_version((int(version_parts.group(1)),
                                               int(version_parts.group(2)),
                                               int(version_parts.group(3))),
                                              (1, 5, 4)) and
                    svn_remote):
                    die("Your installation of git-svn must be upgraded to "
                        "version 1.5.4 or later")
        # Check for a tracking branch and determine merge-base
        short_head = self._strip_heads_prefix(self.head_ref)
        merge = execute(['git', 'config', '--get',
                         'branch.%s.merge' % short_head],
                        ignore_errors=True).strip()
        remote = execute(['git', 'config', '--get',
                          'branch.%s.remote' % short_head],
                         ignore_errors=True).strip()

        merge = self._strip_heads_prefix(merge)
        self.upstream_branch = ''

        if remote and remote != '.' and merge:
            self.upstream_branch = '%s/%s' % (remote, merge)

        self.upstream_branch, origin_url = self.get_origin(self.upstream_branch,
                                                       True)

        if not origin_url or origin_url.startswith("fatal:"):
            self.upstream_branch, origin_url = self.get_origin()

        url = origin_url.rstrip('/')
        if url:
            self.type = "git"
            return RepositoryInfo(path=url, base_path='',
                                  supports_parent_diffs=True)
    def get_origin(self, default_upstream_branch=None, ignore_errors=False):
        """Get upstream remote origin from options or parameters.

        Returns a tuple: (upstream_branch, remote_url)
        """
        upstream_branch = options.tracking or default_upstream_branch or \
                          'origin/master'
        upstream_remote = upstream_branch.split('/')[0]
        origin_url = execute(["git", "config", "remote.%s.url" % upstream_remote],
                         ignore_errors=ignore_errors)

        return (upstream_branch, origin_url.rstrip('\n'))

        parent_branch = options.parent_branch
        self.merge_base = execute(["git", "merge-base", self.upstream_branch,
                                   self.head_ref]).strip()
        if parent_branch:
            diff_lines = self.make_diff(parent_branch)
            parent_diff_lines = self.make_diff(self.merge_base, parent_branch)
            diff_lines = self.make_diff(self.merge_base, self.head_ref)
                ["git", "log", "--pretty=format:%s%n%n%b",
                 (parent_branch or self.merge_base) + ".."],
    def make_diff(self, ancestor, commit=""):
        rev_range = "%s..%s" % (ancestor, commit)

                                  "--no-ext-diff", "-r", "-u", rev_range],
            return self.make_svn_diff(ancestor, diff_lines)
                            "--no-ext-diff", rev_range])
        rev = execute(["git", "svn", "find-rev", parent_branch]).strip()
            elif line.startswith("new file mode"):
                # Filter this out.
                pass
            elif line.startswith("Binary files "):
                # Add the following so that we know binary files were added/changed
                diff_data += "Cannot display: file marked as a binary type.\n"
                diff_data += "svn:mime-type = application/octet-stream\n"
        """Perform a diff between two arbitrary revisions"""
        if ":" not in revision_range:
            # only one revision is specified
            if options.guess_summary and not options.summary:
                options.summary = execute(
                    ["git", "log", "--pretty=format:%s", revision_range + ".."],
                    ignore_errors=True).strip()

            if options.guess_description and not options.description:
                options.description = execute(
                    ["git", "log", "--pretty=format:%s%n%n%b", revision_range + ".."],
                    ignore_errors=True).strip()

            return self.make_diff(revision_range)
        else:
            r1, r2 = revision_range.split(":")

            if options.guess_summary and not options.summary:
                options.summary = execute(
                    ["git", "log", "--pretty=format:%s", "%s..%s" % (r1, r2)],
                    ignore_errors=True).strip()

            if options.guess_description and not options.description:
                options.description = execute(
                    ["git", "log", "--pretty=format:%s%n%n%b", "%s..%s" % (r1, r2)],
                    ignore_errors=True).strip()

            return self.make_diff(r1, r2)


class PlasticClient(SCMClient):
    """
    A wrapper around the cm Plastic tool that fetches repository
    information and generates compatible diffs
    """
    def get_repository_info(self):
        if not check_install('cm version'):
            return None

        # Get the repository that the current directory is from.  If there
        # is more than one repository mounted in the current directory,
        # bail out for now (in future, should probably enter a review
        # request per each repository.)
        split = execute(["cm", "ls", "--format={8}"], split_lines=True,
                        ignore_errors=True)
        m = re.search(r'^rep:(.+)$', split[0], re.M)

        if not m:
            return None

        # Make sure the repository list contains only one unique entry
        if len(split) != split.count(split[0]):
            # Not unique!
            die('Directory contains more than one mounted repository')

        path = m.group(1)

        # Get the workspace directory, so we can strip it from the diff output
        self.workspacedir = execute(["cm", "gwp", ".", "--format={1}"],
                                    split_lines=False,
                                    ignore_errors=True).strip()

        debug("Workspace is %s" % self.workspacedir)

        return RepositoryInfo(path,
                              supports_changesets=True,
                              supports_parent_diffs=False)

    def get_changenum(self, args):
        """ Extract the integer value from a changeset ID (cs:1234) """
        if len(args) == 1 and args[0].startswith("cs:"):
                try:
                    return str(int(args[0][3:]))
                except ValueError:
                    pass

        return None

    def sanitize_changenum(self, changenum):
        """ Return a "sanitized" change number.  Currently a no-op """
        return changenum

    def diff(self, args):
        """
        Performs a diff across all modified files in a Plastic workspace

        Parent diffs are not supported (the second value in the tuple).
        """
        changenum = self.get_changenum(args)

        if changenum is None:
            return self.branch_diff(args), None
        else:
            return self.changenum_diff(changenum), None

    def diff_between_revisions(self, revision_range, args, repository_info):
        """
        Performs a diff between 2 revisions of a Plastic repository.

        Assume revision_range is a branch specification (br:/main/task001)
        and hand over to branch_diff
        """
        return self.branch_diff(revision_range)

    def changenum_diff(self, changenum):
        debug("changenum_diff: %s" % (changenum))
        files = execute(["cm", "log", "cs:" + changenum,
                         "--csFormat={items}",
                         "--itemFormat={shortstatus} {path} "
                         "rev:revid:{revid} rev:revid:{parentrevid} "
                         "src:{srccmpath} rev:revid:{srcdirrevid} "
                         "dst:{dstcmpath} rev:revid:{dstdirrevid}{newline}"],
                        split_lines = True)

        debug("got files: %s" % (files))

        # Diff generation based on perforce client
        diff_lines = []

        empty_filename = make_tempfile()
        tmp_diff_from_filename = make_tempfile()
        tmp_diff_to_filename = make_tempfile()

        for f in files:
            f = f.strip()

            if not f:
                continue

            m = re.search(r'(?P<type>[ACIMR]) (?P<file>.*) '
                          r'(?P<revspec>rev:revid:[-\d]+) '
                          r'(?P<parentrevspec>rev:revid:[-\d]+) '
                          r'src:(?P<srcpath>.*) '
                          r'(?P<srcrevspec>rev:revid:[-\d]+) '
                          r'dst:(?P<dstpath>.*) '
                          r'(?P<dstrevspec>rev:revid:[-\d]+)$',
                          f)
            if not m:
                die("Could not parse 'cm log' response: %s" % f)

            changetype = m.group("type")
            filename = m.group("file")

            if changetype == "M":
                # Handle moved files as a delete followed by an add.
                # Clunky, but at least it works
                oldfilename = m.group("srcpath")
                oldspec = m.group("srcrevspec")
                newfilename = m.group("dstpath")
                newspec = m.group("dstrevspec")

                self.write_file(oldfilename, oldspec, tmp_diff_from_filename)
                dl = self.diff_files(tmp_diff_from_filename, empty_filename,
                                     oldfilename, "rev:revid:-1", oldspec,
                                     changetype)
                diff_lines += dl

                self.write_file(newfilename, newspec, tmp_diff_to_filename)
                dl = self.diff_files(empty_filename, tmp_diff_to_filename,
                                     newfilename, newspec, "rev:revid:-1",
                                     changetype)
                diff_lines += dl
            else:
                newrevspec = m.group("revspec")
                parentrevspec = m.group("parentrevspec")

                debug("Type %s File %s Old %s New %s" % (changetype,
                                                         filename,
                                                         parentrevspec,
                                                         newrevspec))

                old_file = new_file = empty_filename

                if (changetype in ['A'] or
                    (changetype in ['C', 'I'] and
                     parentrevspec == "rev:revid:-1")):
                    # File was Added, or a Change or Merge (type I) and there
                    # is no parent revision
                    self.write_file(filename, newrevspec, tmp_diff_to_filename)
                    new_file = tmp_diff_to_filename
                elif changetype in ['C', 'I']:
                    # File was Changed or Merged (type I)
                    self.write_file(filename, parentrevspec,
                                    tmp_diff_from_filename)
                    old_file = tmp_diff_from_filename
                    self.write_file(filename, newrevspec, tmp_diff_to_filename)
                    new_file = tmp_diff_to_filename
                elif changetype in ['R']:
                    # File was Removed
                    self.write_file(filename, parentrevspec,
                                    tmp_diff_from_filename)
                    old_file = tmp_diff_from_filename
                else:
                    die("Don't know how to handle change type '%s' for %s" %
                        (changetype, filename))

                dl = self.diff_files(old_file, new_file, filename,
                                     newrevspec, parentrevspec, changetype)
                diff_lines += dl

        os.unlink(empty_filename)
        os.unlink(tmp_diff_from_filename)
        os.unlink(tmp_diff_to_filename)

        return ''.join(diff_lines)

    def branch_diff(self, args):
        debug("branch diff: %s" % (args))

        if len(args) > 0:
            branch = args[0]
        else:
            branch = args

        if not branch.startswith("br:"):
            return None

        if not options.branch:
            options.branch = branch

        files = execute(["cm", "fbc", branch, "--format={3} {4}"],
                        split_lines = True)
        debug("got files: %s" % (files))

        diff_lines = []

        empty_filename = make_tempfile()
        tmp_diff_from_filename = make_tempfile()
        tmp_diff_to_filename = make_tempfile()

        for f in files:
            f = f.strip()

            if not f:
                continue

            m = re.search(r'^(?P<branch>.*)#(?P<revno>\d+) (?P<file>.*)$', f)

            if not m:
                die("Could not parse 'cm fbc' response: %s" % f)

            filename = m.group("file")
            branch = m.group("branch")
            revno = m.group("revno")

            # Get the base revision with a cm find
            basefiles = execute(["cm", "find", "revs", "where",
                                 "item='" + filename + "'", "and",
                                 "branch='" + branch + "'", "and",
                                 "revno=" + revno,
                                 "--format={item} rev:revid:{id} "
                                 "rev:revid:{parent}", "--nototal"],
                                split_lines = True)

            # We only care about the first line
            m = re.search(r'^(?P<filename>.*) '
                              r'(?P<revspec>rev:revid:[-\d]+) '
                              r'(?P<parentrevspec>rev:revid:[-\d]+)$',
                              basefiles[0])
            basefilename = m.group("filename")
            newrevspec = m.group("revspec")
            parentrevspec = m.group("parentrevspec")

            # Cope with adds/removes
            changetype = "C"

            if parentrevspec == "rev:revid:-1":
                changetype = "A"
            elif newrevspec == "rev:revid:-1":
                changetype = "R"

            debug("Type %s File %s Old %s New %s" % (changetype,
                                                     basefilename,
                                                     parentrevspec,
                                                     newrevspec))

            old_file = new_file = empty_filename

            if changetype == "A":
                # File Added
                self.write_file(basefilename, newrevspec,
                                tmp_diff_to_filename)
                new_file = tmp_diff_to_filename
            elif changetype == "R":
                # File Removed
                self.write_file(basefilename, parentrevspec,
                                tmp_diff_from_filename)
                old_file = tmp_diff_from_filename
            else:
                self.write_file(basefilename, parentrevspec,
                                tmp_diff_from_filename)
                old_file = tmp_diff_from_filename

                self.write_file(basefilename, newrevspec,
                                tmp_diff_to_filename)
                new_file = tmp_diff_to_filename

            dl = self.diff_files(old_file, new_file, basefilename,
                                 newrevspec, parentrevspec, changetype)
            diff_lines += dl

        os.unlink(empty_filename)
        os.unlink(tmp_diff_from_filename)
        os.unlink(tmp_diff_to_filename)

        return ''.join(diff_lines)

    def diff_files(self, old_file, new_file, filename, newrevspec,
                   parentrevspec, changetype, ignore_unmodified=False):
        """
        Do the work of producing a diff for Plastic (based on the Perforce one)

        old_file - The absolute path to the "old" file.
        new_file - The absolute path to the "new" file.
        filename - The file in the Plastic workspace
        newrevspec - The revid spec of the changed file
        parentrevspecspec - The revision spec of the "old" file
        changetype - The change type as a single character string
        ignore_unmodified - If true, will return an empty list if the file
            is not changed.

        Returns a list of strings of diff lines.
        """
        if filename.startswith(self.workspacedir):
            filename = filename[len(self.workspacedir):]

        diff_cmd = ["diff", "-urN", old_file, new_file]
        # Diff returns "1" if differences were found.
        dl = execute(diff_cmd, extra_ignore_errors=(1,2),
                     translate_newlines = False)

        # If the input file has ^M characters at end of line, lets ignore them.
        dl = dl.replace('\r\r\n', '\r\n')
        dl = dl.splitlines(True)

        # Special handling for the output of the diff tool on binary files:
        #     diff outputs "Files a and b differ"
        # and the code below expects the output to start with
        #     "Binary files "
        if (len(dl) == 1 and
            dl[0].startswith('Files %s and %s differ' % (old_file, new_file))):
            dl = ['Binary files %s and %s differ\n' % (old_file, new_file)]

        if dl == [] or dl[0].startswith("Binary files "):
            if dl == []:
                if ignore_unmodified:
                    return []
                else:
                    print "Warning: %s in your changeset is unmodified" % \
                          filename

            dl.insert(0, "==== %s (%s) ==%s==\n" % (filename, newrevspec,
                                                    changetype))
            dl.append('\n')
        else:
            dl[0] = "--- %s\t%s\n" % (filename, parentrevspec)
            dl[1] = "+++ %s\t%s\n" % (filename, newrevspec)

            # Not everybody has files that end in a newline.  This ensures
            # that the resulting diff file isn't broken.
            if dl[-1][-1] != '\n':
                dl.append('\n')

        return dl

    def write_file(self, filename, filespec, tmpfile):
        """ Grabs a file from Plastic and writes it to a temp file """
        debug("Writing '%s' (rev %s) to '%s'" % (filename, filespec, tmpfile))
        execute(["cm", "cat", filespec, "--file=" + tmpfile])
    PlasticClient(),
def check_gnu_diff():
    """Checks if GNU diff is installed, and informs the user if it's not."""
    has_gnu_diff = False

    try:
        result = execute(['diff', '--version'], ignore_errors=True)
        has_gnu_diff = 'GNU diffutils' in result
    except OSError:
        pass

    if not has_gnu_diff:
        sys.stderr.write('\n')
        sys.stderr.write('GNU diff is required for Subversion '
                         'repositories. Make sure it is installed\n')
        sys.stderr.write('and in the path.\n')
        sys.stderr.write('\n')

        if os.name == 'nt':
            sys.stderr.write('On Windows, you can install this from:\n')
            sys.stderr.write(GNU_DIFF_WIN32_URL)
            sys.stderr.write('\n')

        die()


        except SyntaxError, e:
            die('Syntax error in config file: %s\n'
                'Line %i offset %i\n' % (filename, e.lineno, e.offset))
        if options.bugs_closed:     # append to existing list
            options.bugs_closed = options.bugs_closed.strip(", ")
            bug_set = set(re.split("[, ]+", options.bugs_closed)) | \
                      set(review_request['bugs_closed'])
            options.bugs_closed = ",".join(bug_set)
        if e.error_code == 103: # Not logged in
            die("Error getting review request %s: %s" % (options.rid, e))
            die("Error creating review request: %s" % e)
            sys.stderr.write('\n')
            sys.stderr.write('Error uploading diff\n')
            sys.stderr.write('\n')

            if e.error_code == 105:
                sys.stderr.write('The generated diff file was empty. This '
                                 'usually means no files were\n')
                sys.stderr.write('modified in this change.\n')
                sys.stderr.write('\n')
                sys.stderr.write('Try running with --output-diff and --debug '
                                 'for more information.\n')
                sys.stderr.write('\n')

    if options.reopen:
        server.reopen(review_request)

    request_url = 'r/' + str(review_request['id']) + '/'
                          version="RBTools " + get_version_string())
    parser.add_option("--reopen",
                      dest="reopen", action="store_true", default=False,
                      help="reopen discarded review request "
                           "after update")
                           "hg/hgsubversion only)")
                           "(git/hg/hgsubversion only)")
    parser.add_option("--tracking-branch",
                      dest="tracking", default=None,
                      metavar="TRACKING",
                      help="Tracking branch from which your branch is derived "
                           "(git only, defaults to origin/master)")
    parser.add_option("--p4-passwd",
                      dest="p4_passwd", default=None,
                      help="the Perforce password or ticket of the user in the P4USER environment variable")
                           "outside of a working copy (currently only "
                           "supported by Subversion with --revision-range or "
                           "--diff-filename and ClearCase with relative "
                           "paths outside the view)")
    parser.add_option("--diff-filename",
                      dest="diff_filename", default=None,
                      help='upload an existing diff file, instead of '
                           'generating a new diff')
    if options.reopen and not options.rid:
        sys.stderr.write("The --reopen option requires "
                         "--review-request-id option.\n")
def determine_client():

    origcwd = os.path.abspath(os.getcwd())

    if 'APPDATA' in os.environ:
        homepath = os.environ['APPDATA']
    debug('RBTools %s' % get_version_string())
    debug('Home = %s' % homepath)

    # Verify that options specific to an SCM Client have not been mis-used.
    tool.check_options()

    elif options.diff_filename:
        parent_diff = None

        if options.diff_filename == '-':
            diff = sys.stdin.read()
        else:
            try:
                fp = open(os.path.join(origcwd, options.diff_filename), 'r')
                diff = fp.read()
                fp.close()
            except IOError, e:
                die("Unable to open diff filename: %s" % e)
    if len(diff) == 0:
        die("There don't seem to be any diffs!")

    if (isinstance(tool, PerforceClient) or
        isinstance(tool, PlasticClient)) and changenum is not None:
        changenum = tool.sanitize_changenum(changenum)

        # The comma here isn't a typo, but rather suppresses the extra newline
        print diff,