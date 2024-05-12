import hashlib

from hoyt.extensions import db

from lib.util_sqlalchemy import ResourceMixin


class Obj:
    def __str__(self):
        return '\n'.join('{} => {}'.format(k, self.__dict__[k])
                         for k in self.__dict__)


class Attribute(db.Model):
    __tablename__ = 'attributes'  # plural lower-case
    id = db.Column(db.Integer, primary_key=True)

    # Details.
    request = db.Column(db.Text, nullable=False)
    key = db.Column(db.Text, nullable=False)
    value = db.Column(db.Text, nullable=False)

    @classmethod
    def attribute_dict(cls, request):
        o = Obj()
        for row in Attribute.query.filter_by(request=request).all():
            o.__dict__[row.key] = row.value
        return o


class LastModified(ResourceMixin, db.Model):
    __tablename__ = 'pages_last_modified'
    id = db.Column(db.Integer, primary_key=True)

    # Details.
    request = db.Column(db.Text, nullable=False)
    checksum = db.Column(db.Text)

    @property
    def sitemap_date(self):
        return self.updated_on.strftime("%Y-%m-%d")

    def strftime(self, _format):
        return self.update_on.strftime(_format)

    def update_time(self, source):
        new_checksum = LastModified.create_checksum(source)
        if new_checksum != self.checksum:
            self.checksum = new_checksum
        self.save()

    @classmethod
    def create_checksum(cls, text):
        m = hashlib.md5()
        m.update(text.encode('utf-8', 'ignore'))
        return m.hexdigest()

    @classmethod
    def select(cls, request):
        result = LastModified.query.filter_by(request=request).first()
        if not result:
            page = LastModified(request=request)
            db.session.add(page)
            db.session.commit()
            return page
        return result
