"""
Custom session serializer for MongoDB ObjectId compatibility
"""

from django.core.signing import JSONSerializer as DjangoJSONSerializer
import json
from bson import ObjectId


class MongoJSONSerializer(DjangoJSONSerializer):
    """
    Custom JSON serializer that handles MongoDB ObjectId
    """
    
    def dumps(self, obj):
        """Serialize object to JSON, converting ObjectId to string"""
        return json.dumps(obj, separators=(',', ':'), cls=MongoJSONEncoder).encode('latin-1')
    
    def loads(self, data):
        """Deserialize JSON to object"""
        return json.loads(data.decode('latin-1'))


class MongoJSONEncoder(json.JSONEncoder):
    """
    JSON encoder that converts MongoDB ObjectId to string
    """
    
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoJSONEncoder, self).default(obj)
