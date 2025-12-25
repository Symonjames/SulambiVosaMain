from .Model import Model

class ExternalReportModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "externalReport"
    self.primaryKey = "id"
    self.columns = [
      "eventId",
      "narrative",
      "photos",
      "photoCaptions",
      "signatoriesId"
    ]


  def create(self, eventId: int, narrative: str, photos: str, photoCaptions: str, signatoriesId: int=None):
    return super().create((
      eventId, narrative, photos, photoCaptions, signatoriesId
    ))