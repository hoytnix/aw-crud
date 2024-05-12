import warnings

from flask_frozen import Freezer as _Freezer


class RedirectWarning(Warning):
    pass


class Freezer(_Freezer):
    """Customized for blocking endpoints."""

    def init_app(self, app):
        """Include configuration option."""
        super(Freezer, self).init_app(app)
        app.config.setdefault('FREEZER_ENDPOINT_BLACKLIST', [])
        app.config.setdefault('FREEZER_URL_BLACKLIST', [])

    def _generate_all_urls(self):
        for url, endpoint in super(Freezer, self)._generate_all_urls():
            white = True
            # Endpoints
            eb = self.app.config['FREEZER_ENDPOINT_BLACKLIST']
            for black in eb:
                if black in endpoint:
                    white = False

            # Urls
            ub = self.app.config['FREEZER_URL_BLACKLIST']
            for black in ub:
                if black in url:
                    white = False

            if white:
                yield url, endpoint

    def _build_one(self, url):
        "Wrapping parent _build_one to not make 405 files"
        try:
            # normal build, raising 405 if needed
            filename = super(Freezer, self)._build_one(url)

        except ValueError as e:
            if '405' in str(e):
                warnings.warn('Ignored 405', RedirectWarning, stacklevel=3)
            filename = '404.txt'

        return filename
