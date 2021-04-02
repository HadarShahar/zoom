"""
    Hadar Shahar
    ClientInfo.
"""


class ClientInfo(object):
    """ Definition of the class ClientInfo. """

    def __init__(self, client_id: bytes, meeting_id: bytes, name: str,
                 img_url='', is_audio_on=True, is_video_on=True):
        """ Constructor. """
        self.id = client_id
        self.meeting_id = meeting_id
        self.name = name
        self.img_url = img_url
        self.is_audio_on = is_audio_on
        self.is_video_on = is_video_on

    def __repr__(self) -> str:
        """ Returns the ClientInfo representation. """
        return f'ClientInfo({self.json()})'

    def json(self) -> dict:
        """
        Returns the json representation of the object,
        bytes values represented as hex digits.
        """
        d = self.__dict__.copy()
        # convert the ids to hex representation
        d['id'] = d['id'].hex()
        d['meeting_id'] = d['meeting_id'].hex()
        return d

    @classmethod
    def from_json(cls, json_dict: dict):
        """ Factory method which creates an object from json. """
        d = json_dict.copy()
        # the ids are represented as hex digits in the json object
        d['id'] = bytes.fromhex(d['id'])
        d['meeting_id'] = bytes.fromhex(d['meeting_id'])

        client_info = cls(b'', b'', '')
        client_info.__dict__ = d
        return client_info


if __name__ == '__main__':
    info = ClientInfo(b'1', b'2', 'name')
    json_d = info.json()
    print(json_d)
    print(ClientInfo.from_json(json_d))

