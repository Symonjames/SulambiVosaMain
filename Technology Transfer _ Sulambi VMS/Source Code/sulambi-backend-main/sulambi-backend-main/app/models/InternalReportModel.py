from .Model import Model

class InternalReportModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "internalReport"
    self.primaryKey = "id"
    self.columns = [
      "eventId",
      "narrative",
      "budgetUtilized",
      "budgetUtilizedSrc",
      "psAttribution",
      "psAttributionSrc",
      "photos",
      "photoCaptions",
      "signatoriesId"
    ]


  def create(self, eventId: int, narrative: str, budgetUtilized: int, budgetUtilizedSrc: str, psAttribution: int, psAttributionSrc: str, photos, photoCaptions: str, signatoriesId: int=None):
    return super().create((
      eventId, narrative, budgetUtilized, budgetUtilizedSrc, psAttribution, psAttributionSrc, photos, photoCaptions, signatoriesId
    ))