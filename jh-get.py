"""
A service that downloads a file to a user's jupyter instance and forwards the user's browser to the downloaded file.

Call it with http://{jupyterhub_url}/services/get/?path={path to notebook dl}
"""
from getpass import getuser
import os

from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import urlopen

from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import RequestHandler, Application, authenticated

from jupyterhub.services.auth import HubAuthenticated


class GetHandler(HubAuthenticated, RequestHandler):
    hub_users = {getuser()} # the users allowed to access me

    @authenticated
    @coroutine
    def get(self):
        user_model = self.get_current_user()
        get_path = self.get_argument('path', '')

        if get_path != '':
            #fetch from url
            try:
                file_contents = urlopen(get_path).read().decode('utf-8')
                put_filename = os.path.basename(get_path)

                #the path to save to
                put_path = os.environ['JUPYTERHUB_USER_PATH'].format(user=user_model['name'])

                #accept extensionless?
                if '.' not in put_filename:
                    put_filename += '.ipynb'
                #check filename
                file_type = put_filename.split('.')[-1]
                if file_type != 'ipynb':
                    raise ValueError('File type {} not allowed'.format(file_type))

                #rename loop in case file exists
                if os.path.exists(os.path.join(put_path, put_filename)):
                    rename_counter = 1
                    root = put_filename.rsplit('.', 1)[0]
                    suffix = put_filename.split('.')[-1]
                    while os.path.exists(os.path.join(put_path, put_filename)):
                        put_filename = '{}.{}.{}'.format(root, rename_counter, suffix)
                        rename_counter += 1

                with open(os.path.join(put_path, put_filename), 'wb') as outfile:
                    outfile.write(file_contents.encode('utf-8'))

                #ensure ownership is same as folder it's in
                put_own = os.stat(put_path)
                os.chown(os.path.join(put_path, put_filename), put_own.st_uid, put_own.st_gid)

                #redirect
                self.redirect(os.environ['JUPYTERHUB_BASE_URL']+ 'user/' + user_model['name'] +'/tree/'+ put_filename)

            except HTTPError:
                error = ('Source file "{}" does not exist or is not accessible.'.format(get_path))
                self.write(error)
            except Exception as e:
                error = ('Unhandled error: {}'.format(e))
                self.write(error)


def main():
    app = Application([
        (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + '/?', GetHandler),
        (r'.*', GetHandler),
    ], login_url='/hub/login')
    
    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    http_server.listen(url.port, url.hostname)

    IOLoop.current().start()



if __name__ == '__main__':
    main()
