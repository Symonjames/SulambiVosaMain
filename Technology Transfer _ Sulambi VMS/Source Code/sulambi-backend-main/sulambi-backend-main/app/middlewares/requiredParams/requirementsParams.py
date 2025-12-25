from ..paramcheck import basicParamFileCheck, basicParamFormCheck

def requirementsParamCheck():
  from flask import request
  
  # Debug: Log what files are received
  print(f"[requirementsParams] request.files keys: {list(request.files.keys())}")
  for key in request.files:
    file = request.files[key]
    print(f"[requirementsParams] {key}: filename={file.filename}, content_type={file.content_type}")
  
  # Only require file uploads (medCert and waiver)
  missingParams = basicParamFileCheck([
    "medCert",
    "waiver",
  ])
  
  print(f"[requirementsParams] missingParams: {missingParams}")

  # Form fields (fullname, email, srcode, age, birthday, sex) are optional
  # They can be provided if available, but are not required

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": f"Missing required fields: {', '.join(missingParams)}"
    }, 400)
