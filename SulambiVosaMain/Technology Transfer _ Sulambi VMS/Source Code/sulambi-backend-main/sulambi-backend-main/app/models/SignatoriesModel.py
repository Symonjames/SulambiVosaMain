from .Model import Model

class SignatoriesModel(Model):
  def __init__(self):
    super().__init__()

    self.table = "eventSignatories"
    self.primaryKey = "id"
    self.columns = [
      "preparedBy",
      "reviewedBy",
      "recommendingApproval1",
      "recommendingApproval2",
      "approvedBy",

      # for review purposes
      "preparedTitle",
      "reviewedTitle",
      "approvedTitle",
      "recommendingSignatory1",
      "recommendingSignatory2"
    ]

  def create(self,
    preparedBy: str,
    reviewedBy: str,
    recommendingApproval1: str,
    recommendingApproval2: str,
    approvedBy: str,
    preparedTitle: str = "Asst. Director, GAD Advocacies/GAD Head Secretariat/Coordinator",
    reviewedTitle: str = "Director, Extension Services/Head, Extension Services",
    approvedTitle: str = "University President/Chancellor",
    recommendingSignatory1: str = "Vice President/Vice Chancellor for Research, Development and Extension Services",
    recommendingSignatory2: str = "Vice President/Vice Chancellor for Administration and Finance"):

    return super().create((
      preparedBy,
      reviewedBy,
      recommendingApproval1,
      recommendingApproval2,
      approvedBy,
      preparedTitle,
      reviewedTitle,
      approvedTitle,
      recommendingSignatory1,
      recommendingSignatory2
    ))