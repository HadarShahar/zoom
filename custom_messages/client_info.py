"""
    Hadar Shahar
    ClientInfo.
"""


class ClientInfo(object):
    """ Definition of the class ClientInfo. """

    def __init__(self,  client_id: bytes, name: str,
                 img_url='', is_audio_on=True, is_video_on=True):
        """ Constructor. """
        self.id = client_id
        self.name = name
        self.img_url = img_url
        self.is_audio_on = is_audio_on
        self.is_video_on = is_video_on

    def __repr__(self) -> str:
        """ Returns the ClientInfo representation. """
        return f'ClientInfo({self.__dict__})'

    @classmethod
    def from_json(cls, json: dict):
        """ Factory method which creates an object from json. """
        return cls(json['id'].encode(), json['name'], json.get('img_url', ''))
