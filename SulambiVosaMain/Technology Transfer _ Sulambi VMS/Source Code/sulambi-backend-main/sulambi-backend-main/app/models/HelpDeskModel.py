from .Model import Model

class HelpDeskModel(Model):
  def __init__(self):
    self.primaryKey = "id"
    self.columns = [
      "email",
      "nameOfRequestee",
      "addressOfRequestee",
      "contactOfRequestee",
      "fblinkOfRequestee",
      "donationType",
      "nameOfMoneyRecipient",
      "addressOfRecipient",
      "contactOfRecipient",
      "gcashOrBankOfRecipient",
      "reason",
      "bloodTypeOfRecipient",
      "necessaryFiles",
      "donationNeeded"
    ]

    super().__init__()

  def create(self,
      email: str,
      nameOfRequestee: str,
      addressOfRequestee: str,
      contactOfRequestee: str,
      fblinkOfRequestee: str,
      donationType: int,
      nameOfMoneyRecipient: str,
      addressOfRecipient: str,
      contactOfRecipient: str,
      gcashOrBankOfRecipient: str,
      reason: str,
      bloodTypeOfRecipient: str,
      necessaryFiles: str,
      donationNeeded: str):

    return super().create((
      email,
      nameOfRequestee,
      addressOfRequestee,
      contactOfRequestee,
      fblinkOfRequestee,
      donationType,
      nameOfMoneyRecipient,
      addressOfRecipient,
      contactOfRecipient,
      gcashOrBankOfRecipient,
      reason,
      bloodTypeOfRecipient,
      necessaryFiles,
      donationNeeded,
    ))
