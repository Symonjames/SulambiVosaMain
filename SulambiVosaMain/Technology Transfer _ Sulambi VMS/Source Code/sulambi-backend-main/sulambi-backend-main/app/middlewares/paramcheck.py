from flask import request
import json

def basicParamCheck(params: list[str], paramStringify: bool=False):
  requestJson: dict = request.json
  requestParams = list(requestJson.keys())
  missingParams = []

  for requiredParams in params:
    if (requiredParams not in requestParams):
      missingParams.append(requiredParams)
      continue

    if (paramStringify and (
        type(requestJson[requiredParams]) is dict or
        type(requestJson[requiredParams]) is list)):
      requestJson[requiredParams] = json.dumps(requestJson[requiredParams])

  return missingParams

def basicParamFileCheck(params: list[str], paramStringify: bool=False):
  from flask import request
  
  requestJson: dict = request.files
  requestParams = list(requestJson.keys())
  missingParams = []
  
  # Debug logging
  print(f"[basicParamFileCheck] Looking for params: {params}")
  print(f"[basicParamFileCheck] Found files: {requestParams}")

  for requiredParams in params:
    if (requiredParams not in requestParams):
      print(f"[basicParamFileCheck] Missing: {requiredParams} (not in request.files)")
      missingParams.append(requiredParams)
      continue
    
    # Check if file actually has content (has a filename)
    file = requestJson.get(requiredParams)
    if file:
      print(f"[basicParamFileCheck] Found {requiredParams}: type={type(file)}, hasattr filename={hasattr(file, 'filename')}")
      if hasattr(file, 'filename'):
        filename = file.filename
        print(f"[basicParamFileCheck] {requiredParams} filename: '{filename}'")
        if not filename or filename.strip() == "":
          print(f"[basicParamFileCheck] Missing: {requiredParams} (empty filename)")
          missingParams.append(requiredParams)
          continue
      else:
        print(f"[basicParamFileCheck] {requiredParams} doesn't have filename attribute")
    else:
      print(f"[basicParamFileCheck] {requiredParams} is None or empty")

    if (paramStringify and (type(requestJson[requiredParams]) is dict or type(requestJson[requiredParams]) is list)):
      requestJson[requiredParams] = json.dumps(requestJson[requiredParams])

  print(f"[basicParamFileCheck] Final missingParams: {missingParams}")
  return missingParams

def basicParamFormCheck(params: list[str], paramStringify: bool=False):
  requestJson: dict = request.form
  requestParams = list(requestJson.keys())
  missingParams = []

  for requiredParams in params:
    if (requiredParams not in requestParams):
      missingParams.append(requiredParams)
      continue

    if (requestJson.get(requiredParams) == None or requestJson.get(requiredParams) == ""):
      missingParams.append(requiredParams)
      continue


    if (paramStringify and (type(requestJson[requiredParams]) is dict or type(requestJson[requiredParams]) is list)):
      requestJson[requiredParams] = json.dumps(requestJson[requiredParams])

  return missingParams