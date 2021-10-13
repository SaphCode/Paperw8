import os
from gbpartners.configuration.config import DevelopmentConfig

from flask import Flask
from flask_pagedown import PageDown

import sys

from pathlib import Path

class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DevelopmentConfig())
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        # already exists
        pass
    
    paths = DisplayablePath.make_tree(Path(os.getcwd()))
    for path in paths:
        print(path.displayable())
    sys.stdout.flush()

    
    # override config with env_variable_config
    app.config.from_envvar('GBPARTNERS_SETTINGS')

    # import db commands & functionality
    from gbpartners.database import db
    db.init_app(app)

    # import login module
    from gbpartners.user import auth
    app.register_blueprint(auth.bp)
    
    # import admin module
    from gbpartners.data_processing import admin
    app.register_blueprint(admin.bp)
    
    # import chart module and set as home
    from gbpartners.data_processing import performance
    app.register_blueprint(performance.bp)
    app.add_url_rule('/', endpoint='performance')
    
    # load pagedown module for blog
    pagedown = PageDown(app)
    # import blog module
    from gbpartners.blog import blog
    app.register_blueprint(blog.bp)
    
    # import user module
    from gbpartners.user import user
    app.register_blueprint(user.bp)
    
    # import contact module
    from gbpartners.contact import contact
    app.register_blueprint(contact.bp)

    return app