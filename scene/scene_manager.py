"""Container for the objects in one synthetic scene."""
class SceneManager:
    def __init__(self, objects=None):
        self.objects = list(objects or [])
        ids = [obj.instance_id for obj in self.objects]
        if len(ids) != len(set(ids)):
            raise ValueError("Every object must have a unique instance_id")

    def add(self, obj):
        if any(existing.instance_id == obj.instance_id for existing in self.objects):
            raise ValueError(f"Duplicate instance_id: {obj.instance_id}")
        self.objects.append(obj)

    def metadata(self):
        return [obj.metadata() for obj in self.objects]
