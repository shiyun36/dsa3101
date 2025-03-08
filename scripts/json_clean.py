
#clean the data
def json_clean(json_list_llm):
    json_return = []
    for i in json_list_llm:
        jsons = i.strip().replace('\n', '').replace('  ', '').strip('```json').strip('```') ##remove the json```` stuff````
        json_return.append(jsons)

    return json_return